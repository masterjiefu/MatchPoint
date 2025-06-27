import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
from datetime import datetime, timezone

# --- PAGE CONFIG ---
st.set_page_config(page_title="Score Match", page_icon="📝", layout="centered")
st.title("Score Match 📝")

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
if st.session_state.get("selected_match_id") is None:
    st.warning("Please select a match to score from the 'Match Management' page first.")
    st.stop()

selected_match_id = st.session_state.selected_match_id

try:
    match_response = supabase.table("matches").select("*, tournaments(*), team_a:teams!matches_team_a_id_fkey(*), team_b:teams!matches_team_b_id_fkey(*)").eq("id", selected_match_id).single().execute()
    match_data = match_response.data
    
    if not match_data:
        st.error("Could not find the selected match.")
        st.stop()

    # --- NEW: Auto-record Start Time ---
    # If the match has just started (no start time yet), record it now.
    if match_data.get('start_time') is None:
        try:
            supabase.table("matches").update({
                "start_time": datetime.now(timezone.utc).isoformat()
            }).eq("id", selected_match_id).execute()
        except Exception as e:
            st.warning(f"Could not set start time: {e}")


    tournament_sport = match_data['tournaments']['sport']
    team_a_name = match_data['team_a']['team_name']
    team_b_name = match_data['team_b']['team_name']

    st.header(f"Scoring: {team_a_name} VS {team_b_name}")
    st.subheader(f"Tournament: {match_data['tournaments']['name']} ({tournament_sport})")
    st.caption(f"Match ID: {selected_match_id}")
    st.divider()

    with st.form("scoring_form"):
        if tournament_sport in ["Badminton", "Pickleball"]:
            # ... (Set Scores UI is the same) ...
        elif tournament_sport == "Captain Ball":
            # ... (Final Score UI is the same) ...

        save_button = st.form_submit_button("Save Final Score")

        if save_button:
            # --- NEW: Add end_time to the data we save ---
            update_data = {
                "status": "Completed",
                "end_time": datetime.now(timezone.utc).isoformat(), # Record end time
                "team_a_player1_actual": match_data['team_a']['player1_name'],
                "team_a_player2_actual": match_data['team_a']['player2_name'],
                "team_b_player1_actual": match_data['team_b']['player1_name'],
                "team_b_player2_actual": match_data['team_b']['player2_name'],
            }
            winner_id = None
            
            if tournament_sport in ["Badminton", "Pickleball"]:
                # ... (Winner logic is the same) ...
            elif tournament_sport == "Captain Ball":
                # ... (Winner logic is the same) ...

            try:
                response = supabase.table("matches").update(update_data).eq("id", selected_match_id).execute()
                if response.data:
                    st.success("Match score saved successfully!")
                    st.balloons()
                else:
                    st.error("Data was not saved. The database returned an empty response.")
                    st.write("Error details:", response)

            except Exception as e:
                st.error(f"Error saving score: {e}")

except Exception as e:
    st.error(f"An error occurred while fetching match data: {e}")
