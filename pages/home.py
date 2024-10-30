import streamlit as st
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """
    Establish a connection to the SQLite database.

    Returns:
        sqlite3.Connection: Database connection object.
    """
    logging.info("Establishing database connection.")
    conn = sqlite3.connect('user.db')
    logging.info("Database connection established.")
    return conn

def get_user_info():
    """
    Fetch user information from the database.

    Returns:
        tuple: A tuple containing the first name and last name of the user, or None if no user info is found.
    """
    logging.info("Fetching user information from the database.")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name FROM user_info")
        user_info = cursor.fetchone()
        if user_info:
            logging.info(f"User information retrieved: {user_info}")
        else:
            logging.warning("No user information found in the database.")
        return user_info

# Fetch user info
logging.info("Starting to fetch user information.")
user_info = get_user_info()

# Display welcome message
if user_info:
    first_name, last_name = user_info
    logging.info(f"Displaying welcome message for user: {first_name} {last_name}")
    st.markdown(f"# Welcome {first_name} {last_name}")
else:
    logging.info("Displaying generic welcome message.")
    st.markdown("# Welcome")