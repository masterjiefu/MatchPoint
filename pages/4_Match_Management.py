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
    # We don't need to switch pages manually, we'll just tell the user to navigate.
    st.info(f"Match {match_id} selected. Please navigate to the 'Scoring' page from the sidebar.")


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
    events = supabase.table("events").select("id, event_name").execute().data
    if not events:
        st.warning("No events created yet. Please create an event in the Admin Dashboard first.")
        st.stop()

    event_names = {e['event_name']: e['id'] for e in events}
    selected_event_name = st.selectbox("Select an Event:", event_names.keys())
    
    if selected_event_name:
        selected_event_id = event_names[selected_event_name]
        st.divider()
        st.header(f"Tournaments for '{selected_event_name}'")
        tournaments = supabase.table("tournaments").select("*").eq("event_id", selected_event_id).execute().data

        if not tournaments:
            st.info("This event has no tournaments yet.")
        else:
            all_tournament_ids = [t['id'] for t in tournaments]
            if all_tournament_ids:
                all_team_data = supabase.table("teams").select("id, team_name").in_("tournament_id", all_tournament_ids).execute().data
                team_map = {team['id']: team['team_name'] for team in all_team_data}
            else:
                team_map = {}

            for t in tournaments:
                with st.container(border=True):
                    # ... Lock/Unlock and Generate Matches buttons are the same ...
                    
                    if t['status'] in ['In Progress', 'Completed']:
                        st.markdown("---")
                        st.write("**Match Schedule:**")
                        match_data = supabase.table("matches").select("*").eq("tournament_id", t['id']).execute().data
                        for match in match_data:
                            team_a_name = team_map.get(match['team_a_id'], "Unknown")
                            team_b_name = team_map.get(match['team_b_id'], "Unknown")
                            
                            m_col1, m_col2 = st.columns([3, 1])
                            with m_col1:
                                st.write(f"**Match {match['id']}:** {team_a_name} **VS** {team_b_name} | Status: {match['status']}")
                            with m_col2:
                                st.button("Score this Match", key=f"score_{match['id']}", on_click=select_match, args=(match['id'],), disabled=(match['status']=='Completed'))

except Exception as e:
    st.error(f"An error occurred: {e}")
