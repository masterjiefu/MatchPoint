import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

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
# Check if a match has been selected from the other page
if st.session_state.get("selected_match_id") is None:
    st.warning("Please select a match to score from the 'Match Management' page first.")
    st.stop()

selected_match_id = st.session_state.selected_match_id

try:
    # Fetch all data needed for this match in one go
    match_response = supabase.table("matches").select("*, tournaments(*), team_a:teams!matches_team_a_id_fkey(*), team_b:teams!matches_team_b_id_fkey(*)").eq("id", selected_match_id).single().execute()
    match_data = match_response.data
    
    if not match_data:
        st.error("Could not find the selected match.")
        st.stop()

    # Extract data for easier use
    tournament_sport = match_data['tournaments']['sport']
    team_a_name = match_data['team_a']['team_name']
    team_b_name = match_data['team_b']['team_name']

    st.header(f"Scoring: {team_a_name} VS {team_b_name}")
    st.subheader(f"Tournament: {match_data['tournaments']['name']} ({tournament_sport})")
    st.caption(f"Match ID: {selected_match_id}")
    st.divider()

    with st.form("scoring_form"):
        # --- CONDITIONAL SCORING UI ---
        
        # UI for Badminton and Pickleball (Set-based)
        if tournament_sport in ["Badminton", "Pickleball"]:
            st.subheader("Set Scores")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{team_a_name}**")
                team_a_set1 = st.number_input("Set 1 Score", min_value=0, key="a1", value=match_data.get('team_a_set1_score') or 0)
                team_a_set2 = st.number_input("Set 2 Score", min_value=0, key="a2", value=match_data.get('team_a_set2_score') or 0)
                team_a_set3 = st.number_input("Set 3 Score", min_value=0, key="a3", value=match_data.get('team_a_set3_score') or 0)
            with col2:
                st.write(f"**{team_b_name}**")
                team_b_set1 = st.number_input("Set 1 Score", min_value=0, key="b1", value=match_data.get('team_b_set1_score') or 0)
                team_b_set2 = st.number_input("Set 2 Score", min_value=0, key="b2", value=match_data.get('team_b_set2_score') or 0)
                team_b_set3 = st.number_input("Set 3 Score", min_value=0, key="b3", value=match_data.get('team_b_set3_score') or 0)
        
        # UI for Captain Ball (Accumulation)
        elif tournament_sport == "Captain Ball":
            st.subheader("Final Score")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{team_a_name}**")
                team_a_final = st.number_input("Final Score", min_value=0, key="a_final", value=match_data.get('team_a_final_score') or 0)
            with col2:
                st.write(f"**{team_b_name}**")
                team_b_final = st.number_input("Final Score", min_value=0, key="b_final", value=match_data.get('team_b_final_score') or 0)

        save_button = st.form_submit_button("Save Final Score")

        if save_button:
            update_data = {"status": "Completed"}
            winner_id = None
            
            # Determine winner and prepare update data based on sport
            if tournament_sport in ["Badminton", "Pickleball"]:
                team_a_sets_won = (1 if team_a_set1 > team_b_set1 else 0) + (1 if team_a_set2 > team_b_set2 else 0) + (1 if team_a_set3 > team_b_set3 else 0)
                team_b_sets_won = 3 - team_a_sets_won
                winner_id = match_data['team_a_id'] if team_a_sets_won > team_b_sets_won else match_data['team_b_id']
                update_data.update({
                    "team_a_set1_score": team_a_set1, "team_b_set1_score": team_b_set1,
                    "team_a_set2_score": team_a_set2, "team_b_set2_score": team_b_set2,
                    "team_a_set3_score": team_a_set3, "team_b_set3_score": team_b_set3,
                    "winner_id": winner_id
                })
            elif tournament_sport == "Captain Ball":
                winner_id = match_data['team_a_id'] if team_a_final > team_b_final else match_data['team_b_id']
                update_data.update({
                    "team_a_final_score": team_a_final, "team_b_final_score": team_b_final,
                    "winner_id": winner_id
                })

            try:
                supabase.table("matches").update(update_data).eq("id", selected_match_id).execute()
                st.success("Match score saved successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"Error saving score: {e}")

except Exception as e:
    st.error(f"An error occurred while fetching match data: {e}")
    st.write("Please ensure you have selected a match from the 'Match Management' page.")
