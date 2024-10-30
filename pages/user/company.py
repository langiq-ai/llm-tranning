import streamlit as st
import sqlite3
from contextlib import contextmanager


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
        st.button("Search ")

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
