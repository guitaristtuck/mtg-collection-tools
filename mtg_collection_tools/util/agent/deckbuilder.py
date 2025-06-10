import json
import uuid
from calendar import c
from enum import StrEnum, auto
from typing import Annotated, Generator, Literal, cast

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, StreamMode
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from mtg_collection_tools.util.agent.work_with_existing_deck import (
    get_work_with_existing_deck_graph,
)
from mtg_collection_tools.util.models.agent import BuilderMode, DeckBuilderState
from mtg_collection_tools.util.models.config import MTGConfig
from mtg_collection_tools.util.models.mtg import Card, Deck
from mtg_collection_tools.util.providers import get_provider


def run_deckbuilder_agent(
    config: MTGConfig, builder_mode: BuilderMode, deck_id: str | None
) -> DeckBuilderState:
    provider = get_provider(config=config)

    # Initialize the state. Set the deck ID if it is passed
    init_state = DeckBuilderState(
        messages=[HumanMessage(content="Initiate deck building request")],
        builder_mode=builder_mode,
        original_deck=Deck(id=deck_id) if deck_id else None,
    )

    match builder_mode:
        case BuilderMode.WORK_WITH_EXISTING_DECK:
            graph = get_work_with_existing_deck_graph(config=config, provider=provider)
        case BuilderMode.BUILD_NEW_DECK:
            raise NotImplementedError()
        case BuilderMode.GET_CARD_SUGGESTIONS:
            raise NotImplementedError()

    graph_config: RunnableConfig = {
        "configurable": {
            "thread_id": f"deck_builder_{provider.provider_name}_{uuid.uuid4().hex}"
        },
    }

    # Keep track of the current state
    new_command = init_state

    while new_command:
        # Stream the graph execution
        print("→ sending to graph:", new_command)
        for event in graph.stream(new_command, config=graph_config, debug=True):
            # print("====> new event")
            new_command = None
            # Handle each event from the graph
            for step_name, step_output in event.items():
                # print(step_name + ": " + str(step_output))
                match step_name:
                    case "agent":
                        if step_output.get("messages"):
                            for message in step_output["messages"]:
                                if isinstance(message.content, str):
                                    print(f"🤖: {message.content}")
                                else:
                                    for entry in message.content:
                                        print(f"🤖: {entry.get('text')}")
                    case "tools":
                        if step_output.get("messages"):
                            for message in step_output["messages"]:
                                if message.name != "prompt_user":
                                    print(f"🔧({message.name})")
                    case "__interrupt__":
                        new_command = Command(
                            resume=input(step_output[-1].value).strip()
                        )
