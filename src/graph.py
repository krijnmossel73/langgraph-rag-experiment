from langgraph.graph import END, StateGraph

from .nodes import generate, grade, retrieve, rewrite, should_continue
from .state import GraphState


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("retrieve", retrieve)
    builder.add_node("grade", grade)
    builder.add_node("rewrite", rewrite)
    builder.add_node("generate", generate)

    builder.set_entry_point("retrieve")
    builder.add_edge("retrieve", "grade")
    builder.add_conditional_edges(
        "grade",
        should_continue,
        {"generate": "generate", "rewrite": "rewrite"},
    )
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("generate", END)

    return builder.compile()


graph = build_graph()
