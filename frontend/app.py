import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import streamlit as st
from backend.config import UPLOAD_DIR
from backend.rag import index_file, find_relevant_chunks
from backend.llm import generate_answer
from backend import audit

st.set_page_config(page_title="DocuMind", page_icon="🧠", layout="wide")
st.title("🧠 DocuMind")
st.caption("Upload a document, ask a question, get an answer grounded in it — nothing made up.")

if "history" not in st.session_state: st.session_state.history = audit.get_all()

with st.sidebar:
    st.subheader("📄 Document")
    file = st.file_uploader("PDF or TXT", type=["pdf", "txt"], label_visibility="collapsed")
    if file and file.name != st.session_state.get("last_file"):
        path = os.path.join(UPLOAD_DIR, file.name)
        open(path, "wb").write(file.getbuffer())
        with st.spinner("Reading and indexing..."): n = index_file(path, file.name)
        st.session_state.last_file = file.name
        st.toast(f"Indexed **{file.name}** — {n} chunks ready", icon="✅")
    st.divider()
    st.metric("Questions asked", len(st.session_state.history))
    if st.session_state.history and st.button("🧹 Clear history"):
        audit.clear_all()
        st.session_state.history = []
        st.toast("History cleared", icon="🧹")
        st.rerun()

def render(question, answer, confidence, sources):
    with st.chat_message("user", avatar="🧑"): st.write(question)
    with st.chat_message("assistant", avatar="🤖"):
        st.write(answer)
        src = f" · Source: {', '.join(sources)}" if sources else ""
        st.caption(f"{'🟢' if confidence >= 50 else '🟠'} {confidence}% confidence{src}")

if not st.session_state.history:
    with st.chat_message("assistant", avatar="🤖"): st.write("👋 Hi! Upload a document on the left, then ask me anything about it.")

for e in st.session_state.history:
    render(e["question"], e["answer"], e["confidence"], e["sources_used"])

if question := st.chat_input("Ask something about your document..."):
    with st.spinner("Thinking..."):
        chunks, confidence = find_relevant_chunks(question)
        answer = generate_answer(question, chunks) if chunks else "No relevant document found. Please upload one first."
    st.session_state.history.append(entry := audit.save_entry(question, answer, chunks, confidence))
    render(question, answer, confidence, entry["sources_used"])
    _ = st.balloons() if len(st.session_state.history) == 1 else st.toast("Thanks for your question! 🙏", icon="💬")
