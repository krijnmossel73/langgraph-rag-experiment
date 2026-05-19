"""Individual graph nodes. Each takes a GraphState and returns a state delta."""
from __future__ import annotations

import os
from typing import List

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from .prompts import GENERATE_SYSTEM, GRADER_SYSTEM, REWRITE_SYSTEM
from .state import GraphState

MAX_REWRITES = 2
TOP_K = 4

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def _vectorstore() -> QdrantVectorStore:
    client = QdrantClient(url=os.environ["QDRANT_URL"])
    return QdrantVectorStore(
        client=client,
        collection_name=os.environ["QDRANT_COLLECTION"],
        embedding=_embeddings,
    )


def retrieve(state: GraphState) -> dict:
    query = state["rewritten"] or state["question"]
    docs: List[Document] = _vectorstore().similarity_search(query, k=TOP_K)
    return {"documents": [d.page_content for d in docs]}


def grade(state: GraphState) -> dict:
    """Grade each retrieved doc against the question. Keep only relevant ones."""
    kept: list[str] = []
    for doc in state["documents"]:
        verdict = _llm.invoke(
            [
                SystemMessage(content=GRADER_SYSTEM),
                HumanMessage(content=f"Question: {state['question']}\n\nDocument:\n{doc}"),
            ]
        ).content.strip().lower()
        if verdict.startswith("yes"):
            kept.append(doc)
    return {"documents": kept, "relevant": len(kept) > 0}


def rewrite(state: GraphState) -> dict:
    new_query = _llm.invoke(
        [
            SystemMessage(content=REWRITE_SYSTEM),
            HumanMessage(
                content=(
                    f"Original question: {state['question']}\n"
                    f"Previous query that failed: {state['rewritten'] or state['question']}"
                )
            ),
        ]
    ).content.strip()
    return {"rewritten": new_query, "rewrites": state["rewrites"] + 1}


def generate(state: GraphState) -> dict:
    if not state["documents"]:
        return {
            "answer": (
                "I could not retrieve any documents that would support an answer to "
                f"\"{state['question']}\". (Tried {state['rewrites']} rewrite(s).)"
            )
        }
    context = "\n\n".join(f"[{i + 1}] {d}" for i, d in enumerate(state["documents"]))
    response = _llm.invoke(
        [
            SystemMessage(content=GENERATE_SYSTEM),
            HumanMessage(content=f"Question: {state['question']}\n\nContext:\n{context}"),
        ]
    ).content
    return {"answer": response}


def should_continue(state: GraphState) -> str:
    """Conditional edge: where do we go after grading?"""
    if state["relevant"]:
        return "generate"
    if state["rewrites"] >= MAX_REWRITES:
        # Generate anyway — generator will return an explicit failure message
        return "generate"
    return "rewrite"
