import sqlite3
import streamlit as st
import grpc
import os
import sys

# Add the directory containing api.py and the proto directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'proto'))

from scrape_pb2 import ScrapeRequest, ScrapeBlobRequest, ScrapeStatusRequest
from scrape_pb2_grpc import ScrapeServiceStub
from contextlib import contextmanager
import re


# Database Functions
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                company_url TEXT NOT NULL,
                company_description TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        conn.commit()


def update_company_description(company_name, new_description):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_info SET company_description = ? WHERE company_name = ?",
                (new_description, company_name),
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False


# gRPC Functions
def create_stub():
    channel = grpc.insecure_channel("localhost:5200")
    return ScrapeServiceStub(channel)


def send_scrape_request(stub, name, url):
    request = ScrapeRequest(name=name, url=url)
    response = stub.Scrape(request)
    return response


def check_scraping_status(stub, name):
    status_request = ScrapeStatusRequest(name=name)
    try:
        status_response = stub.IsScrapingDone(status_request)
        return status_response.is_done
    except grpc.RpcError as e:
        st.error(f"Failed to check scraping status: {e.details()}")
        return None


def get_scraping_data():
    try:
        with sqlite3.connect("user.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT company_name, data FROM scraping_data")
            return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return []


def get_scraping_blob(stub, name):
    blob_request = ScrapeBlobRequest(name=name)
    try:
        blob_response = stub.GetScrapingBlob(blob_request)
        return blob_response.json_blob
    except grpc.RpcError as e:
        st.error(f"Failed to get scraping blob: {e.details()}")
        return None


# Streamlit App
init_db()


def strip_url(url):
    # Remove 'https://' or 'http://'
    url = re.sub(r'^https?://', '', url)
    # Remove trailing slashes
    url = url.rstrip('/')
    return url


st.header("Company Information")


def save_scraping_data_to_db(company_name, data):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM scraping_data WHERE company_name = ?",
                (company_name,)
            )
            existing_data = cursor.fetchone()

            if existing_data and existing_data[0] == data:
                st.info("Data is the same as the existing data. No update needed.")
                return False

            cursor.execute(
                "INSERT INTO scraping_data (company_name, data) VALUES (?, ?)",
                (company_name, data)
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False


with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT company_name, company_url, company_description FROM user_info")
    data = cursor.fetchall()

for company_name, company_url, company_description in data:
    st.divider()
    col1, col2, col3 = st.columns([3, 3, 1])

    with col1:
        st.write(f"**Name:** {company_name}")
    with col2:
        st.write(f"**URL:** {company_url}")
    with col3:
        if st.button("Search", key=f"search_btn_{company_name}"):
            stub = create_stub()
            try:
                send_scrape_request(stub, company_name, company_url)
            except Exception as e:
                st.warning(f"Failed to send scrape request: {e}")

    form_key = f"form_{company_name}"

    if company_description:
        st.write("**Current Description:**")
        st.write(company_description)
        if st.button(f"Edit Description", key=f"edit_btn_{company_name}"):
            st.session_state[f"edit_{company_name}"] = True

    if not company_description or st.session_state.get(f"edit_{company_name}", False):
        with st.form(key=form_key):
            new_description = st.text_area(
                "Company Description",
                value=company_description or "",
                height=200,
                key=f"textarea_{company_name}",
            )

            submit_button = st.form_submit_button(
                label="Submit" if company_description else "Add Description"
            )

            if submit_button:
                if update_company_description(company_name, new_description):
                    st.success("Company description updated successfully!")
                    if f"edit_{company_name}" in st.session_state:
                        del st.session_state[f"edit_{company_name}"]
                    st.rerun()

# Display scraping data
company_url = strip_url(company_url)
st.markdown("### Company web curl info ")
stub = create_stub()
data = get_scraping_blob(stub, company_url)

if data:
    if save_scraping_data_to_db(company_url, data):
        st.success("Scraping data saved to database successfully!")

with st.expander("Scraping Data"):
    st.write(data)
