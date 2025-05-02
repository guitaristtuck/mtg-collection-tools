from calendar import c
from enum import StrEnum, auto
from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.models.mtg import Card, Deck


def stream_graph_updates(user_input: str, graph: StateGraph) -> None:
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

def prompt_builder_mode(_: State) -> str:
    return """
    Started deck builder agent. What would you like to do?

    1. Work with an existing deck
    2. Build a new deck
    3. Get generalized card suggestions
    """

def set_builder_mode(state: State) -> str:
    user_input = state["messages"][-1].content
    if user_input == "1":
        return BuilderMode.WORK_WITH_EXISTING_DECK
    elif user_input == "2":
        return BuilderMode.BUILD_NEW_DECK
    elif user_input == "3":
        return BuilderMode.GET_CARD_SUGGESTIONS
    else:
        return BuilderMode.INVALID_MODE


def run_deckbuilder_agent(config: MTGConfig) -> None:
    llm = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        api_key=config.anthropic_api_key,
    )
    graph_builder = StateGraph(State)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    graph_builder.add_node("prompt_builder_mode", prompt_builder_mode)
    graph_builder.add_node("set_builder_mode", set_builder_mode)
    graph_builder.add_node("chatbot", chatbot)

    graph_builder.add_edge(START, "set_builder_mode")
    graph_builder.add_edge("chatbot", END)

    graph = graph_builder.compile()

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input, graph)
        except:
            # fallback if input() is not available
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input, graph)
            break



