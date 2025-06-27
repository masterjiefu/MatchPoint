import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import itertools
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Match Management", page_icon="⚔️", layout="wide")
st.title("Match & Score Management ⚔️")

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

# --- HELPER FUNCTION TO ASSIGN RESOURCES ---
def assign_resources(match_id, umpire_id, court_number):
    try:
        supabase.table("matches").update({
            "umpire_id": umpire_id,
            "court_number": court_number
        }).eq("id", match_id).execute()
        st.success(f"Successfully assigned resources to Match ID: {match_id}")
    except Exception as e:
        st.error(f"Error assigning resources: {e}")

# --- PAGE LOGIC ---
try:
    # Fetch data needed for the page
    events = supabase.table("events").select("id, event_name").execute().data
    umpires = supabase.table("profiles").select("id, full_name").eq("is_umpire_candidate", True).execute().data
    umpire_map = {ump['full_name']: ump['id'] for ump in umpires}

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
                    # ... (Tournament info and Lock/Generate buttons are the same) ...
                    
                    if t['status'] in ['In Progress', 'Completed']:
                        st.markdown("---")
                        st.write("**Match Schedule:**")
                        match_data = supabase.table("matches").select("*").eq("tournament_id", t['id']).execute().data
                        
                        for match in match_data:
                            with st.expander(f"Manage Match ID: {match['id']}"):
                                team_a_name = team_map.get(match['team_a_id'], "Unknown")
                                team_b_name = team_map.get(match['team_b_id'], "Unknown")
                                st.write(f"**{team_a_name} VS {team_b_name}** | Status: {match['status']}")

                                # Form for assigning umpire and court
                                with st.form(key=f"assign_form_{match['id']}"):
                                    st.write("Assign Umpire and Court:")
                                    c1, c2, c3 = st.columns([2,1,1])
                                    
                                    current_umpire_id = match.get('umpire_id')
                                    # Find the umpire's name from their ID to set the default value
                                    current_umpire_name = next((name for name, uid in umpire_map.items() if uid == current_umpire_id), None)
                                    
                                    assigned_umpire_name = c1.selectbox("Umpire", options=umpire_map.keys(), index=list(umpire_map.keys()).index(current_umpire_name) if current_umpire_name else 0)
                                    court_num = c2.text_input("Court No.", value=match.get('court_number') or "")
                                    
                                    if c3.form_submit_button("Assign"):
                                        umpire_id_to_save = umpire_map[assigned_umpire_name]
                                        assign_resources(match['id'], umpire_id_to_save, court_num)
                                        st.rerun()

except Exception as e:
    st.error(f"An error occurred: {e}")
