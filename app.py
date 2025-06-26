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
# This is the app's "memory". We'll use it to remember the user's choices.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'event_type_choice' not in st.session_state:
    st.session_state.event_type_choice = None


# --- A function to reset the view ---
def reset_view():
    st.session_state.event_type_choice = None


# --- MAIN APP LOGIC ---

# If user is logged in, show the main app dashboard.
if st.session_state.logged_in:
    st.sidebar.success("You are logged in!")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        # Reset all other session state variables on logout
        for key in st.session_state.keys():
            if key != 'logged_in':
                del st.session_state[key]
        st.rerun()

    # --- ADMIN DASHBOARD ---
    st.title("Admin Dashboard")

    # If an event type has been chosen, show a button to go back
    if st.session_state.event_type_choice:
        st.button("← Back to Event Type Selection", on_click=reset_view)

    # Show the initial choice if no selection has been made yet
    if not st.session_state.event_type_choice:
        st.header("Step 1: Choose Your Event Type")
        st.write("How would you like to set up your event?")
        
        col1, col2 = st.columns(2)
        if col1.button("🚀 Create Standalone Event (Single Sport)", use_container_width=True, help="For a dedicated tournament focusing on just one sport, like a weekend badminton championship."):
            st.session_state.event_type_choice = "Standalone"
            st.rerun()

        if col2.button("🎉 Create Festival Event (Multiple Sports)", use_container_width=True, help="For a large event with many different sports running at the same time, like a sports day."):
            st.session_state.event_type_choice = "Festival"
            st.rerun()

    # Show the Standalone workflow if that was chosen
    elif st.session_state.event_type_choice == "Standalone":
        st.header("Standalone Event Setup")
        st.info("The UI and logic for creating a Standalone (single sport) event will go here.")
        st.success("You selected Standalone!")

    # Show the Festival workflow if that was chosen
    elif st.session_state.event_type_choice == "Festival":
        st.header("Festival Event Setup")
        st.info("The UI and logic for creating a Festival (multi-sport) event, including the batch-creation tool, will go here.")
        st.success("You selected Festival!")


# If user is not logged in, show the login/register page.
else:
    # ... (The login/register code is the same as before) ...
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
        st.header("Create a New Account")
        with st.form("register_form"):
            full_name = st.text_input("Full Name (as per IC)")
            email = st.text_input("Email")
            phone_number = st.text_input("Phone Number")
            password = st.text_input("Password", type="password")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                if password and email and full_name and phone_number:
                    try:
                        user_session = supabase.auth.sign_up({
                            "email": email,
                            "password": password
                        })
                        if user_session.user:
                            user_id = user_session.user.id
                            supabase.table("profiles").update({
                                "full_name": full_name,
                                "phone_number": phone_number
                            }).eq("id", user_id).execute()
                            st.success("Registration successful! Please check your email to verify your account.")
                        else:
                            st.error("Registration failed after sign-up. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred during registration: {e}")
                else:
                    st.warning("Please fill out all fields.")
