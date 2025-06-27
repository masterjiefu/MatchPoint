import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import numpy as np

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

        tournament_info_map = {f"{t['name']} ({t['sport']})": {"id": t['id'], "sport": t['sport']} for t in tournaments}
        selected_tournament_display_name = st.selectbox("Next, select a Tournament to register teams for:", tournament_info_map.keys())

        if selected_tournament_display_name:
            selected_tournament_info = tournament_info_map[selected_tournament_display_name]
            selected_tournament_id = selected_tournament_info["id"]
            selected_tournament_sport = selected_tournament_info["sport"]

            st.divider()

            # Step 3: Register new teams using the new table format
            st.header(f"Register New Teams for '{selected_tournament_display_name}'")
            st.write("Use the table below to add multiple teams at once. Add new rows using the `+` button at the bottom.")

            editor_key = f"team_editor_{selected_tournament_id}"

            if selected_tournament_sport == "Captain Ball":
                if editor_key not in st.session_state:
                    st.session_state[editor_key] = pd.DataFrame([ {"Team Name": ""} ])
                edited_teams = st.data_editor(st.session_state[editor_key], num_rows="dynamic", disabled=["No."])
            else:
                if editor_key not in st.session_state:
                    st.session_state[editor_key] = pd.DataFrame([
                        {"Team Name": "", "Player 1 Name": "", "Player 2 Name": "", "Reserve Man 1": "", "Reserve Man 2": "", "Reserve Woman 1": ""},
                    ])
                edited_teams = st.data_editor(st.session_state[editor_key], num_rows="dynamic", disabled=["No."])


            if st.button("Register All Teams from Table"):
                st.session_state[editor_key] = edited_teams
                teams_to_insert = []

                for index, row in st.session_state[editor_key].iterrows():
                    if row["Team Name"]:
                        if selected_tournament_sport == "Captain Ball":
                            teams_to_insert.append({ "tournament_id": selected_tournament_id, "team_name": row["Team Name"] })
                        elif "Player 1 Name" in row and "Player 2 Name" in row and row["Player 1 Name"] and row["Player 2 Name"]:
                            teams_to_insert.append({
                                "tournament_id": selected_tournament_id, "team_name": row["Team Name"],
                                "player1_name": row["Player 1 Name"], "player2_name": row["Player 2 Name"],
                                "reserve_man_1_name": row["Reserve Man 1"], "reserve_man_2_name": row["Reserve Man 2"],
                                "reserve_woman_1_name": row["Reserve Woman 1"]
                            })

                if teams_to_insert:
                    try:
                        supabase.table("teams").insert(teams_to_insert).execute()
                        st.success(f"Successfully registered {len(teams_to_insert)} new team(s) for '{selected_tournament_display_name}'!")
                        st.balloons()
                        del st.session_state[editor_key] # Clear the editor after submission
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Error registering teams: {e}")
                else:
                    st.warning("No complete teams were entered in the table. Please make sure all required fields are filled.")

            st.divider()

            # Step 4: Display already registered teams
            st.header("Registered Teams for this Tournament")
            teams_data = supabase.table("teams").select("*").eq("tournament_id", selected_tournament_id).execute().data
            if teams_data:
                display_df = pd.DataFrame(teams_data)
                # Corrected logic to add the 'No.' column
                display_df.insert(0, 'No.', range(1, len(display_df) + 1))
                st.dataframe(display_df)
            else:
                st.write("No teams registered for this tournament yet.")

except Exception as e:
    st.error(f"An error occurred: {e}")
