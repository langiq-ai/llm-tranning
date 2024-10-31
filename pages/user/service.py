import streamlit as st
import sqlite3
from contextlib import contextmanager


# Database operations
@contextmanager
def get_db_connection():
    conn = sqlite3.connect("user.db")
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """
        )
        conn.commit()


def insert_product(title, description):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM services WHERE title = ?", (title,))
            if cursor.fetchone()[0] > 0:
                return "service with this title already exists."
            cursor.execute(
                "INSERT INTO services (title, description) VALUES (?, ?)",
                (title, description),
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        return str(e)


def delete_product(title):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM services WHERE title = ?", (title,))
            conn.commit()
        return True
    except sqlite3.Error as e:
        return str(e)


# Main execution
# Initialize database
init_db()

# service handling
st.header("service List")
if "services" not in st.session_state:
    st.session_state["services"] = []

# Fetch services from the database
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM services")
    st.session_state["services"] = cursor.fetchall()

import streamlit as st

for service in st.session_state["services"]:
    col1, col2, col3 = st.columns([1, 10, 2])

    with col1:
        st.subheader(service[0])
    with col2:
        st.write(service[1])
    with col3:
        if st.button(f"Delete {service[0]}", key=f"delete_{service[0]}"):
            if delete_product(service[0]):
                st.success(f"service '{service[0]}' deleted successfully!")
                st.session_state["services"] = [
                    p for p in st.session_state["services"] if p[0] != service[0]
                ]
                st.rerun()
            else:
                st.error(f"Failed to delete service '{service[0]}'.")

st.header("New service")
with st.form(key="product_form"):
    product_title = st.text_input("service Title")
    product_description = st.text_area("service Description", height=100)
    submit_button = st.form_submit_button(label="Add service")

    if submit_button:
        if not product_title or not product_description:
            st.error("Both fields are required.")
        else:
            result = insert_product(product_title, product_description)
            if result is True:
                st.success("service added successfully!")
                st.rerun()
            else:
                st.error(result)
