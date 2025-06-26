import streamlit as st
from supabase import create_client, Client
import os

# --- DATABASE CONNECTION ---
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(supabase_url, supabase_key)
    st.success("Successfully connected to Supabase! ✅")
except Exception as e:
    st.error("Failed to connect to Supabase. Check your secrets.")
    st.error(f"Details: {e}")
    st.stop()


# --- SIMPLE FORM TEST ---
st.title("Login Form Test (with DB Connection)")

st.write("If you can see the form below, the test is working.")

with st.form("login_form_test"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.form_submit_button("Test Login Button")

if login_button:
    st.success("The button was clicked successfully!")
