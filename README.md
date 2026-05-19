# langgraph-rag-experiment

A small, opinionated experiment in building a **self-correcting RAG pipeline** with [LangGraph](https://github.com/langchain-ai/langgraph), [Qdrant](https://qdrant.tech/) as the vector store, and [LangSmith](https://smith.langchain.com/) for tracing and evaluation.

## What this is

Most RAG demos chain `retrieve → generate` and call it done. That falls over the moment retrieval misses. This experiment implements a **Corrective RAG** pattern (after the [CRAG paper](https://arxiv.org/abs/2401.15884)) as a LangGraph state machine:

1. **Retrieve** candidate documents from Qdrant
2. **Grade** each document's relevance to the question (LLM-as-judge)
3. **Conditionally branch**:
   - If documents are relevant → **Generate** with citations
   - If none are relevant → **Rewrite** the query and retry (bounded)
4. **Generate** a grounded answer, or fail explicitly if retrieval cannot recover

The interesting bits are the **conditional edges**, the **bounded retry loop**, and the **separation of retrieval grading from generation** — patterns that matter when this kind of system goes anywhere near production.

## Why I built this

I have a long enterprise-search background (Fredhopper, FAST/Microsoft, Autonomy/HP, Attivio) and most of what I learned there about recall/precision tradeoffs, query rewriting, and result quality maps directly onto vector retrieval — same problem, different index. I wanted a sandbox to think about retrieval grading and eval design in LangGraph specifically, rather than yet another notebook.

## Architecture

```
                ┌──────────┐
                │ retrieve │ ◄────────┐
                └────┬─────┘          │
                     ▼                │
                ┌──────────┐          │
                │  grade   │          │
                └────┬─────┘          │
              relevant?               │
                ├── yes               │
                ▼                     │
            ┌──────────┐        ┌─────┴─────┐
            │ generate │        │  rewrite  │
            └────┬─────┘        └───────────┘
                 ▼                   ▲
              ┌─────┐             retry?
              │ END │             (≤ N times)
              └─────┘
```

## Running it locally

Requirements: Python 3.11+, Docker, an OpenAI API key, optional LangSmith key.

```bash
# 1. Start Qdrant locally
docker compose up -d

# 2. Install deps
uv sync   # or: pip install -e .

# 3. Configure
cp .env.example .env
# edit .env

# 4. Ingest the sample corpus
python -m src.ingest

# 5. Ask something
python -m src.run "What is corrective RAG?"
```

## Evaluation

`evals/dataset.jsonl` contains a small set of question/answer pairs over the sample corpus. Run:

```bash
python -m evals.run_eval
```

This pushes the dataset to LangSmith and runs the graph against each example with a (deliberately crude) scorer. The eval is intentionally small — the point is the harness pattern, not the dataset.

## What's deliberately *not* here

- Production deployment scaffolding (the real version would use LangGraph Cloud or a containerised server)
- A real corpus — the sample data is a handful of markdown files
- Reranking — a real pipeline would add a cross-encoder reranker before grading
- Streaming — `astream_events` works fine with this graph, but the CLI here is sync for readability
- An LLM-judge scorer in the eval — the included scorer is token overlap so the eval runs without extra API spend; swap in an LLM judge for anything serious

## Notes

- State is a `TypedDict`, not a Pydantic model, to keep the diff readable
- Grader, rewriter, and generator have separate prompts in `src/prompts.py`
- Retry cap is `MAX_REWRITES = 2` — three retrieval attempts total per question

## License

MIT
