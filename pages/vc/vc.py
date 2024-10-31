import streamlit as st
import sqlite3


# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect("user.db")
    return conn


# Function to remove a vc
def remove_client(vc_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM vcs WHERE id = ?", (vc_id,))
    conn.commit()
    conn.close()


# Function to edit a vc (placeholder for now)
def edit_client(vc_id):
    st.session_state["edit_client_id"] = vc_id
    # Edit form (if an edit is in progress)
    if "edit_client_id" in st.session_state:
        st.title("Edit vc")
        # Fetch current vc details
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "SELECT name, url FROM vcs WHERE id = ?",
            (st.session_state["edit_client_id"],),
        )
        vc = c.fetchone()
        conn.close()

        with st.form(key="edit_client_form"):
            company_name = st.text_input("vc Company Name", value=vc[0] if vc else "")
            company_url = st.text_input("vc Company URL", value=vc[1] if vc else "")
            submit_button = st.form_submit_button(label="Update vc")

            if submit_button:
                conn = get_db_connection()
                c = conn.cursor()
                try:
                    c.execute(
                        "UPDATE vcs SET name = ?, url = ? WHERE id = ?",
                        (company_name, company_url, st.session_state["edit_client_id"]),
                    )
                    conn.commit()
                    st.success("vc updated successfully!")
                    del st.session_state["edit_client_id"]
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.warning("vc update failed!")
                finally:
                    conn.close()


# Function to edit a vc (placeholder for now)
def fetch_client(vc_id):
    st.session_state["edit_client_id"] = vc_id


# Initialize database and create table
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
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
    conn.close()


# Initialize the database
init_db()


# Streamlit app

st.title("VC Management")

# Search vcs
search_query = st.text_input("Search vcs")

# Retrieve and display vcs from the database
conn = get_db_connection()
c = conn.cursor()
c.execute(
    "SELECT id, name, url FROM vcs WHERE name LIKE ?", ("%" + search_query + "%",)
)
filtered_clients = c.fetchall()
conn.close()

st.write("### VC List")
if filtered_clients:
    for vc in filtered_clients:
        col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])
        col1.write(vc[1])  # Name
        col2.write(vc[2])  # URL

        if col3.button(
            "Remove",
            key=f"remove_{vc[0]}",
            on_click=remove_client,
            args=(vc[0],),
        ):
            st.rerun()

        if col4.button(
            "Edit",
            key=f"edit_{vc[0]}",
            on_click=edit_client,
            args=(vc[0],),
        ):
            st.rerun()

        if col5.button(
            "Fetch",
            key=f"fetch_{vc[0]}",
            on_click=fetch_client,
            args=(vc[0],),
        ):
            st.rerun()

else:
    st.write("No vcs found.")

# Add new vc form
st.title("Add VC")
with st.form(key="client_form"):
    company_name = st.text_input("vc Company Name")
    company_url = st.text_input("vc Company URL")
    submit_button = st.form_submit_button(label="Add vc")

    # Add new vc to the database if not a duplicate
    if submit_button:
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO vcs (name, url) VALUES (?, ?)",
                (company_name, company_url),
            )
            conn.commit()
            st.success("vc added successfully!")
        except sqlite3.IntegrityError:
            st.warning("vc already exists!")
        finally:
            conn.close()
