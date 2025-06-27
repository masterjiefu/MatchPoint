import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Team Registration", page_icon="👥", layout="wide")
st.title("Team Registration 👥")

# --- DATABASE CONNECTION AND USER AUTHENTICATION ---
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error("Error connecting to database. Please check secrets.")
    st.stop()

# Check if the user is logged in. If not, show a message and stop.
if not st.session_state.get("logged_in", False):
    st.warning("You must be logged in to access this page.")
    st.info("Please log in using the main 'app' page first.")
    st.stop()

# --- PAGE LOGIC ---
try:
    # Step 1: Select an Event
    events = supabase.table("events").select("id, event_name").execute().data
    if not events:
        st.warning("No events created yet. Please create an event in the Admin Dashboard first.")
        st.stop()

    event_names = {e['event_name']: e['id'] for e in events}
    selected_event_name = st.selectbox("First, select an Event:", event_names.keys())

    if selected_event_name:
        selected_event_id = event_names[selected_event_name]

        # Step 2: Select a Tournament from the chosen event
        tournaments = supabase.table("tournaments").select("id, name").eq("event_id", selected_event_id).execute().data
        if not tournaments:
            st.info("This event has no tournaments. Please add tournaments in the Admin Dashboard.")
            st.stop()

        tournament_names = {t['name']: t['id'] for t in tournaments}
        selected_tournament_name = st.selectbox("Next, select a Tournament to register teams for:", tournament_names.keys())

        if selected_tournament_name:
            selected_tournament_id = tournament_names[selected_tournament_name]

            st.divider()

            # Step 3: Register a new team for the selected tournament
            st.header(f"Register a New Team for '{selected_tournament_name}'")
            with st.form("add_team_form", clear_on_submit=True):
                team_name = st.text_input("Team Name")
                player1_name = st.text_input("Player 1 Name")
                player2_name = st.text_input("Player 2 Name")
                st.markdown("---")
                reserve_man_1_name = st.text_input("Reserve Man 1")
                reserve_man_2_name = st.text_input("Reserve Man 2")
                reserve_woman_1_name = st.text_input("Reserve Woman 1")

                add_team_button = st.form_submit_button("Add Team to Tournament")

                if add_team_button:
                    if team_name and player1_name and player2_name:
                        new_team = {
                            "tournament_id": selected_tournament_id,
                            "team_name": team_name,
                            "player1_name": player1_name,
                            "player2_name": player2_name,
                            "reserve_man_1_name": reserve_man_1_name,
                            "reserve_man_2_name": reserve_man_2_name,
                            "reserve_woman_1_name": reserve_woman_1_name
                        }
                        try:
                            supabase.table("teams").insert(new_team).execute()
                            st.success(f"Team '{team_name}' added to '{selected_tournament_name}'!")
                        except Exception as e:
                            st.error(f"Error adding team: {e}")
                    else:
                        st.warning("Please fill in at least the Team Name and the two main players.")

            st.divider()

            # Step 4: Display already registered teams
            st.header("Registered Teams for this Tournament")
            teams_data = supabase.table("teams").select("*").eq("tournament_id", selected_tournament_id).execute().data
            if teams_data:
                st.dataframe(teams_data)
            else:
                st.write("No teams registered for this tournament yet.")

except Exception as e:
    st.error(f"An error occurred: {e}")
