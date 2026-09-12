"""A minimal LangGraph with a Pydantic state schema and a conditional edge.

No LLM / API key required - good for practicing graph mechanics.
"""
from typing import Literal

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


class CounterState(BaseModel):
    value: int = 0
    limit: int = 5
    history: list[int] = Field(default_factory=list)


def increment(state: CounterState) -> dict:
    new = state.value + 1
    return {"value": new, "history": state.history + [new]}


def should_continue(state: CounterState) -> Literal["increment", "__end__"]:
    return "increment" if state.value < state.limit else END


def build_graph():
    builder = StateGraph(CounterState)
    builder.add_node("increment", increment)
    builder.add_edge(START, "increment")
    builder.add_conditional_edges("increment", should_continue)
    return builder.compile()


if __name__ == "__main__":
    result = build_graph().invoke({"limit": 5})
    print(result)
