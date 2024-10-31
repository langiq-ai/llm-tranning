import os
import sqlite3
import streamlit as st
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

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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


# Database operations
@contextmanager
def database_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect(config.root_dir / "user.db")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        st.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def get_company_name() -> Optional[str]:
    """Fetch company name from database with proper error handling"""
    try:
        with database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_name FROM user_info")
            result = cursor.fetchone()

            if result:
                company_name = result[0]
                logger.info(f"Successfully fetched company name: {company_name}")
                return company_name

            logger.warning("No company name found in database")
            return None

    except Exception as e:
        logger.error(f"Error fetching company name: {e}")
        st.error("Failed to fetch company name from database")
        return None


def remove_rag_db() -> bool:
    """Remove RAG directory with proper error handling"""
    try:
        if config.persistent_directory.exists():
            shutil.rmtree(config.persistent_directory)
            logger.info(f"Successfully removed directory: {config.persistent_directory}")
            st.success("RAG directory removed successfully")
            return True

        logger.info("RAG directory doesn't exist - nothing to remove")
        st.info("No RAG directory found to remove")
        return False

    except Exception as e:
        logger.error(f"Error removing RAG directory: {e}")
        st.error(f"Failed to remove RAG directory: {str(e)}")
        return False


def load_documents(company: str) -> List:
    """Load and process documents for the given company"""
    documents = []
    books_dir = config.book_dir / "RAG" / company

    if not books_dir.exists():
        raise FileNotFoundError(f"Company directory not found: {books_dir}")

    # Filter for YAML files
    yaml_files = list(books_dir.glob("*.yaml"))
    if not yaml_files:
        raise FileNotFoundError(f"No YAML files found in {books_dir}")

    st.info(f"Found {len(yaml_files)} YAML files to process")

    # Process each file
    for file_path in yaml_files:
        try:
            loader = TextLoader(str(file_path))
            book_docs = loader.load()
            for doc in book_docs:
                doc.metadata = {"source": file_path.name}
                documents.append(doc)
            logger.info(f"Successfully loaded: {file_path.name}")
        except Exception as e:
            logger.error(f"Error loading {file_path.name}: {e}")
            st.warning(f"Skipped {file_path.name} due to error")
            continue

    return documents


def generate_rag():
    """Generate RAG vector store with improved error handling and progress feedback"""
    try:
        if config.persistent_directory.exists():
            st.info("Vector store already exists. No need to initialize.")
            return

        company = get_company_name()
        if not company:
            st.error("Please set up company information first")
            return

        with st.spinner("Loading documents..."):
            documents = load_documents(company)

        with st.spinner("Processing documents..."):
            text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=10)
            docs = text_splitter.split_documents(documents)
            st.info(f"Created {len(docs)} document chunks")

        with st.spinner("Creating embeddings..."):
            embeddings = NomicEmbeddings(
                model="nomic-embed-text-v1.5",
                inference_mode="local"
            )

        with st.spinner("Generating vector store..."):
            # Configure Chroma settings
            chroma_settings = Settings(
                anonymized_telemetry=False,
                is_persistent=True,
                persist_directory=str(config.persistent_directory)
            )

            # Create vector store with settings
            db = Chroma.from_documents(
                documents=docs,
                embedding=embeddings,
                persist_directory=str(config.persistent_directory),
                client_settings=chroma_settings
            )

            # Explicitly persist the database
            db.persist()

        st.success("Vector store created successfully!")

    except Exception as e:
        logger.error(f"Error generating RAG: {e}")
        st.error(f"Failed to generate vector store: {str(e)}")


# Streamlit UI
st.header("Retrieval Augmented Generation")

col1, col2 = st.columns(2)

with col1:
    if st.button("Remove RAG DB", key="remove_btn"):
        if remove_rag_db():
            st.rerun()

with col2:
    if st.button("Generate RAG", key="generate_btn"):
       if  generate_rag() :
           st.rerun()



