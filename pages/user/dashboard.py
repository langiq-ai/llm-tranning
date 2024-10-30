import sqlite3
import streamlit as st
from contextlib import contextmanager
from typing import List, Tuple, Optional


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect('user.db')
        yield conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Initialize database with necessary tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create user_info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                first_name TEXT,
                last_name TEXT,
                company_name TEXT,
                position TEXT,
                email TEXT,
                address TEXT,
                phone TEXT,
                company_url TEXT
            )
        """)

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT
            )
        """)

        # Create services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT
            )
        """)

        conn.commit()


def fetch_data(table: str, columns: List[str]) -> List[Tuple]:
    """Generic function to fetch data from any table"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            column_names = ", ".join(columns)
            cursor.execute(f"SELECT {column_names} FROM {table}")
            return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching data from {table}: {e}")
        return []


def get_user_info() -> List[Tuple]:
    """Get user information from database"""
    return fetch_data(
        "user_info",
        ["first_name", "last_name", "company_name", "position",
         "email", "address", "phone", "company_url"]
    )


def display_user_info(user_data: List[Tuple]):
    """Display user information in a structured format"""
    if not user_data:
        st.warning("No user information found in the database.")
        return

    st.markdown("### User Information")

    for user in user_data:
        with st.expander(f"{user[0]} {user[1]} - {user[2]}"):
            cols = st.columns(2)

            with cols[0]:
                st.subheader("Personal Information")
                st.write(f"**Name:** {user[0]} {user[1]}")
                st.write(f"**Position:** {user[3]}")
                st.write(f"**Email:** {user[4]}")
                st.write(f"**Phone:** {user[6]}")

            with cols[1]:
                st.subheader("Company Information")
                st.write(f"**Company:** {user[2]}")
                st.write(f"**Address:** {user[5]}")
                if user[7]:  # Company URL
                    st.write(f"**Website:** [{user[7]}]({user[7]})")


def display_items(items: List[Tuple], title: str):
    """Display products or services in a structured format"""
    if not items:
        st.info(f"No {title.lower()} found in the database.")
        return

    st.header(title)

    for item in items:
        with st.expander(item[0]):  # item[0] is the title
            st.write(item[1])  # item[1] is the description



st.header("Company Dashboard")

# Initialize database
init_db()

# Initialize session state if needed
if 'products' not in st.session_state:
    st.session_state['products'] = []
if 'services' not in st.session_state:
    st.session_state['services'] = []

# Fetch data
try:
    # Fetch products
    st.session_state['products'] = fetch_data("products", ["title", "description"])

    # Fetch services
    st.session_state['services'] = fetch_data("service", ["title", "description"])

    # Fetch user info
    user_info = get_user_info()

    # Display all information
    display_user_info(user_info)

    # Create tabs for products and services
    tab1, tab2 = st.tabs(["Products", "Services"])

    with tab1:
        display_items(st.session_state['products'], "Products")

    with tab2:
        display_items(st.session_state['services'], "Services")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.error("Please check your database connection and try again.")


