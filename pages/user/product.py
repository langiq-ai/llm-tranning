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
            cursor.execute("SELECT COUNT(*) FROM products WHERE title = ?", (title,))
            if cursor.fetchone()[0] > 0:
                return "Product with this title already exists."
            cursor.execute(
                "INSERT INTO products (title, description) VALUES (?, ?)",
                (title, description)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        return str(e)

def delete_product(title):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE title = ?", (title,))
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

import streamlit as st

for product in st.session_state['products']:
    col1, col2, col3 = st.columns([1, 10, 2])

    with col1:
        st.subheader(product[0])
    with col2:
        st.write(product[1])
    with col3:
        if st.button(f"Delete {product[0]}", key=f"delete_{product[0]}"):
            if delete_product(product[0]):
                st.success(f"Product '{product[0]}' deleted successfully!")
                st.session_state['products'] = [p for p in st.session_state['products'] if p[0] != product[0]]
                st.rerun()
            else:
                st.error(f"Failed to delete product '{product[0]}'.")

st.header("New Product")
with st.form(key='product_form'):
    product_title = st.text_input("Product Title")
    product_description = st.text_area("Product Description", height=100)
    submit_button = st.form_submit_button(label='Add Product')

    if submit_button:
        if not product_title or not product_description:
            st.error("Both fields are required.")
        else:
            result = insert_product(product_title, product_description)
            if result is True:
                st.success("Product added successfully!")
                st.rerun()
            else:
                st.error(result)