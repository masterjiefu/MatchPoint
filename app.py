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

    # --- 1. EVENT MANAGEMENT ---
    st.header("Step 1: Create or Select an Event")

    with st.expander("Create New Event"):
        with st.form("create_event_form"):
            event_name = st.text_input("New Event Name (e.g., 'CBC Sports Day 2025')")
            event_date = st.date_input("Event Date")
            create_event_button = st.form_submit_button("Create Event")

            if create_event_button:
                if event_.name and event_date:
                    try:
                        supabase.table("events").insert({ "event_name": event_name, "event_date": str(event_date) }).execute()
                        st.success(f"Event '{event_name}' created successfully!")
                    except Exception as e:
                        st.error(f"Error creating event: {e}")
                else:
                    st.warning("Please provide both an event name and a date.")

    st.divider()

    try:
        events = supabase.table("events").select("id, event_name").execute().data
        event_names = {e['event_name']: e['id'] for e in events}
        
        selected_event_name = st.selectbox("Select an Event to Manage", event_names.keys())

        if selected_event_name:
            selected_event_id = event_names[selected_event_name]

            # --- 2. TOURNAMENT MANAGEMENT (within the selected event) ---
            st.header(f"Step 2: Add a Tournament to '{selected_event_name}'")
            
            with st.form("create_tournament_form", clear_on_submit=True):
                tournament_name = st.text_input("Tournament Name (e.g., 'Men's Doubles Badminton')")
                col1, col2 = st.columns(2)
                with col1:
                    sport = st.selectbox("Sport", ["Badminton", "Pickleball", "Captain Ball"])
                    format_choice = st.selectbox("Format", ["Full Round Robin", "2 Brackets", "3 Brackets", "4 Brackets"])
                with col2:
                    if sport == "Badminton" or sport == "Pickleball":
                        match_type = st.selectbox("Match Type", ["Mens Doubles", "Womens Doubles", "Mix Doubles"])
                    elif sport == "Captain Ball":
                        match_type = st.selectbox("Match Type", ["Standard"], disabled=True)
                
                create_tournament_button = st.form_submit_button("Add Tournament to Event")

                if create_tournament_button:
                    if tournament_name:
                        try:
                            if format_choice == "Full Round Robin":
                                num_brackets = 0
                            else:
                                num_brackets = int(format_choice.split(" ")[0])
                            new_tournament = { "event_id": selected_event_id, "name": tournament_name, "sport": sport, "match_type": match_type, "num_brackets": num_brackets }
                            supabase.table("tournaments").insert(new_tournament).execute()
                            st.success(f"Tournament '{tournament_name}' added to event '{selected_event_name}'!")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                    else:
                        st.warning("Please enter a tournament name.")
            
            st.divider()
            
            # --- NEW: DISPLAY REGISTERED TOURNAMENTS ---
            st.subheader("Registered Tournaments for this Event")
            tournaments_data = supabase.table("tournaments").select("*").eq("event_id", selected_event_id).execute().data
            if tournaments_data:
                st.dataframe(tournaments_data)
            else:
                st.write("No tournaments created for this event yet.")

    except Exception as e:
        st.error(f"An error occurred while fetching events: {e}")


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
