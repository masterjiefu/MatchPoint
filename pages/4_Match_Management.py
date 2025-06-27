import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd
import itertools

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
            # Fetch all teams for all tournaments in this event just once for efficiency
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
                            existing_matches = supabase.table("matches").select("id", count='exact').eq("tournament_id", tournament_id).execute()
                            if existing_matches.count > 0:
                                st.warning("Matches have already been generated for this tournament.")
                            else:
                                teams_in_tournament = [team_id for team_id, team_name in team_map.items() if supabase.table("teams").select("id").eq("id", team_id).eq("tournament_id", tournament_id).execute().data]
                                
                                if len(teams_in_tournament) < 2:
                                    st.error("Cannot generate matches. At least 2 teams must be registered.")
                                else:
                                    match_pairs = list(itertools.combinations(teams_in_tournament, 2))
                                    matches_to_insert = []
                                    for pair in match_pairs:
                                        matches_to_insert.append({
                                            "tournament_id": tournament_id, "team_a_id": pair[0],
                                            "team_b_id": pair[1], "round": "Round Robin"
                                        })
                                    supabase.table("matches").insert(matches_to_insert).execute()
                                    supabase.table("tournaments").update({"status": "In Progress"}).eq("id", tournament_id).execute()
                                    st.success(f"Successfully generated {len(matches_to_insert)} matches!")
                                    st.rerun()

                    # --- UPDATED: DISPLAY MATCH SCHEDULE WITH "VS" FORMAT ---
                    if tournament_status in ['In Progress', 'Completed']:
                        st.markdown("---")
                        st.write("**Match Schedule:**")
                        match_data = supabase.table("matches").select("*").eq("tournament_id", tournament_id).execute().data
                        if match_data:
                            
                            schedule_df_data = []
                            for match in match_data:
                                team_a_name = team_map.get(match['team_a_id'], f"ID: {match['team_a_id']}")
                                team_b_name = team_map.get(match['team_b_id'], f"ID: {match['team_b_id']}")
                                
                                # Combine Team A and Team B into a single "Matchup" string
                                schedule_df_data.append({
                                    "Match ID": match['id'],
                                    "Matchup": f"{team_a_name} VS {team_b_name}",
                                    "Status": match['status']
                                })
                            
                            schedule_df = pd.DataFrame(schedule_df_data)
                            st.dataframe(schedule_df, hide_index=True)
                        else:
                            st.write("No matches generated for this tournament yet.")

except Exception as e:
    st.error(f"An error occurred: {e}")
