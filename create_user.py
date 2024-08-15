import streamlit as st
from db_utils import create_user, hash_password, check_user_exists
import time

def sign_up():
    st.title("Sign Up")

    with st.form(key='signup_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')

        if st.form_submit_button("Sign Up"):
            if password != confirm_password:
                st.error("Passwords do not match.")
                return

            if check_user_exists(username):
                st.error("Username already exists. Please choose a different username.")
                return

            hashed_password = hash_password(password)
            create_user(username, hashed_password)
            st.session_state.page = "Login"
            # st.session_state.signup_message = "Account created successfully! Please log in."
            st.success("Sign up successful! Redirecting to login page...")
            
            st.markdown("""
                 <script>
                setTimeout(function() {
                window.location.href = 'http://localhost:8501/login';  // Adjust the path to your login page if different
                }, 2000); 
            </script>
            """, unsafe_allow_html=True)
            st.stop() 

