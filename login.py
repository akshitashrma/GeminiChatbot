import streamlit as st
from db_utils import verify_password, check_user_exists


def login_user():
    st.title("Login")

    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.form_submit_button("Login"):
            if not check_user_exists(username):
                st.error("Invalid username.")
                return

            if verify_password(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['page'] = "Chat"  # Redirect to the chat page
                # st.experimental_rerun()
            else:
                st.error("Invalid password.")
