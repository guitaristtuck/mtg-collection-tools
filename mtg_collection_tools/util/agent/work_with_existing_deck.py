from enum import StrEnum, auto
from typing import Callable, Literal

from langchain.chat_models.base import BaseChatModel
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import (
   AIMessage,
   FunctionMessage,
   HumanMessage,
   SystemMessage,
   ToolMessage,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from langgraph.types import interrupt

from mtg_collection_tools.util.agent.tools import (
   get_deck_builder_tools,
)
from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.providers import BaseProvider


class BuilderStep(StrEnum):
   LOAD_DECK = auto()
   ASK_PARAMETERS = auto()
   INITIAL_RECOMMENDATIONS = auto()
   REFINE_UPGRADES = auto()
   SAVE_DECK = auto()

def make_load_deck(provider: BaseProvider) -> Callable[..., DeckBuilderState]:
   def load_deck(state: DeckBuilderState) -> DeckBuilderState:
      # update the step
      state.builder_step = BuilderStep.LOAD_DECK
      # check if the user provided a deck_id already
      if state.original_deck and state.original_deck.id:
         state.messages.append(AIMessage(f"Loading provided deck id {state.original_deck.id} from {provider.provider_name}"))
         deck_id= str(state.original_deck.id)
      else:
         # prompt the user what deck they want to load
         prompt = f"Which deck would you like to load from {provider.provider_name}?"
         deck_info = provider.list_decks()
         for i in range(len(deck_info)):
            prompt += (f"\n\t{i + 1}. {deck_info[i][1]}")

         prompt += "\nEnter deck number from above:"

         while True:
            user_input = interrupt(prompt + "\n> ")
            user_input_int = 0

            try:
               user_input_int = int(user_input) - 1
               if user_input_int not in range(len(deck_info)):
                  raise ValueError()
               break
            except ValueError:
               prompt = f"Invalid option. Please enter [{1} - {len(deck_info)}]"

         deck_id= deck_info[user_input_int][0]

      state.original_deck = provider.get_deck(deck_id=deck_id)

      state.messages.append(
         AIMessage(
            name="load_deck",
            content=(
               f"Loaded **{state.original_deck.name}** with commander **{state.original_deck.commander.name}** "
               f"({len(state.original_deck.cards)} cards).\n\n"
               "Let's gather a few preferences before suggesting changes."
            )
         )
      )
      return state

   return load_deck

PRESET_QUESTIONS: list[tuple[str, str]] = [
   ("budget", "Do you have a per-card or total budget in USD? (e.g., 'single cards ≤$5', 'no budget')"),
   ("collection_weight",
   "How should I weigh cards you already own? (options: 'only use collection', "
   "'prefer collection but suggest others if clearly better', 'ignore collection')"),
   ("weaknesses",
   "Where does the deck feel weak right now? (e.g., protection, removal, mana curve, land drops)"),
   ("target_bracket", 
   "Do you have a target bracket that you'd like your deck to perform at? "
   " See here for more info: https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-april-22-2025"),
   ("goals",
   "What new themes or synergies would you like to lean into?"),
]


def ask_parameters(state: DeckBuilderState) -> DeckBuilderState:
   state.builder_step = BuilderStep.ASK_PARAMETERS
   for key, question in PRESET_QUESTIONS:
      user_input = interrupt(question + "\n> ")
      state.builder_params[key] = user_input

   return state

def system_prompt():
    return """
You are **Commander Deck-Builder**, an expert Magic: The Gathering assistant focused on upgrading EDH (Commander) decks.

## Overall Goal
Help the user iteratively improve their existing Commander deck while respecting their card collection, budget, and competitive "bracket" goals.

## Workflow (STRICTLY FOLLOW)
1. **Load the current deck**  
   Use the tool `load_original_deck` to get the deck object already provided by the user. Save this deck structure as you'll need to modify it.

2. **Load the deck building parameters**
   Use the tool `load_deck_builder_parameters` to get the parameters already provided by the user

3. **Confirm context back to the user**  
   - Summarize the current deck's commander, key themes, and statistics (land count, colour distribution, avg. mana value, price, etc.).  
   - Restate the deck building parameters to ensure alignment

4. **Generate upgrade plan**  
   - Produce ≤10 paired suggestions: **{cut → add}**.  
   - Honour the deck building parameters provided by the user
   - For each suggestion include a one-sentence rationale.  
   - Explain how the overall plan addresses the user's stated parameters.

5. **Set the altered deck in the conversation state**
   - Start with the deck structure returned by `load_original_deck`
   - Remove all cards that were in your "cuts" list
   - Add all cards that were in your "adds" list
   - Pass this modified deck structure to the `set_altered_deck` tool. The structure must be:
     ```
     {
         "id": str | None,
         "provider": str,
         "name": str | None,
         "cards": list[dict],  # Each card is a dictionary with card properties
         "commander": dict | None  # Commander card as a dictionary
     }
     ```

## Style & Etiquette
* Be concise but data-rich; provide card links via scryfall format when referencing cards in the upgrade plan.
* Scryfall links should be in the format `https://scryfall.com/search?q=<card_name>&unique=cards&as=grid&order=name`. For example,
   `Sol Ring` would have a link to `https://scryfall.com/search?q=sol+ring&unique=cards&as=grid&order=name`
* Mention prices in USD (to two decimals) when discussing budget.  
* Never exceed the 100-card deck limit, and respect singleton rules (basic lands exempt).  
* If a user request conflicts with Commander legality or their stated bracket/budget, explain the conflict and propose alternatives.

## Safety
* Do not output copyrighted card text larger than 400 characters total in any single response.  
* Do not hallucinate real-world prices; if a price is unknown, say "n/a".

Begin every new conversation by following **Step 1** above.
"""

def make_suggest_upgrades(llm: BaseChatModel) -> Callable[..., DeckBuilderState]:
   def suggest_upgrades(state: DeckBuilderState) -> DeckBuilderState:
      state.builder_step = BuilderStep.INITIAL_RECOMMENDATIONS
      
      # Create a message that includes all the context the LLM needs
      if not state.original_deck:
         raise ValueError("No deck loaded. Please load a deck first.")

      # Create a ReAct agent that can use the tools
      agent = create_react_agent(llm, get_deck_builder_tools())
      
      # Create the initial prompt for the agent
      context_message = (
         "You are helping upgrade a Commander deck. Here is the current context:\n\n"
         f"Deck: {state.original_deck.name or 'Unnamed Deck'}\n"
         f"Commander: {state.original_deck.commander.name if state.original_deck.commander else 'No Commander Set'}\n"
         "Current cards: " + ", ".join(card.name for card in (state.original_deck.cards or [])) + "\n\n"
         "User preferences:\n" +
         "\n".join(f"- {key}: {value}" for key, value in state.builder_params.items()) + "\n\n"
         "Please analyze the deck and suggest upgrades based on the user's preferences. "
         "First use the tools to get the full deck information, then analyze it and suggest specific card changes. "
         "Make sure to use the set_altered_deck tool to save your changes."
      )

      # Get the agent's response
      response = agent.invoke({
         "messages": [
            SystemMessage(content=system_prompt()),
            HumanMessage(content=context_message)
         ]
      })

      # Add the response to the state
      state.messages.append(response)

      return state
   
   return suggest_upgrades

def make_refine_upgrades(llm: BaseChatModel) -> Callable[..., DeckBuilderState]:
   def refine_upgrades(state: DeckBuilderState) -> DeckBuilderState:
      state.builder_step = BuilderStep.REFINE_UPGRADES
      # Delegate heavy lifting to the bound LLM so it can call helper tools.
      messages = llm.invoke(state.messages)
      state.messages.append(messages)
      # Append follow-up choice question

      return state
   
   return refine_upgrades

def make_save_deck(provider: BaseProvider) -> Callable[..., DeckBuilderState]:
   def save_deck(state: DeckBuilderState) -> DeckBuilderState:
      state.builder_step = BuilderStep.SAVE_DECK
      url = provider.save_altered_deck(state.altered_deck)
      state.messages.append(
         FunctionMessage(
            name="save_deck",
            content=(
                  f"Saved **{state.altered_deck.name}** with commander **{state.altered_deck.commander.name}** "
                  f"to {url}\n\n"
            )
         )
      )
      return state
   
   return save_deck

def router(state: DeckBuilderState) -> dict:
   match state.builder_step:
      case None:
         next_step = BuilderStep.LOAD_DECK
      case BuilderStep.LOAD_DECK:
         next_step = BuilderStep.ASK_PARAMETERS
      case BuilderStep.ASK_PARAMETERS:
         next_step = BuilderStep.INITIAL_RECOMMENDATIONS
      case BuilderStep.INITIAL_RECOMMENDATIONS | BuilderStep.REFINE_UPGRADES:
         
         if state.builder_step == BuilderStep.INITIAL_RECOMMENDATIONS:
            prompt = (
               "How would you like to proceed?"
               "\n\t- 's' or 'save' will save the deck to your provider"
               "\n\t- 'q' or 'quit' will exit the deck builder without saving changes"
               "\n\t- Any other responses will be used to refine the deck further"
            )
         else:
            prompt = "Would you like to refine further? (q - quit / s - save)"

         user_response = interrupt(prompt + "\n> ")

         match user_response.lower():
            case "q" | "quit":
               next_step = END
            case "s"  | "save":
               next_step = BuilderStep.SAVE_DECK
            case _:
               next_step = BuilderStep.REFINE_UPGRADES
      case BuilderStep.SAVE_DECK:
         prompt = "Would you like to refine further? (q - quit)"

         user_response = interrupt(prompt + "\n> ")

         match user_response.lower():
            case "q" | "quit":
               next_step = END
            case _:
               next_step = BuilderStep.REFINE_UPGRADES

   return {"builder_step": next_step}

def choose_path(state: DeckBuilderState) -> str:
   return state.builder_step


def get_work_with_existing_deck_graph(config: MTGConfig, provider: BaseProvider) -> CompiledGraph:
   llm = ChatAnthropic(
      model_name="claude-3-5-sonnet-latest",
      api_key=config.anthropic_api_key,
   ).bind_tools(get_deck_builder_tools())

   builder = StateGraph(DeckBuilderState)

   builder.add_node("router",router)
   builder.add_node(BuilderStep.LOAD_DECK, make_load_deck(provider=provider))
   builder.add_node(BuilderStep.ASK_PARAMETERS, ask_parameters)
   builder.add_node(BuilderStep.INITIAL_RECOMMENDATIONS, make_suggest_upgrades(llm=llm))
   builder.add_node(BuilderStep.REFINE_UPGRADES, make_refine_upgrades(llm=llm))
   builder.add_node(BuilderStep.SAVE_DECK, make_save_deck(provider=provider))

   for step in BuilderStep:
      builder.add_edge(step.value, "router")

   builder.add_conditional_edges("router", choose_path, {**{step.value: step.value for step in BuilderStep},**{END: END}})

   builder.set_entry_point("router")

   return builder.compile(checkpointer=MemorySaver())
