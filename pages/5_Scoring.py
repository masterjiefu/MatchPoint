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

# --- HELPER FUNCTION TO DETERMINE WINNER ---
def get_winner_id(match_data, scores):
    team_a_id = match_data['team_a']['id']
    team_b_id = match_data['team_b']['id']
    sport = match_data['tournaments']['sport']

    if sport in ["Badminton", "Pickleball"]:
        team_a_sets_won = (1 if scores['a1'] > scores['b1'] else 0) + \
                          (1 if scores['a2'] > scores['b2'] else 0) + \
                          (1 if scores['a3'] > scores['b3'] else 0)
        team_b_sets_won = 3 - team_a_sets_won
        if team_a_sets_won > team_b_sets_won:
            return team_a_id
        else:
            return team_b_id
            
    elif sport == "Captain Ball":
        if scores['a_final'] > scores['b_final']:
            return team_a_id
        else:
            return team_b_id
    return None

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

    if match_data.get('start_time') is None:
        try:
            supabase.table("matches").update({"start_time": datetime.now(timezone.utc).isoformat()}).eq("id", selected_match_id).execute()
            st.toast("Match started!")
        except Exception as e:
            st.warning(f"Could not set start time: {e}")

    team_a_name = match_data['team_a']['team_name']
    team_b_name = match_data['team_b']['team_name']

    st.header(f"Scoring: {team_a_name} VS {team_b_name}")
    st.subheader(f"Tournament: {match_data['tournaments']['name']} ({match_data['tournaments']['sport']})")
    st.divider()

    with st.form("scoring_form"):
        scores = {}
        if match_data['tournaments']['sport'] in ["Badminton", "Pickleball"]:
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
        
        elif match_data['tournaments']['sport'] == "Captain Ball":
            st.subheader("Final Score")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**{team_a_name}**")
                scores['a_final'] = st.number_input("Final Score", min_value=0, step=1, key="a_final", value=match_data.get('team_a_final_score') or 0)
            with c2:
                st.write(f"**{team_b_name}**")
                scores['b_final'] = st.number_input("Final Score", min_value=0, step=1, key="b_final", value=match_data.get('team_b_final_score') or 0, label_visibility="hidden")

        save_button = st.form_submit_button("Save Final Score")

        if save_button:
            winner_id = get_winner_id(match_data, scores)
            update_data = {
                "status": "Completed", "end_time": datetime.now(timezone.utc).isoformat(),
                "winner_id": winner_id,
                "team_a_player1_actual": match_data['team_a']['player1_name'], "team_a_player2_actual": match_data['team_a']['player2_name'],
                "team_b_player1_actual": match_data['team_b']['player1_name'], "team_b_player2_actual": match_data['team_b']['player2_name'],
                "team_a_set1_score": scores.get('a1'), "team_b_set1_score": scores.get('b1'),
                "team_a_set2_score": scores.get('a2'), "team_b_set2_score": scores.get('b2'),
                "team_a_set3_score": scores.get('a3'), "team_b_set3_score": scores.get('b3'),
                "team_a_final_score": scores.get('a_final'), "team_b_final_score": scores.get('b_final')
            }
            try:
                response = supabase.table("matches").update(update_data).eq("id", selected_match_id).execute()
                if response.data:
                    st.success("Match score saved successfully!")
                    st.balloons()
                else:
                    st.error("Data was not saved.")
                    st.write("Error details:", response.error if hasattr(response, 'error') else "No details")
            except Exception as e:
                st.error(f"Error saving score: {e}")

except Exception as e:
    st.error(f"An error occurred while fetching match data: {e}")
