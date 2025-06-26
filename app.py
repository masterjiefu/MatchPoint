import streamlit as st
from supabase import create_client, Client
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MatchPoint",
    page_icon="🏆",
    layout="centered"
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
# This is the app's "memory". We'll use it to remember if the user is logged in.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- MAIN APP LOGIC ---

# If user is logged in, show the main app. Otherwise, show login/register page.
if st.session_state.logged_in:
    st.success("You are logged in!")
    st.header("Welcome to the Main App Dashboard!")
    st.write("All the tournament management features will go here.")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun() # Rerun the script to show the login page again

else:
    st.title("Welcome to MatchPoint! 🏆")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Register"])

    if page == "Login":
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            # --- NEW LOGIN LOGIC ---
            if login_button:
                try:
                    user_session = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    # If login is successful, the 'user' object will be populated
                    if user_session.user:
                        st.session_state
