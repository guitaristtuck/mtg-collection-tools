from calendar import c
from enum import StrEnum, auto
from typing import Annotated

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from mtg_collection_tools.util.agent.tools import DECK_BUILDER_TOOLS
from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.models.mtg import Card, Deck


def stream_graph_updates(user_input: str, graph: StateGraph) -> None:
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

def ask_builder_mode(state: DeckBuilderState) -> DeckBuilderState:
    while True:
        user_input = input("""
        Started deck builder agent. What would you like to do?

        1. Work with an existing deck
        2. Build a new deck
        3. Get generalized card suggestions
        """)
        if user_input == "1":
            state.builder_mode = BuilderMode.WORK_WITH_EXISTING_DECK
            return state
        elif user_input == "2":
            state.builder_mode = BuilderMode.BUILD_NEW_DECK
            return state
        elif user_input == "3":
            state.builder_mode = BuilderMode.GET_CARD_SUGGESTIONS
            return state
        else:
            print(f"Unrecongnized input '{user_input}'. Please pick a valid option 1-3.")

def route_builder_mode(state: DeckBuilderState) -> str:
    return state.builder_mode


def run_deckbuilder_agent(config: MTGConfig) -> None:
    graph_builder = StateGraph(DeckBuilderState)

    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        api_key=config.anthropic_api_key,
    ).bind_tools(DECK_BUILDER_TOOLS)

    llm.

    def stream_graph_updates(user_input: str, graph: Runnable):
        for event in graph.stream(DeckBuilderState(messages=[{"role": "user", "content": user_input}])):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)

    def work_with_existing_deck(state: DeckBuilderState):
        state.messages = [llm.invoke(state.messages)]
        return state


    graph_builder.add_node("ask_builder_mode", ask_builder_mode)
    graph_builder.add_conditional_edges(
        "ask_builder_mode", route_builder_mode, {
            #BuilderMode.BUILD_NEW_DECK: BuilderMode.BUILD_NEW_DECK,
            BuilderMode.WORK_WITH_EXISTING_DECK: BuilderMode.WORK_WITH_EXISTING_DECK,
            #BuilderMode.GET_CARD_SUGGESTIONS: BuilderMode.GET_CARD_SUGGESTIONS
        }
    )
    #graph_builder.add_node(BuilderMode.BUILD_NEW_DECK, build_new_deck)
    graph_builder.add_node(BuilderMode.WORK_WITH_EXISTING_DECK, work_with_existing_deck)
    #graph_builder.add_node(BuilderMode.GET_CARD_SUGGESTIONS, get_card_suggestions)

    graph_builder.add_edge(START, "ask_builder_mode")
    #graph_builder.add_edge(BuilderMode.BUILD_NEW_DECK, END)
    graph_builder.add_edge(BuilderMode.WORK_WITH_EXISTING_DECK, END)
    #graph_builder.add_edge(BuilderMode.GET_CARD_SUGGESTIONS, END)

    graph = graph_builder.compile()

    for event in graph.stream(DeckBuilderState(messages=[{"role": "user", "content": ""}])):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input, graph)



