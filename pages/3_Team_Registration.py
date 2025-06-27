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
        tournaments = supabase.table("tournaments").select("id, name, sport").eq("event_id", selected_event_id).execute().data
        if not tournaments:
            st.info("This event has no tournaments. Please add tournaments in the Admin Dashboard.")
            st.stop()
        
        tournament_names = {t['name']: {"id": t['id'], "sport": t['sport']} for t in tournaments}
        selected_tournament_name = st.selectbox("Next, select a Tournament to register teams for:", tournament_names.keys())
        
        if selected_tournament_name:
            selected_tournament_info = tournament_names[selected_tournament_name]
            selected_tournament_id = selected_tournament_info["id"]
            selected_tournament_sport = selected_tournament_info["sport"]

            st.divider()

            # Step 3: Register new teams using a conditional form based on the sport
            st.header(f"Register New Teams for '{selected_tournament_name}'")
            st.write("Use the table below to add multiple teams at once. Add new rows using the `+` button at the bottom.")

            # --- NEW CONDITIONAL UI LOGIC ---
            
            # If the sport is Captain Ball, show a simpler table
            if selected_tournament_sport == "Captain Ball":
                initial_teams = pd.DataFrame([ {"Team Name": ""} ])
                edited_teams = st.data_editor(
                    initial_teams, num_rows="dynamic", key=f"team_editor_cb_{selected_tournament_id}"
                )
            # Otherwise, show the full table
            else:
                initial_teams = pd.DataFrame([
                    {"Team Name": "", "Player 1 Name": "", "Player 2 Name": "", "Reserve Man 1": "", "Reserve Man 2": "", "Reserve Woman 1": ""},
                ])
                edited_teams = st.data_editor(
                    initial_teams, num_rows="dynamic", key=f"team_editor_full_{selected_tournament_id}"
                )

            if st.button("Register All Teams from Table"):
                teams_to_insert = []
                for index, row in edited_teams.iterrows():
                    # Always require a team name
                    if row["Team Name"]:
                        # Logic for Captain Ball (only team name)
                        if selected_tournament_sport == "Captain Ball":
                            teams_to_insert.append({ "tournament_id": selected_tournament_id, "team_name": row["Team Name"] })
                        # Logic for other sports (requires players)
                        elif row["Player 1 Name"] and row["Player 2 Name"]:
                            teams_to_insert.append({
                                "tournament_id": selected_tournament_id, "team_name": row["Team Name"],
                                "player1_name": row["Player 1 Name"], "player2_name": row["Player 2 Name"],
                                "reserve_man_1_name": row["Reserve Man 1"], "reserve_man_2_name": row["Reserve Man 2"],
                                "reserve_woman_1_name": row["Reserve Woman 1"]
                            })

                if teams_to_insert:
                    try:
                        supabase.table("teams").insert(teams_to_insert).execute()
                        st.success(f"Successfully registered {len(teams_to_insert)} new team(s) for '{selected_tournament_name}'!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error registering teams: {e}")
                else:
                    st.warning("No complete teams were entered in the table. Please make sure all required fields are filled.")
            
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
