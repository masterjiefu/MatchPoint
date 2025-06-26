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

# If user is logged in, show the main app. Otherwise, show login/register page.
if st.session_state.logged_in:
    st.success("You are logged in!")
    st.header("Welcome to the Main App Dashboard!")
    # Dashboard code will go here later
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

else:
    st.title("Welcome to MatchPoint! 🏆")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Register"])

    if page == "Login":
        st.header("Login Page")
        st.write("The login form should appear here. This proves the page navigation is working.")
        # We will add the form back in the next step

    elif page == "Register":
        st.header("Register Page")
        st.write("The registration form should appear here.")
        # We will add the form back in the next step
