import streamlit as st
from supabase import create_client, Client
import os
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

    if match_data.get('start_time') is None and match_data['status'] != 'Completed':
        try:
            supabase.table("matches").update({"start_time": datetime.now(timezone.utc).isoformat()}).eq("id", selected_match_id).execute()
            st.toast("Match started!")
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
        scores = {}
        if tournament_sport in ["Badminton", "Pickleball"]:
            st.subheader("Set Scores")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**{team_a_name}**")
                scores['a1'] = st.number_input("Set 1", min_value=0, step=1, key="a1", value=match_data.get('team_a_set1_score') or 0)
                scores['a2'] = st.number_input("Set 2", min_value=0, step=1, key="a2", value=match_data.get('team_a_set2_score') or 0)
                scores['a3'] = st.number_input("Set 3", min_value=0, step=1, key="a3", value=match_data.get('team_a_set3_score') or 0)
            with c2:
                st.write(f"**{team_b_name}**")
                scores['b1'] = st.number_input("Set 1", min_value=0, step=1, key="b1", value=match_data.get('team_b_set1_score') or 0, label_visibility="hidden")
                scores['b2'] = st.number_input("Set 2", min_value=0, step=1, key="b2", value=match_data.get('team_b_set2_score') or 0, label_visibility="hidden")
                scores['b3'] = st.number_input("Set 3", min_value=0, step=1, key="b3", value=match_data.get('team_b_set3_score') or 0, label_visibility="hidden")
        
        elif tournament_sport == "Captain Ball":
            # ... (Captain Ball UI is the same) ...

        save_button = st.form_submit_button("Save Final Score")

        if save_button:
            # ... (Save logic is the same) ...

except Exception as e:
    st.error(f"An error occurred while fetching match data: {e}")
