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

from mtg_collection_tools.util.agent.work_with_existing_deck import (
        get_work_with_existing_deck_agent,
)
from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.models.mtg import Card, Deck


def stream_graph_updates(agent: Runnable, state: DeckBuilderState):
    for event in agent.stream(input=state):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

def run_deckbuilder_agent(config: MTGConfig, builder_mode: BuilderMode, deck_id: str | None) -> None:
    agent = None
    match builder_mode:
        case BuilderMode.WORK_WITH_EXISTING_DECK:
            agent = get_work_with_existing_deck_agent(config=config)
        case BuilderMode.BUILD_NEW_DECK:
            raise NotImplementedError()
        case BuilderMode.GET_CARD_SUGGESTIONS:
            raise NotImplementedError()

    state = DeckBuilderState(
        messages=[],
        builder_mode=builder_mode,
        deck=Deck(
            id=deck_id,
            provider=config.collection_provider
        ),
        collection_id=config.collection_id
    )

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        state.messages += user_input
        stream_graph_updates(agent=agent,state=state)
    



