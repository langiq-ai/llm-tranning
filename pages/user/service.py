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
            CREATE TABLE IF NOT EXISTS service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL
            )
        """
        )
        conn.commit()

def insert_service(title, description):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO service (title, description) VALUES (?, ?)",
                (title, description),
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        return str(e)

# Main execution
# Initialize database
init_db()

# service handling
st.header("Service List")
if "services" not in st.session_state:
    st.session_state["services"] = []

# Fetch services from the database
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM service")
    st.session_state["services"] = cursor.fetchall()

for service in st.session_state["services"]:
    st.subheader(service[0])
    st.write(service[1])

st.header("New Service")
with st.form(key="service_form"):
    service_title = st.text_input("Service Title")
    service_description = st.text_area("Service Description", height=200)
    submit_button = st.form_submit_button(label="Add Service")

    if submit_button:
        if not service_title or not service_description:
            st.error("Both fields are required.")
        else:
            if insert_service(service_title, service_description):
                st.success("Service added successfully!")
                st.rerun()
            else:
                st.error("Failed to add service.")