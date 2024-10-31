import sqlite3
import yaml
import os
import streamlit as st
from contextlib import contextmanager
from typing import List, Tuple, Optional


# Database Connection
@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = sqlite3.connect("user.db")
        yield conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


# Database Initialization
def init_db():
    """Initialize database with necessary tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create user_info table
        cursor.execute(
            """
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
        """
        )

        # Create products table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT
            )
        """
        )

        # Create services table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS service (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT
            )
        """
        )

        conn.commit()


def get_scraping_data():
    try:
        with sqlite3.connect("user.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_name, data FROM scraping_data")
            return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []


# Data Fetching
def fetch_data(table: str, columns: List[str]) -> List[Tuple]:
    """Generic function to fetch data from any table."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            column_names = ", ".join(columns)
            cursor.execute(f"SELECT {column_names} FROM {table}")
            return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching data from {table}: {e}")
        return []


# User Information
def get_user_info() -> List[Tuple]:
    """Get user information from database."""
    return fetch_data(
        "user_info",
        [
            "first_name",
            "last_name",
            "company_name",
            "position",
            "email",
            "address",
            "phone",
            "company_url",
        ],
    )


def display_user_info(user_data: List[Tuple]):
    """Display user information in a structured format."""
    if not user_data:
        st.warning("No user information found in the database.")
        return

    st.markdown("### User Information")

    for user in user_data:
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


# Products and Services
def display_items(items: List[Tuple], title: str):
    """Display products or services in a structured format."""
    if not items:
        st.info(f"No {title.lower()} found in the database.")
        return

    st.header(title)

    for item in items:
        st.subheader(f"{item[0]}")
        st.write(item[1])


def create_rag_data():
    st.write("RAG data creation process started...")

    # Fetch user info
    user_info = get_user_info()

    if not user_info:
        st.error("No user information found.")
        return

    # Use the first user's company name as an example
    company_name = user_info[0][
        2
    ]  # Assuming the company name is the third element in the tuple
    folder_path = os.path.join("data", "RAG", company_name)
    os.makedirs(folder_path, exist_ok=True)

    # Save company info to company_name.yaml in YAML format
    company_info = {
        "name": company_name,
        "info": user_info,  # Replace with actual company info
    }
    with open(os.path.join(folder_path, f"{company_name}.yaml"), "w") as file:
        yaml.dump(company_info, file)

    # Save product info to products.yaml in YAML format
    products_info = st.session_state["products"]
    with open(os.path.join(folder_path, "products.yaml"), "w") as file:
        yaml.dump(products_info, file)

    # Save service info to service.yaml in YAML format
    services_info = st.session_state["services"]
    with open(os.path.join(folder_path, "service.yaml"), "w") as file:
        yaml.dump(services_info, file)

    # Save curl data in web_curl.yaml in YAML format
    curl_data = get_scraping_data()
    with open(os.path.join(folder_path, "web_curl.yaml"), "w") as file:
        yaml.dump(curl_data, file)

    st.success("RAG data created successfully!")


# Main App
st.header("Company Dashboard")

# Initialize database
init_db()

# Initialize session state if needed
if "products" not in st.session_state:
    st.session_state["products"] = []
if "services" not in st.session_state:
    st.session_state["services"] = []

# Fetch data
try:
    # Fetch products
    st.session_state["products"] = fetch_data("products", ["title", "description"])

    # Fetch services
    st.session_state["services"] = fetch_data("services", ["title", "description"])

    # Fetch user info
    user_info = get_user_info()

    # Display all information
    display_user_info(user_info)

    # Create tabs for products and services
    tab1, tab2, tab3 = st.tabs(["Products", "Services", "Curl data"])

    with tab1:
        display_items(st.session_state["products"], "Products")

    with tab2:
        display_items(st.session_state["services"], "Services")

    with tab3:
        scraping_data = get_scraping_data()
        for company_name, data in scraping_data:
            st.write(f"**Company Name:** {company_name}")
            st.write(f"**Data:** {data}")

    if st.button("## Create RAG data "):
        create_rag_data()

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.error("Please check your database connection and try again.")
