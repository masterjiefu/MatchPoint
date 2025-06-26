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

# If user is logged in, show the main app dashboard.
if st.session_state.logged_in:
    st.sidebar.success("You are logged in!")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ADMIN DASHBOARD ---
    st.title("Admin Dashboard")
    # We will add the full dashboard back after this test
    st.success("Login successful! The main dashboard will be built here.")


# If user is not logged in, show the login/register page.
else:
    st.title("Welcome to MatchPoint! 🏆")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Register"])

    if page == "Login":
        st.header("Login")
        # ADDING THE LOGIN FORM BACK
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

    elif page == "Register":
        st.header("Register Page")
        st.write("The registration form should appear here.")
        # We will add the full registration form back in the next step
