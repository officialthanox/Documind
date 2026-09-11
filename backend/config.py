import os
from dotenv import load_dotenv
import streamlit as st
import chromadb
from chromadb.config import Settings
from fastembed import TextEmbedding
from groq import Groq

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "./data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
LOG_FILE = os.path.join(DATA_DIR, "audit_log.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@st.cache_resource(show_spinner=False)
def get_embedder():
    return TextEmbedding(model_name="BAAI/bge-small-en-v1.5")


@st.cache_resource(show_spinner=False)
def get_collection():
    db = chromadb.PersistentClient(
        path=os.path.join(DATA_DIR, "chroma"),
        settings=Settings(anonymized_telemetry=False),
    )
    return db.get_or_create_collection("documents")


@st.cache_resource(show_spinner=False)
def get_groq():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        st.error("⚠️ GROQ_API_KEY is missing. Add it to your .env file and restart.")
        st.stop()
    return Groq(api_key=key)
