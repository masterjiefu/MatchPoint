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

    # --- NEW STANDALONE EVENT UI ---
    elif st.session_state.event_type_choice == "Standalone":
        st.header("Standalone Event Setup")
        
        with st.form("create_standalone_event_form"):
            st.subheader("Step 1: Name Your Event and Choose Sport")
            event_name = st.text_input("Event Name (e.g., 'Annual Pickleball Open')")
            event_date = st.date_input("Event Date")
            sport = st.selectbox("Select the Sport for this Event", ["Badminton", "Pickleball", "Captain Ball"])

            st.divider()

            st.subheader("Step 2: Define All Tournaments for the Event")
            st.write(f"Define the different tournament categories for **{sport}**.")
            
            initial_tournaments = pd.DataFrame([
                {"Tournament Name": "Men's Doubles - Open", "Match Type": "Mens Doubles", "Format": "2 Brackets"},
                {"Tournament Name": "Women's Doubles - Open", "Match Type": "Womens Doubles", "Format": "2 Brackets"},
            ])
            
            edited_tournaments = st.data_editor(
                initial_tournaments,
                num_rows="dynamic",
                column_config={
                    "Tournament Name": st.column_config.TextColumn(required=True),
                    "Match Type": st.column_config.SelectboxColumn("Match Type", options=["Mens Doubles", "Womens Doubles", "Mix Doubles", "Standard"], required=True),
                    "Format": st.column_config.SelectboxColumn("Format", options=["Full Round Robin", "2 Brackets", "3 Brackets", "4 Brackets"], required=True),
                }
            )

            submit_standalone_button = st.form_submit_button("Create Event and Add Tournaments")

            if submit_standalone_button:
                if event_name and event_date:
                    try:
                        event_response = supabase.table("events").insert({ "event_name": event_name, "event_date": str(event_date) }).execute()
                        new_event_id = event_response.data[0]['id']
                        
                        tournaments_to_insert = []
                        for index, row in edited_tournaments.iterrows():
                            if not row["Tournament Name"]:
                                continue
                            if row["Format"] == "Full Round Robin": num_brackets = 0
                            else: num_brackets = int(row["Format"].split(" ")[0])
                            
                            tournaments_to_insert.append({
                                "event_id": new_event_id, "name": row["Tournament Name"], "sport": sport, 
                                "match_type": row["Match Type"], "num_brackets": num_brackets
                            })
                        
                        if tournaments_to_insert:
                            supabase.table("tournaments").insert(tournaments_to_insert).execute()
                            st.success(f"Event '{event_name}' and its {len(tournaments_to_insert)} tournaments were created successfully!")
                            st.balloons()
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.warning("Please provide an event name and a date.")

    elif st.session_state.event_type_choice == "Festival":
        st.header("Festival Event Setup")
        # ... (Festival logic is the same as before) ...
        
# If user is not logged in, show the login/register page.
else:
    st.title("Welcome to MatchPoint! 🏆")
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Register"])
    # ... (Login/Register logic is the same as before) ...
