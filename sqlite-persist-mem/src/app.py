from typing import cast
import json
import sqlite3

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from langchain.schema.runnable.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
import chainlit.data as cl_data
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
import chainlit as cl

def message_converter(history: list[dict]) -> list:
    """Convert OpenAI style dict to LangChain Message Object"""
    role_map = {
        "user": HumanMessage,
        "assistant": AIMessage,
        "system": SystemMessage,
    }
    messages = []
    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        msg_cls = role_map.get(role)
        if not msg_cls:
            # Fallback to HumanMessage if no match
            msg_cls = HumanMessage
        messages.append(msg_cls(content=content))
    return messages


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("alice", "alice"):
        return cl.User(
            identifier="alice", metadata={"role": "admin", "provider": "credentials"}
        )
    elif (username, password) == ("bob", "bob"):
        return cl.User(
            identifier="bob", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

model = init_chat_model("openai:gpt-4o-mini")

async def agent_node(state: MessagesState):
    messages = state["messages"]
    response = await model.ainvoke(messages)
    return {
        "messages": [response]
    }

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)
checkpointer = InMemorySaver() 
graph = builder.compile(checkpointer=checkpointer)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", [])

    cl_data._data_layer = SQLAlchemyDataLayer(
        conninfo=f"sqlite+aiosqlite:///./sqlite/chainlit.db",
    )

@cl.on_message
async def on_message(message: cl.Message):
    chat_history = cl.user_session.get("chat_history")
    chat_history.append({"role": "user", "content": message.content})

    config = {"configurable": {"thread_id": message.thread_id}}
    final_answer = cl.Message(content="")
    async for msg, metadata in graph.astream({"messages": [HumanMessage(content=message.content)]}, stream_mode="messages", config=RunnableConfig(callbacks=[], **config)):
        if (msg.content
            and not isinstance(msg, HumanMessage)
            and not isinstance(msg, SystemMessage)
        ):
            await final_answer.stream_token(msg.content)
    await final_answer.send()

@cl.on_chat_resume
async def on_chat_resume(thread):
    cl.user_session.set("chat_history", [])

    if thread.get("metadata") is not None:
        metadata = thread["metadata"]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        if metadata.get("chat_history") is not None:
            state_messages = []
            chat_history = metadata["chat_history"]
            state_messages = message_converter(chat_history)
            thread_id = thread["id"]
            config = {"configurable": {"thread_id": thread_id}}
            state = graph.get_state(config).values
            if "messages" not in state:
                state["messages"] = state_messages
                graph.update_state(config, state)
