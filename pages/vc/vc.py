import streamlit as st
import sqlite3

# Initialize session state to store vcs
if "vcs" not in st.session_state:
    st.session_state["vcs"] = []

# Connect to SQLite database
conn = sqlite3.connect("user.db")
c = conn.cursor()

# Create vcs table if it doesn't exist
c.execute(
    """
    CREATE TABLE IF NOT EXISTS vcs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL
    )
    """
)
conn.commit()

st.title("VC Page")

# Form to add new vc
with st.form(key="client_form"):
    company_name = st.text_input("VC Company Name")
    company_url = st.text_input("VC Company URL")
    submit_button = st.form_submit_button(label="Add VC")

# Add new vc to the database if not a duplicate
if submit_button:
    try:
        c.execute(
            "INSERT INTO vcs (name, url) VALUES (?, ?)", (company_name, company_url)
        )
        conn.commit()
        st.success("VC added successfully!")
    except sqlite3.IntegrityError:
        st.warning("VC already exists!")

# Search vcs
search_query = st.text_input("Search VCs")

# Retrieve and display vcs from the database
c.execute(
    "SELECT id, name, url FROM vcs WHERE name LIKE ?", ("%" + search_query + "%",)
)
filtered_clients = c.fetchall()

st.write("### VC List")
if filtered_clients:
    for vc in filtered_clients:
        col1, col2, col3 = st.columns([3, 3, 1])
        col1.write(vc[1])
        col2.write(vc[2])
        if col3.button("Remove", key=f"remove_{vc[0]}"):
            c.execute("DELETE FROM vcs WHERE id = ?", (vc[0],))
            conn.commit()
            st.experimental_rerun()
else:
    st.write("No VCs found.")

# Close the database connection
conn.close()