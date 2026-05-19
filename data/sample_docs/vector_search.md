# Vector search basics

Vector search retrieves documents based on semantic similarity in an embedding space, rather than lexical overlap. A document is embedded into a fixed-dimensional vector at ingestion time. At query time the user's question is embedded with the same model and compared against stored vectors using a distance metric, typically cosine similarity or dot product.

**Index types.** Brute-force search is exact but linear in collection size. Approximate nearest neighbour (ANN) indices — HNSW, IVF, ScaNN — trade a small recall loss for sub-linear query time. HNSW (Hierarchical Navigable Small World) is the default in most current vector databases.

**Hybrid retrieval.** Pure vector search loses to lexical search (BM25) on queries with rare named entities, exact identifiers, or domain jargon the embedding model has not seen. Hybrid retrieval combines both, usually by interpolating scores with a tunable weight or by reciprocal rank fusion.

**Chunking.** Documents are split before embedding because most embedding models have small context windows and because retrieval at sub-document granularity is more precise. Chunk size and overlap are the two main knobs: smaller chunks improve precision but lose context; overlap mitigates information being split across chunk boundaries.

**Filtering.** Most vector databases support attaching metadata to each vector and filtering on it at query time. This is essential for multi-tenant systems and any setup where access control intersects with retrieval.
