# Corrective RAG

Corrective RAG (CRAG) is a retrieval-augmented generation pattern that adds a grading step between retrieval and generation. The grader inspects each retrieved document and decides whether it is relevant to the user question. If retrieval is judged insufficient, the system rewrites the query and retries, or falls back to a different knowledge source.

The motivation is that naive RAG generates an answer whether or not retrieval succeeded, which leads to confident hallucination when the index does not contain the needed information.

Typical components of a CRAG pipeline:

- A vector retriever (dense, sparse, or hybrid)
- A lightweight grader, often an LLM-as-judge returning a binary relevance label per document
- A query rewriter that produces an alternative formulation when grading fails
- A bounded retry policy, since unbounded rewriting can loop indefinitely
- A generator that grounds its answer in the surviving documents and abstains when none remain

CRAG is well-suited to LangGraph because the control flow is genuinely a graph with conditional edges, not a linear chain. A typical bound for rewrites is two attempts, giving three retrieval passes per question before falling back.
