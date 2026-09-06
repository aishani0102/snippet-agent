import os
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "code_snippets"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 3

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


def get_active_llama_model(client: Groq) -> str:
    """Fetch available models from Groq and pick the best active text generation model."""
    try:
        # Exclude guardrails, audio, embeddings, and classifiers
        excluded_keywords = ["guard", "whisper", "embed", "classifier"]
        available_models = [
            m.id for m in client.models.list().data
            if not any(keyword in m.lower() for keyword in excluded_keywords)
        ]
        
        preferred_llama = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.2-3b-preview",
            "llama-3.2-1b-preview",
            "llama-3.1-70b-versatile",
        ]
        
        for model_id in preferred_llama:
            if model_id in available_models:
                return model_id

        # Fallback to any non-excluded model with 'llama' in its name
        llama_matches = [m for m in available_models if "llama" in m.lower()]
        if llama_matches:
            return llama_matches[0]

        return available_models[0] if available_models else "llama-3.1-8b-instant"
    except Exception:
        return "llama-3.1-8b-instant"


class CodeSnippetAgent:
    def __init__(self, api_key: str | None = None):
        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "No Groq API key found. Set GROQ_API_KEY as an environment variable or in Secrets."
            )

        self.llm_client = Groq(api_key=api_key)
        self.model = get_active_llama_model(self.llm_client)

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

        self.conversation: list[dict] = []
        self.last_retrieved: list[str] = []

    def retrieve_context(self, query: str, k: int = TOP_K) -> list[str]:
        """Fetch the top-k most relevant knowledge base chunks for this query."""
        results = self.collection.query(query_texts=[query], n_results=k)
        docs = results["documents"][0] if results["documents"] else []
        self.last_retrieved = docs
        return docs

    def ask(self, user_message: str) -> str:
        """Send user message to Groq using the detected active chat model."""
        context_chunks = self.retrieve_context(user_message)
        context_text = "\n\n".join(f"- {c}" for c in context_chunks) or "(no relevant matches found)"
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_text)

        self.conversation.append({"role": "user", "content": user_message})

        response = self.llm_client.chat.completions.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "system", "content": system_prompt}] + self.conversation,
        )

        reply_text = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": reply_text})
        return reply_text

    def reset(self):
        """Clear conversation history to start a fresh session."""
        self.conversation = []
        self.last_retrieved = []
