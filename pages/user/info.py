# info.py
import streamlit as st
import logging
import sqlite3
# Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    try:
        conn = sqlite3.connect(db_file)
        logging.info(f"Connected to database: {db_file}")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None

def create_table(conn):
    """Create the user_info table if it doesn't exist."""
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user_info
                     (first_name TEXT, last_name TEXT, company_name TEXT, position TEXT, email TEXT, address TEXT, phone TEXT, company_url TEXT)''')
        conn.commit()
        logging.info("Table user_info created or already exists.")
    except sqlite3.Error as e:
        logging.error(f"Error creating table: {e}")

def insert_user_info(conn, user_info):
    """Insert user information into the user_info table."""
    try:
        c = conn.cursor()
        c.execute("INSERT INTO user_info (first_name, last_name, company_name, position, email, address, phone, company_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  user_info)
        conn.commit()
        logging.info("User information inserted into the database.")
    except sqlite3.Error as e:
        logging.error(f"Error inserting user information: {e}")

def update_user_info(conn, user_info):
    """Update user information in the user_info table."""
    try:
        c = conn.cursor()
        c.execute('''UPDATE user_info SET first_name=?, last_name=?, company_name=?, position=?, email=?, address=?, phone=?, company_url=?''',
                  user_info)
        conn.commit()
        logging.info("User information updated in the database.")
    except sqlite3.Error as e:
        logging.error(f"Error updating user information: {e}")

def is_table_empty(conn):
    """Check if the user_info table is empty."""
    try:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM user_info")
        count = c.fetchone()[0]
        logging.info(f"Table user_info has {count} records.")
        return count == 0
    except sqlite3.Error as e:
        logging.error(f"Error checking if table is empty: {e}")
        return True

def get_user_info(conn):
    """Get user information from the user_info table."""
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM user_info")
        user_info = c.fetchone()
        logging.info("User information retrieved from the database.")
        return user_info
    except sqlite3.Error as e:
        logging.error(f"Error retrieving user information: {e}")
        return None
# Configure logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database file
DB_FILE = 'user.db'

# Create a database connection
conn = create_connection(DB_FILE)

# Create the table
if conn:
    create_table(conn)

st.header("User Info")

# Check if the table is empty
if conn and is_table_empty(conn):
    # Input fields for user information
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    company_name = st.text_input("Company Name")
    position = st.text_input("Position")
    email = st.text_input("Email")
    address = st.text_area("Address")
    phone = st.text_input("Phone")
    company_url = st.text_input("Company URL")

    # Display the entered information and save to database
    if st.button("Submit"):
        if not all([first_name, last_name, company_name, position, email, address, phone, company_url]):
            st.error("All fields must be filled out before submitting.")
            logging.warning("Submission failed: Not all fields are filled out.")
        else:
            st.subheader("Entered Information")
            st.write(f"**First Name:** {first_name}")
            st.write(f"**Last Name:** {last_name}")
            st.write(f"**Company Name:** {company_name}")
            st.write(f"**Position:** {position}")
            st.write(f"**Email:** {email}")
            st.write(f"**Address:** {address}")
            st.write(f"**Phone:** {phone}")
            st.write(f"**Company URL:** {company_url}")

            # Save to database
            insert_user_info(conn, (first_name, last_name, company_name, position, email, address, phone, company_url))
            st.success("Information saved to database")
else:
    # Display user information
    user_info = get_user_info(conn)
    if user_info:
        st.subheader("Stored Information")
        st.write(f"**First Name:** {user_info[0]}")
        st.write(f"**Last Name:** {user_info[1]}")
        st.write(f"**Company Name:** {user_info[2]}")
        st.write(f"**Position:** {user_info[3]}")
        st.write(f"**Email:** {user_info[4]}")
        st.write(f"**Address:** {user_info[5]}")
        st.write(f"**Phone:** {user_info[6]}")
        st.write(f"**Company URL:** {user_info[7]}")

        if st.button("Edit"):
            # Pre-fill the form with existing information
            first_name = st.text_input("First Name", user_info[0])
            last_name = st.text_input("Last Name", user_info[1])
            company_name = st.text_input("Company Name", user_info[2])
            position = st.text_input("Position", user_info[3])
            email = st.text_input("Email", user_info[4])
            address = st.text_area("Address", user_info[5])
            phone = st.text_input("Phone", user_info[6])
            company_url = st.text_input("Company URL", user_info[7])

            if st.button("Submit Changes"):
                if not all([first_name, last_name, company_name, position, email, address, phone, company_url]):
                    st.error("All fields must be filled out before submitting.")
                    logging.warning("Update failed: Not all fields are filled out.")
                else:
                    update_user_info(conn, (first_name, last_name, company_name, position, email, address, phone, company_url))
                    st.success("Information updated in database")
    else:
        st.error("No user information found in the database.")
        logging.error("No user information found in the database.")