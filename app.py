import streamlit as st

def register_pages():
    return {
        "-- USER -- ": [
            st.Page("./pages/user/info.py", title="Info"),
            st.Page("./pages/user/company.py", title="Company"),
            st.Page("./pages/user/product.py", title="Product"),
            st.Page("./pages/user/service.py", title="Services"),
            st.Page("./pages/user/ai.py", title="AI⭐"),
        ],
        "CLIENT": [
            st.Page("pages/client/client.py", title="Client"),
        ],
        "VENTURE CAPITAL ": [
            st.Page("./pages/vc/vc.py", title="VC"),
        ],
        "-- RETRIEVAL-AUGMENTED GENERATION -- ": [
            st.Page("./pages/rag/rag.py", title="RAG"),
        ],
        "-- TRAINING --": [
            st.Page("./pages/training/oolma.py", title="OOLama"),
        ],
    }
pages = register_pages()
pg = st.navigation(pages)
pg.run()


