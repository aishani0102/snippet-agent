"""
build_index.py
----------------
Builds (or rebuilds) the local Chroma vector database from knowledge_base.py.

Run this once before using agent.py or app.py:
    python build_index.py

It stores the index on disk in ./chroma_store so it persists between runs.
"""

import chromadb
from chromadb.utils import embedding_functions

from knowledge_base import KNOWLEDGE_BASE

CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "code_snippets"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # small, fast, runs locally (no API needed)


def build_index():
    print("Loading embedding model (first run downloads it, may take a minute)...")
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Drop any existing collection so re-running this script is idempotent
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Removed existing collection '{COLLECTION_NAME}'.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME, embedding_function=embed_fn
    )

    documents = [entry["text"] for entry in KNOWLEDGE_BASE]
    metadatas = [{"topic": entry["topic"]} for entry in KNOWLEDGE_BASE]
    ids = [str(i) for i in range(len(KNOWLEDGE_BASE))]

    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"Indexed {len(documents)} knowledge base entries into '{COLLECTION_NAME}'.")
    print(f"Vector store saved to: {CHROMA_PATH}")


if __name__ == "__main__":
    build_index()
