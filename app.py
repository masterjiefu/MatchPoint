import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

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

    if st.session_state.event_type_choice:
        st.button("← Back to Event Type Selection", on_click=reset_view)

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

    elif st.session_state.event_type_choice == "Standalone":
        st.header("Standalone Event Setup")
        st.info("The UI and logic for creating a Standalone (single sport) event will go here.")
        # We will build this out later

    # --- NEW FESTIVAL EVENT UI ---
    elif st.session_state.event_type_choice == "Festival":
        st.header("Festival Event Setup")
        
        with st.form("create_festival_event_form"):
            st.subheader("Step 1: Name Your Festival Event")
            event_name = st.text_input("Event Name (e.g., 'CBC Sports Day 2025')")
            event_date = st.date_input("Event Date")
            
            st.divider()

            st.subheader("Step 2: Define All Tournaments for the Event")
            st.write("Use the table below to add as many tournaments as you need. You can add new rows using the `+` button at the bottom of the table.")

            # Create an initial structure for the editable table
            initial_tournaments = pd.DataFrame([
                {"Tournament Name": "Men's Doubles Badminton", "Sport": "Badminton", "Match Type": "Mens Doubles", "Format": "4 Brackets"},
                {"Tournament Name": "", "Sport": "Pickleball", "Match Type": "Mixed Doubles", "Format": "Full Round Robin"},
            ])

            # Use st.data_editor to create an editable, spreadsheet-like table
            edited_tournaments = st.data_editor(
                initial_tournaments,
                num_rows="dynamic", # Allows user to add or delete rows
                column_config={
                    "Sport": st.column_config.SelectboxColumn("Sport", options=["Badminton", "Pickleball", "Captain Ball"], required=True),
                    "Match Type": st.column_config.SelectboxColumn("Match Type", options=["Mens Doubles", "Womens Doubles", "Mix Doubles", "Standard"], required=True),
                    "Format": st.column_config.SelectboxColumn("Format", options=["Full Round Robin", "2 Brackets", "3 Brackets", "4 Brackets"], required=True),
                }
            )
            
            submit_festival_button = st.form_submit_button("Create Event and Add Tournaments")

            if submit_festival_button:
                st.info("Logic to save the event and all the tournaments from the table will go here next!")


# If user is not logged in, show the login/register page.
else:
    # ... (The login/register code is the same as before) ...
    st.title("Welcome to MatchPoint! 🏆")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Register"])

    if page == "Login":
        st.header("Login")
        # ... (rest of login form) ...
    elif page == "Register":
        st.header("Create a New Account")
        # ... (rest of register form) ...
