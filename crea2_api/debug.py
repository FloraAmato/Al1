import streamlit as st
import requests
import uuid

# Function to send POST request to the provided URL
def send_message(url, session_id, message):
    params = {
        'input': message,
        'session_id': session_id
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Function to generate a unique session ID
@st.cache_data
def generate_session_id():
    return str(uuid.uuid4())

def main():
    st.set_page_config(page_title="CREA2 dev front-end", page_icon=":robot_face:")
    st.title("CREA2 front-end for testing purposes only")

    # Sidebar options
    st.sidebar.header("Chat settings")
    api_url = st.sidebar.text_input("API URL", "http://localhost:8080/invoke")
    if st.sidebar.button("Reset conversation"):
        generate_session_id.clear()
        st.session_state.messages.clear()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat interface
    session_id = generate_session_id()
    if prompt := st.chat_input("Write a message"):
        if api_url:
            with st.spinner("Waiting for the AI to answer.."):
                response = send_message(api_url, session_id, prompt)
            if response:
                # Display user message in chat message container
                st.chat_message("user").markdown(prompt)
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    st.markdown(response['answer'])
                if response['sources']:
                    st.write("Sources used to formulate the answer:", response['sources'])
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})
            else:
                st.error("Failed to get response from the server.")
        else:
            st.warning("Please provide the API URL in the sidebar.")

if __name__ == "__main__":
    main()
