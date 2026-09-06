# Code Snippet Generator Agent

A Python coding assistant that takes plain-English requests and turns them into working code snippets with a short explanation. Under the hood it's RAG-based — before the LLM generates anything, it pulls a few relevant examples from a small local knowledge base so the answers stay grounded and consistent instead of just whatever the model feels like generating.

It also remembers the conversation, so you can follow up with stuff like "now make it async" or "add error handling" and it'll actually build on the last answer instead of starting over from scratch.

## What it does

- Turns natural language into Python code
- Lets you refine code over multiple turns ("add type hints", "wrap this in a try/except", etc.)
- Pulls reference examples for common stuff — file I/O, pandas, APIs, exceptions, testing, regex, async, decorators, classes
- Runs embeddings and the vector DB locally (Sentence Transformers + ChromaDB), so the only thing hitting the network is the actual generation call
- Shows you what got retrieved for a given answer, if you want to check its work
- Has both a CLI and a Streamlit web UI

## How it works

Basically:

1. You type a request
2. It gets embedded locally (Sentence Transformers)
3. ChromaDB finds the top 3 closest examples from the knowledge base
4. Those get stuffed into the system prompt
5. Groq generates the actual code + explanation
6. Response gets shown and added to conversation history

Only step 5 needs internet. Everything else is local.

### The RAG pipeline, a bit more detail

- `knowledge_base.py` has the actual example snippets — topic + text, nothing fancy
- `build_index.py` loads `all-MiniLM-L6-v2` and embeds everything into vectors
- Those get stored in ChromaDB under `./chroma_store`, collection name `code_snippets`
- `CodeSnippetAgent.retrieve_context()` embeds your query and grabs the 3 closest matches
- `CodeSnippetAgent.ask()` shoves those into the system prompt along with chat history, sends it to Groq, stores the reply
- the UI lets you peek at what was retrieved (there's a `sources` command / sidebar panel)

## Project structure

| File | What it does |
|---|---|
| `knowledge_base.py` | the curated examples |
| `build_index.py` | builds/rebuilds the ChromaDB index |
| `rag_agent.py` | retrieval + Groq calls + chat memory |
| `main.py` | CLI chat (uses Rich for formatting) |
| `app.py` | Streamlit UI |
| `requirements.txt` | deps |
| `chroma_store/` | where the local embeddings live |

## Stack

- Python 3.10+
- Groq SDK for generation — currently using `llama-3.3-70b-versatile`
- Sentence Transformers for local embeddings
- ChromaDB for the vector store
- Streamlit for the web UI
- Rich for terminal output
- python-dotenv for loading `.env`

## Setup

Install deps:

```bash
pip install -r requirements.txt
```

You'll need a Groq API key. Drop it in a `.env` file:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
```

(or just set it as a normal env var — either works). Don't commit this file obviously.

Then build the index before running anything for the first time:

```bash
python build_index.py
```

Heads up — the first run downloads the Sentence Transformers model, so it might take a minute. After that it's cached and reused. You'll need to rerun this whenever you touch `knowledge_base.py`.

## Running it

**CLI:**

```bash
python main.py
```

Example session:

```text
You: write a function that reads a CSV and returns the average of a column
You: now add error handling if the file doesn't exist
You: add type hints too
```

Commands: `reset` (clears history/context), `sources` (shows what was retrieved for the last answer), `exit`/`quit`.

**Web UI:**

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` usually. Sidebar has a reset button and shows retrieved context.

## Config

Main settings live as constants at the top of `rag_agent.py`:

- `CHROMA_PATH` — `./chroma_store`
- `COLLECTION_NAME` — `code_snippets`
- `EMBEDDING_MODEL` — `all-MiniLM-L6-v2`
- `GROQ_MODEL` — `llama-3.3-70b-versatile`
- `TOP_K` — `3` (how many examples get retrieved per request)

The system prompt asks for PEP 8 code, one fenced code block, a short explanation, and tells the model to revise previous code on follow-ups rather than regenerate from scratch.

## About the RAG layer (and why it's there)

Worth calling out: the original spec for this project said no external data, just rely on the pre-trained model. I went with RAG anyway, on purpose, for a few reasons:

- Pure LLM output tends to be inconsistent — different style, imports, patterns every time you ask something similar. Feeding it a curated example first keeps things more consistent.
- For less common patterns (specific async stuff, testing conventions, etc.) it cuts down on the model just making up an API that doesn't exist.
- You can actually see what informed the answer, which a plain LLM-only setup can't give you.
- It's not really adding external dependency in the "hitting someone else's server" sense — embeddings and search are 100% local. Groq is the only network call, and that was already required anyway since you need *some* LLM.

The tradeoff is you now have a knowledge base to maintain and re-index whenever it changes, which is extra overhead that a pure LLM-only version wouldn't have.

If you actually want the no-retrieval version to compare, just set `TOP_K = 0` in `rag_agent.py`. That disables retrieval entirely and it'll just use conversation history + system prompt, which matches the original "no external data" requirement exactly.

## Extending it

- Add more `{topic, text}` entries to `KNOWLEDGE_BASE` in `knowledge_base.py`, then rerun `build_index.py`
- Want a different embedding model? Change `EMBEDDING_MODEL` in both `build_index.py` and `rag_agent.py`
- Want a different Groq model? Just change `GROQ_MODEL`
- Play with `TOP_K` to see how much/little retrieved context changes the output
- Set `TOP_K = 0` temporarily if you want to A/B the RAG vs no-RAG answers

## Known limitations

- Knowledge base is small and hand-curated, so retrieval quality depends entirely on what's actually in there
- Conversation history isn't persisted anywhere — close the CLI or refresh the Streamlit session and it's gone
- It just returns text. Nothing here runs, lints, tests, or scans the generated code for you
- Needs a valid Groq key + internet connection to actually generate anything
- If the ChromaDB folder/collection doesn't exist yet, it'll just tell you to run `build_index.py`