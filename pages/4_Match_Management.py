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
                        # --- Lock/Unlock Logic ---
                        if tournament_status == 'Open':
                            if st.button("Lock Registration", key=f"lock_{tournament_id}", type="primary"):
                                supabase.table("tournaments").update({"status": "Locked"}).eq("id", tournament_id).execute()
                                st.rerun()
                        else: # Status is 'Locked'
                            if st.button("Unlock Registration", key=f"unlock_{tournament_id}"):
                                supabase.table("tournaments").update({"status": "Open"}).eq("id", tournament_id).execute()
                                st.rerun()

                    with col3:
                        # --- Generate Matches Button (disabled until locked) ---
                        is_disabled = (tournament_status != 'Locked')
                        if st.button("Generate Matches", key=f"gen_{tournament_id}", disabled=is_disabled):
                            st.info("Match generation logic coming soon!")

except Exception as e:
    st.error(f"An error occurred: {e}")
