from enum import StrEnum, auto
from typing import Callable, Literal

from langchain.chat_models.base import BaseChatModel
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage, FunctionMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from mtg_collection_tools.util.agent.tools import (
   get_deck_builder_tools,
   load_deck_from_provider,
)
from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig


class BuilderStep(StrEnum):
   LOAD_DECK = auto()
   ASK_PARAMETERS = auto()
   INITIAL_RECOMMENDATIONS = auto()
   REFINE_UPGRADES = auto()
   SAVE_DECK = auto()

def load_deck(state: DeckBuilderState) -> DeckBuilderState:
   # prompt the user what deck they want to load
   print(f"Which deck would you like to load from {state.provider.provider_name}?")
   deck_info = state.provider.list_decks()
   for i in range(len(deck_info)):
      print(f"\t{i}. {deck_info[i][1]}")

   while True:
      user_input = input("Enter deck number from above:")
      user_input_int = 0

      try:
         user_input_int = int(user_input) - 1
         if user_input_int not in range(len(deck_info)):
            raise ValueError()
         break
      except ValueError:
         print(f"Invalid option. Please enter [{1} - {len(deck_info) + 1}]")

   state.original_deck = state.provider.get_deck(deck_id=deck_info[user_input_int][0])
   state.messages.append(
      FunctionMessage(
         name="load_deck",
         content=(
               f"Loaded **{state.original_deck.name}** with commander **{state.original_deck.commander.name}** "
               f"({len(state.original_deck.cards)} cards).\n\n"
               "Let's gather a few preferences before suggesting changes."
         )
      )
   )
   return state

PRESET_QUESTIONS: list[tuple[str, str]] = [
   ("budget", "Do you have a per-card or total budget in USD? (e.g., 'single cards ≤$5', 'no budget')"),
   ("collection_weight",
   "How should I weigh cards you already own? (options: 'only use collection', "
   "'prefer collection but suggest others if clearly better', 'ignore collection')"),
   ("weaknesses",
   "Where does the deck feel weak right now? (e.g., protection, removal, mana curve, land drops)"),
   ("target_bracket", 
   "Do you have a target bracket that you'd like your deck to perform at? "
   " See here for more info: https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-april-22-2025")
   ("goals",
   "What new themes or synergies would you like to lean into?"),
]


def ask_parameters(state: DeckBuilderState) -> DeckBuilderState:
   for key, question in PRESET_QUESTIONS:
      user_input = input(question)
      state.builder_params[key] = user_input

   return state

def system_prompt():
    return """
You are **Commander Deck-Builder**, an expert Magic: The Gathering assistant focused on upgrading EDH (Commander) decks.

## Overall Goal
Help the user iteratively improve their existing Commander deck while respecting their card collection, budget, and competitive “bracket” goals.

## Workflow  (STRICTLY FOLLOW)state.original_deck = load_deck_from_provider(
      collection_provider=state.original_deck.provider,
      collection_id=state.collection_id,
      deck_id=state.original_deck.id
   )
1. **Load the current deck**  
   Use the tool `load_original_deck` to get the deck object already provided by the user

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
   Use the tool `set_altered_deck` to set the new deck state. This should be a copy of is returned by load_original_deck, except with the 
   llm-suggested cuts removed and the llm-suggested adds added.

## Style & Etiquette
* Be concise but data-rich; provide card links via scryfall format when referencing cards in the upgrade plan.
* Scryfall links should be in the format `https://scryfall.com/search?q=<card_name>&unique=cards&as=grid&order=name`. For example,
   `Sol Ring` would have a link to `https://scryfall.com/search?q=sol+ring&unique=cards&as=grid&order=name`
* Mention prices in USD (to two decimals) when discussing budget.  
* Never exceed the 100-card deck limit, and respect singleton rules (basic lands exempt).  
* If a user request conflicts with Commander legality or their stated bracket/budget, explain the conflict and propose alternatives.

## Safety
* Do not output copyrighted card text larger than 400 characters total in any single response.  
* Do not hallucinate real-world prices; if a price is unknown, say “n/a”.

Begin every new conversation by following **Step 1** above.
"""

def make_suggest_upgrades(llm: BaseChatModel) -> Callable[..., DeckBuilderState]:
   def suggest_upgrades(state: DeckBuilderState) -> DeckBuilderState:
      # Delegate heavy lifting to the bound LLM so it can call helper tools.
      messages = llm.invoke(system_prompt())
      state.messages.append(messages)

      return state
   
   return suggest_upgrades

def make_refine_upgrades(llm: BaseChatModel) -> Callable[..., DeckBuilderState]:
   def refine_upgrades(state: DeckBuilderState) -> DeckBuilderState:
      # Delegate heavy lifting to the bound LLM so it can call helper tools.
      messages = llm.invoke(state.messages)
      state.messages.append(messages)
      # Append follow-up choice question

      return state
   
   return refine_upgrades

def save_deck(state: DeckBuilderState) -> DeckBuilderState:
   url = state.provider.save_altered_deck(state.altered_deck)
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

def router(state: DeckBuilderState) -> str:
   match state.builder_step:
      case None:
         return BuilderStep.LOAD_DECK
      case BuilderStep.LOAD_DECK:
         return BuilderStep.INITIAL_RECOMMENDATIONS
      case BuilderStep.INITIAL_RECOMMENDATIONS | BuilderStep.REFINLE_UPGRADES:
         
         if state.builder_step == BuilderStep.INITIAL_RECOMMENDATIONS:
            print("How would you like to proceed?")
            print("\t* 's' or 'save' will save the deck to your provider")
            print("\t* 'q' or 'quit' will exit the deck builder without saving changes")
            print("\t* Any other responses will be used to refine the deck further")
         else:
            print("Would you like to refine further? (q - quit / s - save)")

         user_response = input("User:")

         match user_response.lower():
            case "q" | "quit":
               return END
            case "s"  | "save":
               return BuilderStep.SAVE_DECK
            case _:
               return BuilderStep.REFINE_UPGRADES
      case BuilderStep.SAVE_DECK:
         print("Would you like to refine further? (q - quit)")

         user_response = input("User:")

         match user_response.lower():
            case "q" | "quit":
               return END
            case _:
               return BuilderStep.REFINE_UPGRADES







def get_work_with_existing_deck_graph(config: MTGConfig) -> CompiledGraph:
   llm = ChatAnthropic(
      model_name="claude-3-5-sonnet-latest",
      api_key=config.anthropic_api_key,
   ).bind_tools(get_deck_builder_tools())

   builder = StateGraph(DeckBuilderState)

   builder.add_node(BuilderStep.LOAD_DECK, load_deck)
   builder.add_node(BuilderStep.ASK_PARAMETERS, ask_parameters)
   builder.add_node(BuilderStep.INITIAL_RECOMMENDATIONS, make_suggest_upgrades(llm=llm))
   builder.add_node(BuilderStep.REFINE_UPGRADES, make_refine_upgrades(llm=llm))
   builder.add_node(BuilderStep.SAVE_DECK, save_deck)

   builder.add_conditional_edges("router", router, {m.value: m.value for m in BuilderStep})

   builder.set_entry_point("router")

   return builder.compile(checkpointer=MemorySaver())
