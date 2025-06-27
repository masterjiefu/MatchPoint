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
        
        tournament_info_map = {f"{t['name']} ({t['sport']})": {"id": t['id'], "sport": t['sport']} for t in tournaments}
        selected_tournament_display_name = st.selectbox("Next, select a Tournament to register teams for:", tournament_info_map.keys())
        
        if selected_tournament_display_name:
            selected_tournament_info = tournament_info_map[selected_tournament_display_name]
            selected_tournament_id = selected_tournament_info["id"]
            selected_tournament_sport = selected_tournament_info["sport"]

            st.divider()

            # Step 3: Register new teams using a conditional form based on the sport
            st.header(f"Register New Teams for '{selected_tournament_display_name}'")
            st.write("Use the table below to add multiple teams at once. Add new rows using the `+` button at the bottom.")
            
            editor_key = f"team_editor_{selected_tournament_id}"

            if selected_tournament_sport == "Captain Ball":
                if editor_key not in st.session_state:
                    st.session_state[editor_key] = pd.DataFrame([ {"Team Name": ""} ])
                edited_teams = st.data_editor(
                    st.session_state[editor_key], num_rows="dynamic", hide_index=True, key=f"editor_cb_{selected_tournament_id}"
                )
            else:
                if editor_key not in st.session_state:
                    st.session_state[editor_key] = pd.DataFrame([
                        {"Team Name": "", "Player 1 Name": "", "Player 2 Name": "", "Reserve Man 1": "", "Reserve Man 2": "", "Reserve Woman 1": ""},
                    ])
                edited_teams = st.data_editor(
                    st.session_state[editor_key], num_rows="dynamic", hide_index=True, key=f"editor_full_{selected_tournament_id}"
                )

            if st.button("Register All Teams from Table"):
                st.session_state[editor_key] = edited_teams
                teams_to_insert = []

                for index, row in st.session_state[editor_key].iterrows():
                    if row["Team Name"]:
                        team_data = {
                            "tournament_id": selected_tournament_id,
                            "team_name": row["Team Name"]
                        }
                        if selected_tournament_sport != "Captain Ball":
                            if "Player 1 Name" in row and "Player 2 Name" in row and row["Player 1 Name"] and row["Player 2 Name"]:
                                team_data.update({
                                    "player1_name": row["Player 1 Name"], "player2_name": row["Player 2 Name"],
                                    "reserve_man_1_name": row["Reserve Man 1"], "reserve_man_2_name": row["Reserve Man 2"],
                                    "reserve_woman_1_name": row["Reserve Woman 1"]
                                })
                                teams_to_insert.append(team_data)
                        else:
                            teams_to_insert.append(team_data)
                
                if teams_to_insert:
                    try:
                        supabase.table("teams").insert(teams_to_insert).execute()
                        st.success(f"Successfully registered {len(teams_to_insert)} new team(s) for '{selected_tournament_display_name}'!")
                        st.balloons()
                        del st.session_state[editor_key]
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
                
                # --- THIS IS THE FIX ---
                # Define which columns we actually want to show to the user
                columns_to_show = ['team_name', 'player1_name', 'player2_name', 'reserve_man_1_name', 'reserve_man_2_name', 'reserve_woman_1_name']
                # Filter the dataframe to only include columns that exist
                existing_columns_to_show = [col for col in columns_to_show if col in display_df.columns]

                display_df_filtered = display_df[existing_columns_to_show]
                display_df_filtered.insert(0, 'No.', range(1, len(display_df_filtered) + 1))
                
                st.dataframe(display_df_filtered, hide_index=True)
            else:
                st.write("No teams registered for this tournament yet.")

except Exception as e:
    st.error(f"An error occurred: {e}")
