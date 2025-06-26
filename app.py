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
    st.header("Create New Tournament")

    # The indentation of all lines inside this 'with' block is very important
    with st.form("create_tournament_form"):
        tournament_name = st.text_input("Tournament Name")
        
        col1, col2 = st.columns(2)
        with col1:
            sport = st.selectbox("Sport", ["Badminton", "Pickleball", "Captain Ball"])
            format_choice = st.selectbox("Format", ["Full Round Robin", "2 Brackets", "3 Brackets", "4 Brackets"])
        with col2:
            if sport == "Badminton" or sport == "Pickleball":
                match_type = st.selectbox("Match Type", ["Mens Doubles", "Womens Doubles", "Mix Doubles"])
            elif sport == "Captain Ball":
                match_type = st.selectbox("Match Type", ["Standard"], disabled=True)
        
        create_button = st.form_submit_button("Create Tournament")

        if create_button:
            if tournament_name:
                try:
                    if format_choice == "Full Round Robin":
                        num_brackets = 0
                    else:
                        num_brackets = int(format_choice.split(" ")[0])

                    new_tournament = {
                        "name": tournament_name,
                        "sport": sport,
                        "match_type": match_type,
                        "num_brackets": num_brackets
                    }
                    
                    supabase.table("tournaments").insert(new_tournament).execute()
                    
                    st.success(f"Tournament '{tournament_name}' created successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a tournament name.")


# If user is not logged in, show the login/register page.
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
