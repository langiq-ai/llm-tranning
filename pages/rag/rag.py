import os
import sqlite3
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings

# Header
st.header("Tetrieval Augmented Generation")

# Define directories
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "../../data")
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata")


def get_company_name():
    try:
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        cursor.execute("SELECT company_name FROM user_info")
        company_name = cursor.fetchone()
        return company_name[0] if company_name else None
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
        return None
    finally:
        if "conn" in locals():
            conn.close()


def remove_rag_db():
    st.warning("Removing RAG directory...")
    # remvoe the directory  if it exists persistent_directory


def generate_rag():
    if not os.path.exists(persistent_directory):
        st.success("Persistent directory does not exist. Initializing vector store...")

        documents = []

        company = get_company_name()
        books_dir = os.path.join(data_dir, "RAG", company)

        if not os.path.exists(books_dir):
            st.error(
                f"The directory {books_dir} does not exist. Please check the path."
            )
            return
        else:
            st.success(f"The directory {books_dir} exists.")

        # List all text files in the directory
        book_files = [f for f in os.listdir(books_dir) if f.endswith(".yaml")]

        for book_file in book_files:
            file_path = os.path.join(books_dir, book_file)
            loader = TextLoader(file_path)
            book_docs = loader.load()
            for doc in book_docs:
                doc.metadata = {"source": book_file}
                documents.append(doc)

        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)

        st.warning("\n--- Document Chunks Information ---")
        st.warning(f"Number of document chunks: {len(docs)}")

        embeddings = NomicEmbeddings(
            model="nomic-embed-text-v1.5", inference_mode="local"
        )

        db = Chroma.from_documents(
            docs, embeddings, persist_directory=persistent_directory
        )
        st.success("Vector store created and persisted successfully.")
    else:
        st.success("Vector store already exists. No need to initialize.")


# Add buttons with callbacks
st.button("Remove Rag DB", on_click=remove_rag_db)
st.button("Generate Rag", on_click=generate_rag)
