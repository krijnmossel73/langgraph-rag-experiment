# Evaluating RAG and agent systems

Evaluation for RAG splits into two questions: did retrieval find the right information, and did the generator use it correctly?

**Retrieval metrics.** Recall@k and precision@k over a labelled set of question-document pairs. Mean reciprocal rank when ranked position matters. These require a ground-truth set of relevant documents per query, which is the expensive part to build.

**Generation metrics.** Faithfulness measures whether the generated answer is supported by the retrieved context — typically scored by an LLM judge against the cited passages. Answer relevance measures whether the answer addresses the question, regardless of grounding. Both are noisy at the individual-example level and only useful in aggregate.

**End-to-end metrics.** Correctness against a reference answer, when one exists. Helpful for regression testing but rarely available for open-ended queries.

For agents, additional signals matter: tool-call success rate, step count, latency per turn, and cost per resolved task. LangSmith supports per-trace evaluators that can score any of these without changes to the agent code.

A practical rule: build the smallest eval set that catches the regressions you actually care about, and run it on every meaningful change.
