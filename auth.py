"""Authentication module for Streamlit app.

This module provides password protection for the dashboard.
"""

import hashlib
import hmac
import streamlit as st
from typing import Optional


def check_password() -> bool:
    """Returns True if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(
            hashlib.sha256(st.session_state["password"].encode()).hexdigest(),
            hashlib.sha256(st.secrets["password"].encode()).hexdigest()
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show input
    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # Password not correct, show input + error
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    
    # Password correct
    else:
        return True


def logout():
    """Clear the password from session state."""
    if "password_correct" in st.session_state:
        del st.session_state["password_correct"]
    st.rerun()


def get_login_status() -> str:
    """Get current login status for display."""
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return "🔓 Logged in"
    return "🔒 Not logged in"