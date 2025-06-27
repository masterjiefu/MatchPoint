import streamlit as st
from supabase import create_client, Client
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MatchPoint",
    page_icon="🏆",
    layout="wide" 
)

# --- DATABASE CONNECTION ---
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error("Error: Could not connect to the database. Please check your Supabase credentials in the app's secrets.")
    st.error(f"Details: {e}")
    st.stop()


# --- Initialize Session State ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MAIN APP LOGIC ---

# This main page is now ONLY for logging in.
# If the user is logged in, Streamlit will automatically show the other pages from the 'pages/' directory.
if not st.session_state.logged_in:
    st.title("Welcome to MatchPoint! 🏆")
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            try:
                user_session = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                if user_session.user:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid login credentials.")
            except Exception as e:
                st.error(f"An error occurred during login: {e}")
# If the user IS logged in, show a welcome message and the sidebar will show the other pages.
else:
    st.sidebar.success("You are logged in!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("Welcome to MatchPoint!")
    st.write("Please select a page from the navigation sidebar on the left.")
