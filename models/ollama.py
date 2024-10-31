import os
import streamlit as st
import sqlite3
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings
import logging
import shutil
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager
from chromadb.config import Settings
from langchain_text_splitters import SentenceTransformersTokenTextSplitter



# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

st.write("ollama")

# Configuration
class Config:
    def __init__(self):
        self.current_dir = Path(__file__).parent.absolute()
        self.root_dir = self.current_dir.parent.parent
        self.book_dir = self.root_dir / "data"
        self.db_dir = self.current_dir / "db"
        self.persistent_directory = self.book_dir / "chroma_db_with_metadata"

        # Ensure directories exist
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.book_dir.mkdir(parents=True, exist_ok=True)


config = Config()

st.write(config)

with st.spinner("Creating embeddings..."):
    embeddings = NomicEmbeddings(
        model="nomic-embed-text-v1.5",
        inference_mode="local"
    )

    # Define the user's question
    query = "How can I learn more about soccentric"

    # Retrieve relevant documents based on the query
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 1},
    )
    relevant_docs = retriever.invoke(query)