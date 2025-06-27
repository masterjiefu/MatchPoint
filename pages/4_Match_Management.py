import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

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
    # Step 1: Select an Event and Tournament
    events = supabase.table("events").select("id, event_name").execute().data
    if not events:
        st.warning("No events created yet. Please create an event in the Admin Dashboard first.")
        st.stop()

    event_names = {e['event_name']: e['id'] for e in events}
    selected_event_name = st.selectbox("Select an Event:", event_names.keys())
    selected_event_id = event_names[selected_event_name]

    tournaments = supabase.table("tournaments").select("id, name, sport").eq("event_id", selected_event_id).execute().data
    if not tournaments:
        st.info("This event has no tournaments.")
        st.stop()

    tournament_names = {f"{t['name']} ({t['sport']})": t['id'] for t in tournaments}
    selected_tournament_display_name = st.selectbox("Select a Tournament to Manage:", tournament_names.keys())
    selected_tournament_id = tournament_names[selected_tournament_display_name]

    st.divider()

    # Step 2: Display registered teams and add a button for match generation
    st.header(f"Managing: {selected_tournament_display_name}")

    teams_data = supabase.table("teams").select("*").eq("tournament_id", selected_tournament_id).execute().data
    if teams_data:
        st.write("Current Registered Teams:")
        st.dataframe(teams_data)

        st.info("Match generation logic coming in the next step!")
        # The Generate Matches button will go here
    else:
        st.write("No teams have been registered for this tournament yet.")

except Exception as e:
    st.error(f"An error occurred: {e}")
