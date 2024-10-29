import streamlit as st
import sqlite3
from contextlib import contextmanager

# Database operations
@contextmanager
def get_db_connection():
    conn = sqlite3.connect('user.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """)
        conn.commit()

def insert_product(title, description):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (title, description) VALUES (?, ?)",
                (title, description)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        return str(e)

# Main execution
# Initialize database
init_db()

# Product handling
st.header("Product List")
if 'products' not in st.session_state:
    st.session_state['products'] = []

# Fetch products from the database
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM products")
    st.session_state['products'] = cursor.fetchall()

for product in st.session_state['products']:
    st.subheader(product[0])
    st.write(product[1])

st.header("New Product")
with st.form(key='product_form'):
    product_title = st.text_input("Product Title")
    product_description = st.text_area("Product Description", height=100)
    submit_button = st.form_submit_button(label='Add Product')

    if submit_button:
        if not product_title or not product_description:
            st.error("Both fields are required.")
        else:
            if insert_product(product_title, product_description):
                st.success("Product added successfully!")
                st.rerun()
            else:
                st.error("Failed to add product.")