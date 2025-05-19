import uuid
from calendar import c
from enum import StrEnum, auto
from typing import Annotated

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from mtg_collection_tools.util.agent.work_with_existing_deck import (
    get_work_with_existing_deck_graph,
)
from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.models.mtg import Card, Deck
from mtg_collection_tools.util.providers import get_provider


def run_deckbuilder_agent(config: MTGConfig, builder_mode: BuilderMode) -> None:
    provider = get_provider(config=config)
    
    init_state = DeckBuilderState(
        messages=[HumanMessage(content="Initiate deck building request")],
        builder_mode=builder_mode,
        provider=provider
    )

    match builder_mode:
        case BuilderMode.WORK_WITH_EXISTING_DECK:
            graph = get_work_with_existing_deck_graph(config=config)

        case BuilderMode.BUILD_NEW_DECK:
            raise NotImplementedError()
        case BuilderMode.GET_CARD_SUGGESTIONS:
            raise NotImplementedError()

        
