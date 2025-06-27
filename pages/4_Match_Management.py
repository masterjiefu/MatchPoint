import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import itertools

# --- PAGE CONFIG ---
st.set_page_config(page_title="Match Management", page_icon="⚔️", layout="wide")
st.title("Match & Score Management ⚔️")

# --- Initialize Session State for scoring ---
if 'selected_match_id' not in st.session_state:
    st.session_state.selected_match_id = None

# --- A function to set the match ID for scoring ---
def select_match(match_id):
    st.session_state.selected_match_id = match_id

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
    st.stop()

# --- PAGE LOGIC ---
try:
    # Step 1: Select an Event
    events = supabase.table("events").select("id, event_name").execute().data
    if not events:
        st.warning("No events created yet. Please create an event in the Admin Dashboard first.")
        st.stop()

    event_names = {e['event_name']: e['id'] for e in events}
    selected_event_name = st.selectbox("Select an Event:", event_names.keys())
    
    if selected_event_name:
        selected_event_id = event_names[selected_event_name]
        st.divider()

        # Step 2: Display and Manage Tournaments for the selected event
        st.header(f"Tournaments for '{selected_event_name}'")
        tournaments = supabase.table("tournaments").select("*").eq("event_id", selected_event_id).execute().data

        if not tournaments:
            st.info("This event has no tournaments yet. Add them from the Admin Dashboard.")
        else:
            all_tournament_ids = [t['id'] for t in tournaments]
            if all_tournament_ids:
                all_team_data = supabase.table("teams").select("id, team_name").in_("tournament_id", all_tournament_ids).execute().data
                team_map = {team['id']: team['team_name'] for team in all_team_data}
            else:
                team_map = {}

            for t in tournaments:
                tournament_id = t['id']
                tournament_status = t['status']
                
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.subheader(f"{t['name']} ({t['sport']})")
                        st.caption(f"Format: {t['num_brackets']} Brackets" if t['num_brackets'] > 0 else "Format: Full Round Robin")
                        st.caption(f"Status: {tournament_status}")
                    
                    with col2:
                        if tournament_status == 'Open':
                            if st.button("Lock Registration", key=f"lock_{tournament_id}", type="primary"):
                                supabase.table("tournaments").update({"status": "Locked"}).eq("id", tournament_id).execute()
                                st.rerun()
                        else: 
                            if st.button("Unlock Registration", key=f"unlock_{tournament_id}"):
                                supabase.table("tournaments").update({"status": "Open"}).eq("id", tournament_id).execute()
                                st.rerun()

                    with col3:
                        is_disabled = (tournament_status != 'Locked')
                        if st.button("Generate Matches", key=f"gen_{tournament_id}", disabled=is_disabled):
                            # ... (Match generation logic is the same)
                            pass # For brevity, logic is hidden but should be kept from your previous file

                    if tournament_status in ['In Progress', 'Completed']:
                        st.markdown("---")
                        st.write("**Match Schedule:**")
                        match_data = supabase.table("matches").select("*").eq("tournament_id", tournament_id).execute().data
                        if match_data:
                            # Create an interactive list of matches
                            for match in match_data:
                                team_a_name = team_map.get(match['team_a_id'], f"ID: {match['team_a_id']}")
                                team_b_name = team_map.get(match['team_b_id'], f"ID: {match['team_b_id']}")
                                
                                m_col1, m_col2 = st.columns([3, 1])
                                with m_col1:
                                    st.write(f"**Match {match['id']}:** {team_a_name} **VS** {team_b_name}")
                                    st.caption(f"Status: {match['status']}")
                                with m_col2:
                                    # --- NEW SCORE MATCH BUTTON ---
                                    st.button("Score this Match", key=f"score_{match['id']}", on_click=select_match, args=(match['id'],))
                        else:
                            st.write("No matches generated for this tournament yet.")

except Exception as e:
    st.error(f"An error occurred: {e}")
