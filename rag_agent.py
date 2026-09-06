"""
rag_agent.py
-------------
Core logic for the RAG-powered code snippet generator agent.

Responsibilities:
  1. Retrieve relevant knowledge base chunks for a user query (RAG retrieval).
  2. Build a system prompt that injects that context.
  3. Call the Claude API with the running conversation history so the user
     can iteratively refine the generated code ("now make it async", etc.).

Import `CodeSnippetAgent` from this module in either the CLI (main.py)
or the Streamlit app (app.py).
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # reads GROQ_API_KEY from a local .env file if present

CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "code_snippets"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
TOP_K = 3  # how many knowledge base chunks to retrieve per query

SYSTEM_PROMPT_TEMPLATE = """You are an expert Python coding assistant embedded in a \
developer tool called the "Code Snippet Generator Agent".

Your job:
- Interpret the developer's natural language request.
- Generate a correct, idiomatic, PEP 8-compliant Python code snippet.
- Follow up with a short (2-4 sentence) plain-English explanation of how it works.
- If the user asks a follow-up ("make it recursive", "add error handling", "add type hints"), \
revise the PREVIOUS code accordingly rather than starting over, unless they ask for something new.
- Always put code inside a single fenced ```python code block.
- If the request is ambiguous, make a reasonable assumption, state it briefly, and proceed \
(don't just ask a clarifying question and stop).

You have access to the following reference material retrieved from a curated knowledge base. \
Use it if relevant to ground your answer in correct, up-to-date patterns. If it isn't relevant \
to this specific request, ignore it and rely on your own knowledge instead.

--- RETRIEVED REFERENCE MATERIAL ---
{context}
--- END REFERENCE MATERIAL ---
"""


class CodeSnippetAgent:
    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "No Groq API key found. Set GROQ_API_KEY as an environment "
                "variable or in a .env file (see .env.example)."
            )

        self.llm_client = Groq(api_key=api_key)

        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            self.collection = chroma_client.get_collection(
                COLLECTION_NAME, embedding_function=embed_fn
            )
        except Exception as e:
            raise RuntimeError(
                "Vector index not found. Run `python build_index.py` first."
            ) from e

        self.conversation: list[dict] = []  # running chat history for refinement
        self.last_retrieved: list[str] = []  # for transparency/debugging in UI

    def retrieve_context(self, query: str, k: int = TOP_K) -> list[str]:
        """Fetch the top-k most relevant knowledge base chunks for this query."""
        results = self.collection.query(query_texts=[query], n_results=k)
        docs = results["documents"][0] if results["documents"] else []
        self.last_retrieved = docs
        return docs

    def ask(self, user_message: str) -> str:
        """Send a user message (with retrieved context) to Claude and return the reply.
        Maintains conversation history internally so follow-up requests work."""
        context_chunks = self.retrieve_context(user_message)
        context_text = "\n\n".join(f"- {c}" for c in context_chunks) or "(no relevant matches found)"
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_text)

        self.conversation.append({"role": "user", "content": user_message})

        response = self.llm_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=1500,
            messages=[{"role": "system", "content": system_prompt}] + self.conversation,
        )

        reply_text = response.choices[0].message.content

        self.conversation.append({"role": "assistant", "content": reply_text})
        return reply_text

    def reset(self):
        """Clear conversation history to start a fresh session."""
        self.conversation = []
        self.last_retrieved = []
