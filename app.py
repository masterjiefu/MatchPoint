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
# This securely gets the credentials we stored in Streamlit's Secrets
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    # This creates the connection to your Supabase database
    supabase: Client = create_client(supabase_url, supabase_key)
except:
    st.error("Error: Could not connect to the database. Please check your Supabase credentials in the app's secrets.")
    st.stop()


# --- USER INTERFACE ---
st.title("Welcome to MatchPoint! 🏆")
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Register"])

if page == "Login":
    st.header("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            st.info("Login logic coming soon!") # We will add this in the next step

elif page == "Register":
    st.header("Create a New Account")
    with st.form("register_form"):
        full_name = st.text_input("Full Name (as per IC)")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        register_button = st.form_submit_button("Register")

        if register_button:
            st.info("Registration logic coming soon!") # We will add this in the next step
