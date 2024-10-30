import sys
import os
import streamlit as st
import sqlite3
from contextlib import contextmanager
# Add the directory containing api.py to the Python path

# Add the directory containing api.py and the proto directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'proto'))

import grpc
from scrape_pb2 import ScrapeRequest, ScrapeBlobRequest, ScrapeStatusRequest
from scrape_pb2_grpc import ScrapeServiceStub


def create_stub():
    """Create a gRPC stub (client)."""
    channel = grpc.insecure_channel("localhost:5200")
    return ScrapeServiceStub(channel)


def send_scrape_request(stub, name, url):
    """Send a scrape request and return the response."""
    request = ScrapeRequest(name=name, url=url)
    response = stub.Scrape(request)
    return response


def check_scraping_status(stub, name):
    """Check if scraping is done and return the status."""
    status_request = ScrapeStatusRequest(name=name)
    try:
        status_response = stub.IsScrapingDone(status_request)
        logger.info(f"Is scraping done for {name}: {status_response.is_done}")
        return status_response.is_done
    except grpc.RpcError as e:
        logger.error(f"Failed to check scraping status for {name}: {e.details()}")
        return None


def get_scraping_blob(stub, name):
    """Get the scraping blob as JSON and return it."""
    blob_request = ScrapeBlobRequest(name=name)
    try:
        blob_response = stub.GetScrapingBlob(blob_request)
        #logger.info(f"Scraping blob for {name}: {blob_response.json_blob}")
        return blob_response.json_blob
    except grpc.RpcError as e:
        #logger.error(f"Failed to get scraping blob for {name}: {e.details()}")
        return None


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
        cursor.execute("PRAGMA table_info(user_info)")
        columns = [column[1] for column in cursor.fetchall()]
        if "company_description" not in columns:
            cursor.execute("ALTER TABLE user_info ADD COLUMN company_description TEXT")
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

def search_company(company_name):
    # Implement the search logic here
    stub = create_stub()
    send_scrape_request(stub, "EmbeddedOne", "http://embeddedone.com")

# Initialize database
init_db()

# Get company data
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT company_name, company_url, company_description FROM user_info"
    )
    data = cursor.fetchall()

# Display the information using Streamlit
st.header("Company Information")

for company_name, company_url, company_description in data:
    st.divider()
    col1, col2, col3 = st.columns([3, 3, 1])

    with col1:
        st.write(f"**Name:** {company_name}")
    with col2:
        st.write(f"**URL:** {company_url}")
    with col3:
        if st.button("Search", key=f"search_btn_{company_name}"):
            search_company(company_name)

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


# Display the information using Streamlit
st.markdown("### Company web curl info ")
stub = create_stub()
data = get_scraping_blob(stub, "soccentric.com")
with st.expander("Scraping Data"):
    st.write(data)

# save the data to web_curl in the user.db databse