"""CLI entry point: ask a question."""
import sys

from dotenv import load_dotenv

from .graph import graph
from .state import GraphState

load_dotenv()


def main(question: str) -> None:
    initial: GraphState = {
        "question": question,
        "rewritten": question,
        "documents": [],
        "relevant": False,
        "rewrites": 0,
        "answer": "",
    }
    result = graph.invoke(initial)
    print("\n--- Answer ---\n")
    print(result["answer"])
    if result["rewrites"]:
        print(f"\n(Took {result['rewrites']} query rewrite(s).)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python -m src.run "<your question>"')
        sys.exit(1)
    main(" ".join(sys.argv[1:]))
