import streamlit as st
import sqlite3

# Initialize session state to store clients
if 'clients' not in st.session_state:
    st.session_state['clients'] = []

# Connect to SQLite database
conn = sqlite3.connect('user.db')
c = conn.cursor()

# Create clients table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        url TEXT NOT NULL
    )
''')
conn.commit()

st.title("Client Page")

# Form to add new client
with st.form(key='client_form'):
    company_name = st.text_input("Client Company Name")
    company_url = st.text_input("Client Company URL")
    submit_button = st.form_submit_button(label='Add Client')

# Add new client to the database if not a duplicate
if submit_button:
    try:
        c.execute('INSERT INTO clients (name, url) VALUES (?, ?)', (company_name, company_url))
        conn.commit()
        st.success("Client added successfully!")
    except sqlite3.IntegrityError:
        st.warning("Client already exists!")

# Search clients
search_query = st.text_input("Search Clients")

# Retrieve and display clients from the database
c.execute('SELECT id, name, url FROM clients WHERE name LIKE ?', ('%' + search_query + '%',))
filtered_clients = c.fetchall()

st.write("### Client List")
if filtered_clients:
    for client in filtered_clients:
        col1, col2, col3 = st.columns([3, 3, 1])
        col1.write(client[1])
        col2.write(client[2])
        if col3.button("Remove", key=f"remove_{client[0]}"):
            c.execute('DELETE FROM clients WHERE id = ?', (client[0],))
            conn.commit()
            st.rerun()
else:
    st.write("No clients found.")

# Close the database connection
conn.close()