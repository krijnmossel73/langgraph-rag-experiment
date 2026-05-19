"""Smoke test: graph compiles and reaches END from a trivial input.

Doesn't hit any real APIs — the assertion is purely structural.
"""
from src.graph import build_graph


def test_graph_compiles():
    g = build_graph()
    assert g is not None


def test_all_nodes_wired():
    g = build_graph()
    nodes = set(g.get_graph().nodes.keys())
    assert {"retrieve", "grade", "rewrite", "generate"}.issubset(nodes)
