import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings
import logging
from pathlib import Path
from chromadb.config import Settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

st.title("Ollama Chat")


# Configuration
class Config:
    def __init__(self):  # Fixed the init method syntax
        self.current_dir = Path(__file__).parent.absolute()
        self.root_dir = self.current_dir.parent.parent
        self.book_dir = self.root_dir / "data"
        self.db_dir = self.current_dir / "db"
        self.persistent_directory = self.book_dir / "chroma_db_with_metadata"
        # Ensure directories exist
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.book_dir.mkdir(parents=True, exist_ok=True)


config = Config()

# Define the embedding model
embedding = NomicEmbeddings(
    model="nomic-embed-text-v1.5",
    inference_mode="local"
)

# Configure Chroma settings with optimized parameters
chroma_settings = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)

# Load the existing vector store with connection timeout
db = Chroma(
    persist_directory=str(config.persistent_directory),
    embedding_function=embedding,
    client_settings=chroma_settings
)

# Initialize the chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Chat input
user_input = st.chat_input("Enter your query:")

if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Retrieve relevant documents based on the query
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    relevant_docs = retriever.get_relevant_documents(user_input)  # Fixed the retriever method

    combined_input = (
            "Here are some documents that might help answer the question: "
            + user_input
            + "\n\nRelevant Documents:\n"
            + "\n\n".join([doc.page_content for doc in relevant_docs])
            + "\n\nPlease provide an answer based only on the provided documents. If the answer is not found in the documents, respond with 'I'm not sure'."
    )

    # Initialize Ollama model correctly
    model = OllamaLLM(model="llama3.2:1b") # Changed from OllamaLLM to Ollama and fixed model name

    # Define the messages for the model
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=combined_input),
    ]

    # Display assistant's message with a spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Invoke the model with the messages
            result = model.invoke(messages)
            st.write(result)  # Access the content attribute of the response

    # Add assistant message to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": result})

# Display the chat history
for message in st.session_state.chat_history[:-2]:  # Exclude the last two messages as they're already displayed
    with st.chat_message(message["role"]):
        st.write(message["content"])