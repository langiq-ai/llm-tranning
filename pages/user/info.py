import streamlit as st
import logging
import sqlite3
from contextlib import contextmanager
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect('user.db')
        yield conn
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None


def validate_url(url):
    """Validate URL format"""
    pattern = r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
    return re.match(pattern, url) is not None


def init_database():
    """Initialize database and create table"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_info
                         (first_name TEXT, last_name TEXT, company_name TEXT, 
                          position TEXT, email TEXT, address TEXT, 
                          phone TEXT, company_url TEXT)''')
        conn.commit()


def get_user_info():
    """Get user information from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_info")
        return cursor.fetchone()


def save_user_info(data, is_update=False):
    """Save or update user information"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if is_update:
            cursor.execute('''UPDATE user_info SET 
                            first_name=?, last_name=?, company_name=?, 
                            position=?, email=?, address=?, 
                            phone=?, company_url=?''', data)
        else:
            cursor.execute('''INSERT INTO user_info 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()



st.header("User Info")

# Initialize database
init_database()

# Get existing user info
user_info = get_user_info()

# State management for edit mode
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# Display/Edit form
with st.form("user_info_form"):
    if user_info and not st.session_state.edit_mode:
        # Display mode
        st.subheader("Stored Information")
        st.write(f"**First Name:** {user_info[0]}")
        st.write(f"**Last Name:** {user_info[1]}")
        st.write(f"**Company Name:** {user_info[2]}")
        st.write(f"**Position:** {user_info[3]}")
        st.write(f"**Email:** {user_info[4]}")
        st.write(f"**Address:** {user_info[5]}")
        st.write(f"**Phone:** {user_info[6]}")
        st.write(f"**Company URL:** {user_info[7]}")

        if st.form_submit_button("Edit"):
            st.session_state.edit_mode = True
            st.rerun()
    else:
        # Edit/Create mode
        first_name = st.text_input("First Name", value=user_info[0] if user_info else "")
        last_name = st.text_input("Last Name", value=user_info[1] if user_info else "")
        company_name = st.text_input("Company Name", value=user_info[2] if user_info else "")
        position = st.text_input("Position", value=user_info[3] if user_info else "")
        email = st.text_input("Email", value=user_info[4] if user_info else "")
        address = st.text_area("Address", value=user_info[5] if user_info else "")
        phone = st.text_input("Phone", value=user_info[6] if user_info else "")
        company_url = st.text_input("Company URL", value=user_info[7] if user_info else "")

        if st.form_submit_button("Submit"):
            # Validate inputs
            validation_errors = []
            if not validate_email(email):
                validation_errors.append("Invalid email format")
            if not validate_phone(phone):
                validation_errors.append("Invalid phone number format")
            if not validate_url(company_url):
                validation_errors.append("Invalid URL format")

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            elif not all([first_name, last_name, company_name, position, email, address, phone, company_url]):
                st.error("All fields must be filled out")
            else:
                data = (first_name, last_name, company_name, position,
                        email, address, phone, company_url)
                try:
                    save_user_info(data, is_update=bool(user_info))
                    st.success("Information saved successfully")
                    st.session_state.edit_mode = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving data: {str(e)}")
                    logging.error(f"Error saving data: {e}")


