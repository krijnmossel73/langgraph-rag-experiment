"""One-shot ingestion of the sample corpus into Qdrant."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data" / "sample_docs"
COLLECTION = os.environ["QDRANT_COLLECTION"]


def main() -> None:
    client = QdrantClient(url=os.environ["QDRANT_URL"])

    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

    docs: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        docs.append(Document(page_content=path.read_text(), metadata={"source": path.name}))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    )
    store.add_documents(chunks)
    print(f"Ingested {len(chunks)} chunks from {len(docs)} documents into '{COLLECTION}'.")


if __name__ == "__main__":
    main()
