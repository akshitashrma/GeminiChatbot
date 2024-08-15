import streamlit as st
import google.generativeai as genai
import time
import logging
import os
# import jwt
from dotenv import load_dotenv
from login import login_user
from create_user import sign_up

# Load environment variables
load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv('Google_Api_Key'))

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# JWT configuration
# JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mysecret')

# # Create JWT token
# def create_jwt_token(username):
#     from datetime import datetime, timedelta
#     token = jwt.encode({
#         'sub': username,
#         'exp': datetime.utcnow() + timedelta(hours=168)  # 168 hours = 7 days
#     }, JWT_SECRET_KEY, algorithm='HS256')
#     return token

# # Decode JWT token
# def decode_jwt_token(token):
#     try:
#         payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
#         return payload['sub']
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None

def get_gemini_res(question, prompt, message_log, log):
    try:
        model = genai.GenerativeModel('gemini-pro')
        full_prompt = f"{prompt}\n\nUser question: {question}\n\nLog: {message_log}"
        
        res = model.generate_content(full_prompt)
        
        if hasattr(res, 'text'):
            return res.text
        else:
            return "Error: Unable to retrieve text from the response."
    except Exception as e:
        log.error(f"An error occurred while processing the request: {str(e)}")
        return "An error occurred while processing the request."

prompt = """ 
    As a sophisticated chatbot designed to engage in meaningful conversations, I rely on your input to guide our interaction. Whether you have questions,
    thoughts,
    or just want to chat, feel free to express yourself openly. 
    Remember, our previous conversations are valuable insights into our ongoing dialogue, so don't hesitate to refer back to them for context. 
    Let's embark on another enriching exchange together!
"""

def save_session_messages(username, messages, filename):
    try:
        with open(filename, "w") as file:
            for message in messages:
                file.write(f"{message['role']}: {message['content']}\n")
    except Exception as e:
        log.error(f"Failed to save session messages: {str(e)}")


def load_session_messages(filename):
    messages = []
    try:
        if filename and os.path.exists(filename):
            with open(filename, "r") as file:
                role = None
                content = ""
                for line in file:
                    line = line.strip()
                    if line.startswith("user:"):
                        if role and content:
                            messages.append({"role": role, "content": content.strip()})
                        role = "user"
                        content = line[len("user:"):].strip()
                    elif line.startswith("assistant:"):
                        if role and content:
                            messages.append({"role": role, "content": content.strip()})
                        role = "assistant"
                        content = line[len("assistant:"):].strip()
                    else:
                        content += "\n" + line.strip()
                if role and content:
                    messages.append({"role": role, "content": content.strip()})
    except Exception as e:
        log.error(f"Failed to load session messages: {str(e)}")
    return messages


def list_chat_history_files(username):
    return [f for f in os.listdir() if f.startswith(f"{username}_chat_history_") and f.endswith(".txt")]

def clear_session_messages(username):
    try:
        files = list_chat_history_files(username)
        for file in files:
            os.remove(file)
    except Exception as e:
        log.error(f"Failed to clear session messages: {str(e)}")

def clear_all_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def logout():
    clear_all_session_state()  # Clear all session data
    st.session_state.page = "Login"  # Set the page to "Login"
    st.session_state.logout_message = "You have logged out successfully!"  # Set a logout success message
    st.markdown("""
        <script>
            setTimeout(function() {
                window.location.href = '/login.py';  // Adjust the path to your login page if different
            }, 2000);  
        </script>
    """, unsafe_allow_html=True)
    st.stop() 

      
    
def start_new_chat(username):
    # Save current messages to a new file
    if st.session_state.messages:
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        new_chat_filename = f"{username}_chat_history_{timestamp}.txt"
        save_session_messages(username, st.session_state.messages, new_chat_filename)
    
    # Clear the current chat messages and set new session state
    st.session_state.messages = []  # Clear current messages
    st.session_state.current_chat_file = None  # No file associated with new chat



def main():
    # Add custom CSS to make cursor a pointer for chat history items
    st.markdown("""
        <style>
            .pointer-cursor {
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        # If not logged in, show login and sign up options
        st.sidebar.title("Welcome! Let's Chat")
        option = st.sidebar.radio("Choose an option", ["Login", "Sign Up"])

        if option == "Login":
            login_user()
        elif option == "Sign Up":
            sign_up()
            st.session_state.redirect_to_login = False

    else:
        # User is logged in, show chat interface
        username = st.session_state['username']
        st.title("Gemini Chatbot")

        # Initialize `messages` and `current_chat_file`
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_chat_file" not in st.session_state:
            st.session_state.current_chat_file = None

        st.sidebar.write("Logged in as: " + username)

        # Load selected chat history if any
        chat_files = list_chat_history_files(username)
        if chat_files:
            st.sidebar.subheader("Chat History")
            selected_chat = st.sidebar.selectbox("Select a Chat", chat_files, key='chat_files', help="Click to select a chat history.")
            if selected_chat:
                st.session_state.messages = load_session_messages(selected_chat)
                st.session_state.current_chat_file = selected_chat


        # New Chat button
        new_chat_button = st.sidebar.button('New Chat', key='new_chat')
        if new_chat_button:
            start_new_chat(username)  # Start a new chat session

        logout_placeholder = st.empty()

        # Logout button in the footer of the sidebar
        st.sidebar.markdown("---")  # Separator
        logout_button = st.sidebar.button('Logout', key='logout')
        
        if logout_button:
            logout_placeholder.text("Logging out... Please wait.")
            logout()

        # Handle user input
        user_input = st.chat_input("Chat Gemini: ")

        if user_input:
            # Append the new user message to the list
            st.session_state.messages.append({"role": "user", "content": user_input})

            max_messages = 10  # You can adjust this number
            message_log = str(st.session_state.messages[-max_messages:])
            response = get_gemini_res(user_input, prompt, message_log, log)

            st.session_state.messages.append({"role": "assistant", "content": response})

            # Save updated messages to the current chat file
            if st.session_state.current_chat_file:
                save_session_messages(username, st.session_state.messages, st.session_state.current_chat_file)

        # Display messages
        for message in st.session_state.messages:
            with st.container():
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])



if __name__ == "__main__":
    main()
