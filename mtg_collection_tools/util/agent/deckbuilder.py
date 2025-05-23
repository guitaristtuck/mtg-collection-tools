import json
import uuid
from calendar import c
from enum import StrEnum, auto
from typing import Annotated, cast

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


def run_deckbuilder_agent(config: MTGConfig, builder_mode: BuilderMode, deck_id: str | None) -> DeckBuilderState:
    provider = get_provider(config=config)
    
    # Initialize the state. Set the deck ID if it is passed
    init_state = DeckBuilderState(
        messages=[HumanMessage(content="Initiate deck building request")],
        builder_mode=builder_mode,
        original_deck=Deck(
            id=deck_id
        ) if deck_id else None
    )

    match builder_mode:
        case BuilderMode.WORK_WITH_EXISTING_DECK:
            graph = get_work_with_existing_deck_graph(config=config,provider=provider)
        case BuilderMode.BUILD_NEW_DECK:
            raise NotImplementedError()
        case BuilderMode.GET_CARD_SUGGESTIONS:
            raise NotImplementedError()

    graph_config: RunnableConfig = {
        "configurable": {
            "thread_id": f"mtg-deckbuilder-{uuid.uuid4().hex}"
        }
    }

    state = init_state
    resuming = True

    while resuming:
        for event in graph.stream(
            input=state,
            config=graph_config,
            stream_mode=["messages", "updates", "debug"],
            subgraphs=True
        ):
            if isinstance(event, tuple):
                # Handle the case where event is (namespace, mode, data)
                if len(event) == 3:
                    namespace, mode, data = event
                # Handle the case where event is (mode, data)
                else:
                    mode, data = event

                if mode == "messages":
                    msg, metadata = data
                    if hasattr(msg, "content") and msg.content:
                        print(msg.content, end="", flush=True)
                elif mode == "updates":
                    if isinstance(data, dict):
                        # Print tool errors if present
                        if "error" in data:
                            print("\n[Tool Error]:", data["error"], flush=True)
                        # Handle interrupts
                        if "__interrupt__" in data:
                            print("\n")
                            user_response = input(data["__interrupt__"][-1].value)
                            state = Command(resume=user_response)
                            resuming = True
                            break
                elif mode == "debug":
                    # Print debug information about tool usage and state changes
                    if isinstance(data, dict):
                        if "node" in data:
                            print(f"\n[Debug] Node: {data['node']}", flush=True)
                        if "tool_input" in data:
                            print(f"[Debug] Tool Input: {data['tool_input']}", flush=True)
                        if "tool_output" in data:
                            print(f"[Debug] Tool Output: {data['tool_output']}", flush=True)
            else:
                # Handle non-tuple events (backwards compatibility)
                if isinstance(event, dict):
                    if "error" in event:
                        print("\n[Tool Error]:", event["error"], flush=True)
                    if "__interrupt__" in event:
                        print("\n")
                        user_response = input(event["__interrupt__"][-1].value)
                        state = Command(resume=user_response)
                        resuming = True
                        break
        else:
            resuming = False

    final_state = graph.get_state(graph_config)
    if hasattr(final_state, "values"):
        final_state = final_state.values
    
    print("\nProcess completed successfully!")
    return cast(DeckBuilderState, final_state)






