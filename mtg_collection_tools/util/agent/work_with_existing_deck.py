import time
import uuid
from enum import StrEnum, auto
from typing import Callable, Literal

from langchain.chat_models.base import BaseChatModel
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
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
from pydantic import SecretStr

from mtg_collection_tools.util.agent.tools import (
    get_deck_builder_tools,
)
from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.models.mtg import Deck
from mtg_collection_tools.util.providers import BaseProvider


class BuilderStep(StrEnum):
    LOAD_DECK = auto()
    ASK_PARAMETERS = auto()
    SUGGEST_UPGRADES = auto()
    SAVE_DECK = auto()


def make_load_deck(provider: BaseProvider) -> Callable[..., DeckBuilderState]:
    def load_deck(state: DeckBuilderState) -> DeckBuilderState:
        # check if the user provided a deck_id already
        if state.original_deck and state.original_deck.id:
            state.messages.append(
                AIMessage(
                    f"Loading provided deck id {state.original_deck.id} from {provider.provider_name}"
                )
            )
            deck_id = str(state.original_deck.id)
        else:
            # prompt the user what deck they want to load
            prompt = f"Which deck would you like to load from {provider.provider_name}?"
            deck_info = provider.list_decks()
            for i in range(len(deck_info)):
                prompt += f"\n\t{i + 1}. {deck_info[i][1]}"

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

            deck_id = deck_info[user_input_int][0]

        state.original_deck = provider.get_deck(deck_id=deck_id)

        state.messages.append(
            AIMessage(
                name="load_deck",
                content=(
                    f"Loaded **{state.original_deck.name}** with commander **{state.original_deck.commander.name}**"
                    f"({sum(card.quantity for card in state.original_deck.cards)} cards).\n\n"
                    "Let's gather a few preferences before suggesting changes."
                ),
            )
        )
        return state

    return load_deck


PRESET_QUESTIONS: list[tuple[str, str]] = [
    (
        "budget",
        "Do you have a per-card or total budget in USD? (e.g., 'single cards ≤$5', 'no budget')",
    ),
    (
        "collection_weight",
        "How should I weigh cards you already own? (options: 'only use collection', "
        "'prefer collection but suggest others if clearly better', 'ignore collection')",
    ),
    (
        "weaknesses",
        "Where does the deck feel weak right now? (e.g., protection, removal, mana curve, land drops)",
    ),
    (
        "target_bracket",
        "Do you have a target bracket that you'd like your deck to perform at? "
        " See here for more info: https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-april-22-2025",
    ),
    ("goals", "What new themes or synergies would you like to lean into?"),
]


def ask_parameters(state: DeckBuilderState) -> DeckBuilderState:
    for key, question in PRESET_QUESTIONS:
        user_input = interrupt(question + "\n> ")
        state.builder_params[key] = user_input

    return state


def make_suggest_upgrades(llm: BaseChatModel) -> Callable[..., DeckBuilderState]:
    def build_prompt(
        state: DeckBuilderState,
    ) -> list[SystemMessage | HumanMessage | BaseMessage]:
        system_prompt = """
            You are **Commander Deck-Builder**, an expert Magic: The Gathering assistant focused on upgrading EDH (Commander) decks.

            ## Overall Goal
            Help the user iteratively improve their existing Commander deck while respecting their card collection, budget, and competitive "bracket" goals.

            ## Workflow (STRICTLY FOLLOW)
            The User will provide a current deck list to you in the form of a Pydandic model. The user will also provide a dictionary of preferences for the deckbuilding suggestions. 

            Based on this input, you should suggest a list of cards to add and remove from the deck. This should be done as a one-shot effort.
            You should use the tools provided to you to get the information you need to make the best suggestions, and then use the save_card_suggestions 
            tool to save the suggestions to the graph state. You should not call this tool more than once.

            # Tools
            You have access to the following tools:
            - save_card_suggestions: Save a list of card suggestions to the graph state. This should be called once, and should be the last thing you do.
    
            """

        return [
            SystemMessage(content=system_prompt),
            SystemMessage(content=f"Build Parameters: {state.builder_params}"),
            SystemMessage(content=f"Original Deck: {state.original_deck}"),
            SystemMessage(content=f"Previous Suggestions: {state.card_suggestions}"),
            *state.messages[-10:],
        ]

    def suggest_upgrades(state: DeckBuilderState) -> DeckBuilderState:
        # Create a message that includes all the context the LLM needs
        if not state.original_deck:
            raise ValueError("No deck loaded. Please load a deck first.")

        # Build a prompt to pass to the LLM
        prompt = build_prompt(state)
        # Get the agent's response
        response = llm.invoke(prompt)

        # Add the response to the state
        state.messages.append(response)

        return state

    return suggest_upgrades


def make_save_deck(provider: BaseProvider) -> Callable[..., DeckBuilderState]:
    def save_deck(state: DeckBuilderState) -> DeckBuilderState:
        # TODO: Implement this
        url = "http://placeholder.com"
        state.messages.append(
            FunctionMessage(
                name="save_deck",
                content=(f"Saved state to {url}"),
            )
        )
        return state

    return save_deck


def router(state: DeckBuilderState) -> dict:
    prompt = "Would you like to refine further? (q - quit / s - save)"

    user_response = interrupt(prompt + "\n> ")

    match user_response.lower():
        case "q" | "quit":
            next_step = END
        case "s" | "save":
            next_step = BuilderStep.SAVE_DECK
        case _:
            next_step = BuilderStep.SUGGEST_UPGRADES

    return {"next_step": next_step}


def get_work_with_existing_deck_graph(
    config: MTGConfig, provider: BaseProvider
) -> CompiledGraph:
    llm = ChatAnthropic(
        model_name="claude-3-5-haiku-latest",
        api_key=config.anthropic_api_key,
    ).bind_tools(
        get_deck_builder_tools(
            builder_mode=BuilderMode.WORK_WITH_EXISTING_DECK, provider=provider
        )
    )

    builder = StateGraph(DeckBuilderState)

    # Add nodes
    builder.add_node(BuilderStep.LOAD_DECK, make_load_deck(provider=provider))
    builder.add_node(BuilderStep.ASK_PARAMETERS, ask_parameters)
    builder.add_node(BuilderStep.SUGGEST_UPGRADES, make_suggest_upgrades(llm=llm))
    builder.add_node("router", router)
    builder.add_node(BuilderStep.SAVE_DECK, make_save_deck(provider=provider))

    # Add node relationships
    builder.set_entry_point(BuilderStep.LOAD_DECK)
    builder.add_edge(BuilderStep.LOAD_DECK, BuilderStep.ASK_PARAMETERS)
    builder.add_edge(BuilderStep.ASK_PARAMETERS, BuilderStep.SUGGEST_UPGRADES)
    builder.add_edge(BuilderStep.SUGGEST_UPGRADES, "router")
    builder.add_edge(BuilderStep.SAVE_DECK, "router")

    builder.add_conditional_edges(
        "router",
        router,
        {
            BuilderStep.SUGGEST_UPGRADES: BuilderStep.SUGGEST_UPGRADES,
            BuilderStep.SAVE_DECK: BuilderStep.SAVE_DECK,
            END: END,
        },
    )

    return builder.compile(checkpointer=MemorySaver())
