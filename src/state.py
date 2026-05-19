from typing import List, TypedDict


class GraphState(TypedDict):
    """State threaded through the corrective-RAG graph.

    Kept deliberately small — anything heavier belongs in storage, not state.
    """

    question: str          # original user question
    rewritten: str         # latest rewrite (== question on first pass)
    documents: List[str]   # retrieved document chunks for the current attempt
    relevant: bool         # whether the last grading pass found relevant docs
    rewrites: int          # how many rewrites have been attempted
    answer: str            # final answer, populated by `generate`
