```python
import streamlit as st
from supabase import create_client, Client
import os

# --- PAGE CONFIG ---
st.set_page_config(st.write("Version 2")
    page_title="MatchPoint",
    page_icon="🏆",
    layout="centered"
)

# --- DATABASE CONNECTION ---
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
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
            st.info("Login logic coming soon!")

elif page == "Register":
    st.header("Create a New Account")
    with st.form("register_form"):
        full_name = st.text_input("Full Name (as per IC)")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        register_button = st.form_submit_button("Register")

        # --- NEW REGISTRATION LOGIC ---
        if register_button:
            if password and email and full_name and phone_number:
                try:
                    # Step 1: Create the user in Supabase Authentication
                    user = supabase.auth.sign_up({
                        "email": email,
                        "password": password,
                    })
                    
                    # Step 2: Update the user's profile in our 'profiles' table with the extra details
                    # Note: We need to get the user's ID from the session after they are created.
                    # For now, we get the user id from the response, but a more robust way is to use the session.
                    # This is a good starting point.
                    if user.user:
                        user_id = user.user.id
                        supabase.table("profiles").update({
                            "full_name": full_name,
                            "phone_number": phone_number
                        }).eq("id", user_id).execute()

                        st.success("Registration successful! Please check your email to verify your account.")
                    else:
                         st.error("Registration failed. Please try again.")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please fill out all fields.")

```
