from typing import cast

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from langchain.schema.runnable.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

import chainlit as cl

async def agent_node(state: MessagesState):
    model = cast(ChatOpenAI, cl.user_session.get("model"))
    messages = state["messages"]
    print(messages)
    response = await model.ainvoke(messages)
    print(response)
    return {
        "messages": [response]
    }

@cl.on_chat_start
async def on_chat_start():
    model = init_chat_model("openai:gpt-4o-mini")
    cl.user_session.set("model", model)

    builder = StateGraph(MessagesState)
    builder.add_node("agent", agent_node)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    checkpointer = InMemorySaver() 
    graph = builder.compile(checkpointer=checkpointer)
    cl.user_session.set("graph", graph)

@cl.on_message
async def on_message(message: cl.Message):
    config = {"configurable": {"thread_id": message.thread_id}}
    graph = cast(CompiledStateGraph, cl.user_session.get("graph"))
    final_answer = cl.Message(content="")
    async for msg, metadata in graph.astream({"messages": [HumanMessage(content=message.content)]}, stream_mode="messages", config=RunnableConfig(callbacks=[], **config)):
        if (msg.content
            and not isinstance(msg, HumanMessage)
            and not isinstance(msg, SystemMessage)
        ):
            await final_answer.stream_token(msg.content)
    await final_answer.send()
