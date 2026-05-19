"""Tiny eval harness — runs the graph against a JSONL dataset and scores with LangSmith."""
from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate

from src.graph import graph
from src.state import GraphState

load_dotenv()

DATASET_PATH = Path(__file__).parent / "dataset.jsonl"
DATASET_NAME = "langgraph-rag-experiment-eval"


def _target(inputs: dict) -> dict:
    initial: GraphState = {
        "question": inputs["question"],
        "rewritten": inputs["question"],
        "documents": [],
        "relevant": False,
        "rewrites": 0,
        "answer": "",
    }
    result = graph.invoke(initial)
    return {"answer": result["answer"], "rewrites": result["rewrites"]}


def _token_overlap(outputs: dict, reference_outputs: dict) -> dict:
    """Crude token-overlap scorer. Replace with an LLM judge for anything serious."""
    expected = reference_outputs["answer"].lower().split()
    actual = outputs["answer"].lower().split()
    if not expected:
        return {"key": "token_overlap", "score": 0.0}
    overlap = len(set(expected) & set(actual))
    return {"key": "token_overlap", "score": overlap / len(set(expected))}


def ensure_dataset(client: Client) -> None:
    if client.has_dataset(dataset_name=DATASET_NAME):
        return
    ds = client.create_dataset(dataset_name=DATASET_NAME)
    examples = [json.loads(line) for line in DATASET_PATH.read_text().splitlines() if line.strip()]
    client.create_examples(
        inputs=[{"question": ex["question"]} for ex in examples],
        outputs=[{"answer": ex["answer"]} for ex in examples],
        dataset_id=ds.id,
    )


def main() -> None:
    client = Client()
    ensure_dataset(client)
    evaluate(
        _target,
        data=DATASET_NAME,
        evaluators=[_token_overlap],
        experiment_prefix="crag",
    )


if __name__ == "__main__":
    main()
