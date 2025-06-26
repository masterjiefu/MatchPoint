import streamlit as st

st.title("Login Form Test")

st.write("If you can see the form below, the test is working.")

with st.form("login_form_test"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.form_submit_button("Test Login Button")

if login_button:
    st.success("The button was clicked successfully!")
