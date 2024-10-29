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
        cursor.execute("PRAGMA table_info(user_info)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'company_description' not in columns:
            cursor.execute("ALTER TABLE user_info ADD COLUMN company_description TEXT")
            conn.commit()

def update_company_description(product_name, product_description):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_info SET product_description = ? WHERE product_name = ?",
                (product_description, product_name)
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

for product in st.session_state['products']:
    st.subheader(product['title'])
    st.write(product['description'])

st.header("New Product")
with st.form(key='product_form'):
    product_title = st.text_input("Product Title")
    product_description = st.text_area("Product Description", height=100)
    submit_button = st.form_submit_button(label='Add Product')

    if submit_button:
        if not product_title or not product_description:
            st.error("Both fields are required.")
        else:
            st.session_state['products'].insert(0, {
                'title': product_title,
                'description': product_description
            })
            st.success("Product added successfully!")
            st.rerun()