import pytest
from pydantic import ValidationError

from src.graph import build_graph
from src.models import Address, User


def test_user_ok():
    u = User(id=1, name="  Ada  ", email="ada@example.com", age=36)
    assert u.name == "Ada"
    assert u.role == "member"


def test_user_rejects_bad_email():
    with pytest.raises(ValidationError):
        User(id=1, name="Ada", email="not-an-email", age=36)


def test_admin_requires_address():
    with pytest.raises(ValidationError):
        User(id=2, name="Root", email="root@example.com", age=40, role="admin")

    ok = User(
        id=2, name="Root", email="root@example.com", age=40, role="admin",
        address=Address(street="1 Main St", city="Springfield", zip_code="12345"),
    )
    assert ok.address.city == "Springfield"


def test_graph_loops_to_limit():
    out = build_graph().invoke({"limit": 4})
    assert out["value"] == 4
    assert out["history"] == [1, 2, 3, 4]


def test_graph_checkpointer():
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, START, StateGraph
    from src.graph import CounterState, increment

    b = StateGraph(CounterState)
    b.add_node("increment", increment)
    b.add_edge(START, "increment")
    b.add_edge("increment", END)
    g = b.compile(checkpointer=InMemorySaver())

    cfg = {"configurable": {"thread_id": "t1"}}
    assert g.invoke({}, cfg)["value"] == 1
    assert g.invoke({}, cfg)["value"] == 2  # state persisted across runs
