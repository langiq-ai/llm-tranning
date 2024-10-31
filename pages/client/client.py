import streamlit as st
import sqlite3


# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect("user.db")
    return conn


# Function to remove a client
def remove_client(client_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()


# Function to edit a client (placeholder for now)
def edit_client(client_id):
    st.session_state['edit_client_id'] = client_id
    # Edit form (if an edit is in progress)
    if 'edit_client_id' in st.session_state:
        st.title("Edit Client")
        # Fetch current client details
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name, url FROM clients WHERE id = ?", (st.session_state['edit_client_id'],))
        client = c.fetchone()
        conn.close()

        with st.form(key="edit_client_form"):
            company_name = st.text_input("Client Company Name", value=client[0] if client else '')
            company_url = st.text_input("Client Company URL", value=client[1] if client else '')
            submit_button = st.form_submit_button(label="Update Client")

            if submit_button:
                conn = get_db_connection()
                c = conn.cursor()
                try:
                    c.execute(
                        "UPDATE clients SET name = ?, url = ? WHERE id = ?",
                        (company_name, company_url, st.session_state['edit_client_id'])
                    )
                    conn.commit()
                    st.success("Client updated successfully!")
                    del st.session_state['edit_client_id']
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.warning("Client update failed!")
                finally:
                    conn.close()

# Function to edit a client (placeholder for now)
def fetch_client(client_id):
    st.session_state['edit_client_id'] = client_id


# Initialize database and create table
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            url TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# Initialize the database
init_db()


# Streamlit app

st.title("Client Management")

# Search clients
search_query = st.text_input("Search Clients")

# Retrieve and display clients from the database
conn = get_db_connection()
c = conn.cursor()
c.execute(
    "SELECT id, name, url FROM clients WHERE name LIKE ?", ("%" + search_query + "%",)
)
filtered_clients = c.fetchall()
conn.close()

st.write("### Client List")
if filtered_clients:
    for client in filtered_clients:
        col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])
        col1.write(client[1])  # Name
        col2.write(client[2])  # URL

        if col3.button(
                "Remove",
                key=f"remove_{client[0]}",
                on_click=remove_client,
                args=(client[0],),
        ): st.rerun()

        if col4.button(
                "Edit",
                key=f"edit_{client[0]}",
                on_click=edit_client,
                args=(client[0],),
        ): st.rerun()

        if col5.button(
                "Fetch",
                key=f"fetch_{client[0]}",
                on_click=fetch_client,
                args=(client[0],),
        ): st.rerun()

else:
    st.write("No clients found.")

# Add new client form
st.title("Add Client")
with st.form(key="client_form"):
    company_name = st.text_input("Client Company Name")
    company_url = st.text_input("Client Company URL")
    submit_button = st.form_submit_button(label="Add Client")

    # Add new client to the database if not a duplicate
    if submit_button:
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO clients (name, url) VALUES (?, ?)", (company_name, company_url)
            )
            conn.commit()
            st.success("Client added successfully!")
        except sqlite3.IntegrityError:
            st.warning("Client already exists!")
        finally:
            conn.close()


