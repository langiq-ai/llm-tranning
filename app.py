import streamlit as st

st.set_page_config(layout="wide")


def register_pages():
    return {
        "-- USER -- ": [
            st.Page("pages/home.py", title="Home"),
            st.Page("./pages/user/info.py", title="Info"),
            st.Page("./pages/user/company.py", title="Company"),
            st.Page("./pages/user/product.py", title="Product"),
            st.Page("./pages/user/service.py", title="Services"),
            st.Page("pages/user/dashboard.py", title="Dashboard"),
            st.Page("./pages/user/ai.py", title="⭐ AI "),
        ],
        "CLIENT": [
            st.Page("pages/client/client.py", title="Client"),
            st.Page("pages/client/contacts.py", title="Contact"),
        ],
        "VENTURE CAPITAL ": [
            st.Page("./pages/vc/vc.py", title="VC"),
        ],
        "CARD APP ": [
            st.Page("./pages/card/card.py", title="Card App"),
        ],
        "-- RETRIEVAL-AUGMENTED GENERATION -- ": [
            st.Page("./pages/rag/rag.py", title="RAG"),
            st.Page("pages/rag/retrieval.py", title="Retrival"),
        ],
        "-- TRAINING --": [
            st.Page("pages/training/llama3.2-1b.py", title="llama3.2:1b"),
            st.Page("pages/training/gemma2-27b.py", title="Gemma2:27b"),
            st.Page("pages/training/llama3.2-3b.py", title="llama3.2:3b"),
            st.Page("pages/training/llama3.2-3b-instruct-fp16.py", title="llama3.2:3b-instruct-fp16"),
            st.Page("./pages/training/cohere.py", title="CohereLLM"),
            st.Page("./pages/training/fireworks.py", title="FireworksLLM"),
            st.Page("./pages/training/openai.py", title="OpenAILLM"),
            st.Page("./pages/training/together.py", title="TogetherLLM"),
            st.Page("./pages/training/google_vertexai.py", title="VertexAILLM"),
        ],
    }


pages = register_pages()
pg = st.navigation(pages)
pg.run()
