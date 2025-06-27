import streamlit as st

st.set_page_config(page_title="Score Match", page_icon="📝", layout="centered")
st.title("Score Match 📝")

# Check if a match has been selected from the other page
if st.session_state.get("selected_match_id") is None:
    st.warning("Please select a match to score from the 'Match Management' page first.")
    st.stop()

# If a match is selected, display its ID
selected_match_id = st.session_state.selected_match_id
st.info(f"You are now scoring Match ID: **{selected_match_id}**")

# The full scoring interface will be built here in our next step.
