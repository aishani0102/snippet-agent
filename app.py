import os
import streamlit as st
from rag_agent import CodeSnippetAgent
from build_index import build_index

st.set_page_config(page_title="Code Snippet Generator Agent", page_icon="🧩", layout="centered")

st.title("🧩 Code Snippet Generator Agent")
st.caption("Describe what you need in plain English. Ask follow-up questions to refine the code — RAG-grounded with Groq.")

# --- Ensure ChromaDB index exists on Cloud startup ---
if not os.path.exists("./chroma_store"):
    with st.spinner("Building vector index for the first time..."):
        build_index()

# --- Initialize agent + chat history once per session ---
if "agent" not in st.session_state:
    try:
        st.session_state.agent = CodeSnippetAgent()
        st.session_state.error = None
    except Exception as e:
        st.session_state.agent = None
        st.session_state.error = str(e)

if "display_history" not in st.session_state:
    st.session_state.display_history = []  # [(role, text), ...] for rendering

if st.session_state.error:
    st.error(st.session_state.error)
    st.info("Set GROQ_API_KEY in Streamlit Cloud Secrets or environment variables, then reload.")
    st.stop()

agent = st.session_state.agent

# --- Sidebar controls ---
with st.sidebar:
    st.header("Session")
    if st.button("🔄 Reset conversation"):
        agent.reset()
        st.session_state.display_history = []
        st.rerun()

    st.markdown("---")
    st.subheader("Last retrieved context")
    if agent.last_retrieved:
        for i, chunk in enumerate(agent.last_retrieved, 1):
            st.markdown(f"**{i}.** {chunk}")
    else:
        st.caption("No retrieval yet — ask something!")

# --- Render chat history ---
for role, text in st.session_state.display_history:
    with st.chat_message(role):
        st.markdown(text)

# --- Chat input ---
user_input = st.chat_input("e.g. 'write a function to merge two sorted lists'")

if user_input:
    st.session_state.display_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving context and generating..."):
            try:
                reply = agent.ask(user_input)
            except Exception as e:
                reply = f"⚠️ Error: {e}"
        st.markdown(reply)

    st.session_state.display_history.append(("assistant", reply))
    st.rerun()
