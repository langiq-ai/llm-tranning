import os
import sqlite3
import streamlit as st
import time
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
import concurrent.futures

# Configure logging
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
        self.chunk_size = 3  # Number of documents to process at once
        self.max_search_time = 30  # Maximum search time in seconds

        # Ensure directories exist
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.book_dir.mkdir(parents=True, exist_ok=True)


config = Config()

# Session state initialization
if 'search_complete' not in st.session_state:
    st.session_state.search_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None


@st.cache_resource(ttl=3600)  # Cache for 1 hour
def get_embeddings():
    """Initialize and cache embeddings with timeout"""
    try:
        return NomicEmbeddings(
            model="nomic-embed-text-v1.5",
            inference_mode="local"
        )
    except Exception as e:
        logger.error(f"Error initializing embeddings: {e}")
        return None


@st.cache_resource(ttl=3600)  # Cache for 1 hour
def get_retriever():
    """Initialize and cache the vector store and retriever with timeout"""
    try:
        if not config.persistent_directory.exists():
            return None

        embeddings = get_embeddings()
        if embeddings is None:
            return None

        # Configure Chroma settings with optimized parameters
        chroma_settings = Settings(
            anonymized_telemetry=False,
            is_persistent=True,
            persist_directory=str(config.persistent_directory),
        )

        # Load the existing vector store with connection timeout
        db = Chroma(
            persist_directory=str(config.persistent_directory),
            embedding_function=embeddings,
            client_settings=chroma_settings
        )

        # Create retriever with specific search parameters
        return db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.1
            }
        )

    except Exception as e:
        logger.error(f"Error initializing retriever: {e}")
        return None


def search_with_timeout(retriever, query):
    """Execute search with timeout"""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(retriever.invoke, query)
        try:
            return future.result(timeout=config.max_search_time)
        except concurrent.futures.TimeoutError:
            raise TimeoutError("Search operation timed out")



def display_results(documents, query):
    """Display search results in a chunked format"""
    if not documents:
        st.warning("No relevant documents found for the query.")
        return

    st.subheader(f"Results for: '{query}'")

    # Create a container for all results
    with st.container():
        # Process results in chunks
        for i, doc in enumerate(documents, 1):
            st.markdown(f"### Document {i} - Source: {doc.metadata.get('source', 'Unknown')}")
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(doc.page_content)

            with col2:
                st.markdown("**Metadata:**")
                # Display metadata in a more compact format
                metadata_html = "<br>".join([
                    f"<b>{key}:</b> {value}"
                    for key, value in doc.metadata.items()
                    if key != 'source'
                ])
                st.markdown(metadata_html, unsafe_allow_html=True)

            # Add a small delay between chunks to prevent UI freezing
            time.sleep(0.05)



st.title("Document Retrieval System")

# Initialize the retriever using cache
retriever = get_retriever()

if not retriever:
    st.error("Vector store not found. Please generate the vector store first.")
    st.stop()

# Create a form for the search
with st.form(key='search_form'):
    query = st.text_area(
        "Enter your search query:",
        height=100,
        placeholder="Type your query here..."
    )
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.form_submit_button(
            label='Search',
            use_container_width=True
        )

# Process search when form is submitted
if submit_button:
    if not query:
        st.warning("Please enter a search query.")
    else:
        try:
            # Create placeholder for status messages
            status_placeholder = st.empty()
            progress_bar = st.progress(0)

            # Show initial status
            status_placeholder.text("Initializing search...")
            progress_bar.progress(20)
            time.sleep(0.1)
            st.success("Initializing search...")

            # Execute search
            status_placeholder.text("Searching documents...")
            progress_bar.progress(40)
            relevant_docs = search_with_timeout(retriever, query)
            st.success("Searching documents...")

            # Process results
            status_placeholder.text("Processing results...")
            progress_bar.progress(80)
            time.sleep(0.1)
            st.success("Processing results...1")

            # Cleanup progress indicators
            progress_bar.progress(100)
            status_placeholder.empty()
            progress_bar.empty()
            st.success("Processing results...2")

            # Store results in session state
            st.session_state.results = relevant_docs
            st.session_state.search_complete = True

            st.success("Processing results...3")
        except TimeoutError:
            sst.error("Search operation timed out. Please try a more specific query.")
        except Exception as e:
            logger.error(f"Error during search: {e}")
            st.error(f"An error occurred during the search: {str(e)}")

# Display results if search is complete
if st.session_state.search_complete and st.session_state.results is not None:
    display_results(st.session_state.results, query)


