import streamlit as st
import requests
from http import HTTPStatus
import os
import io
import base64
from io import BytesIO
from PIL import Image

# Set page layout
st.set_page_config(layout="wide")

def display_qa_interface():
    
    st.title("Chatbot")
    st.session_state['page'] = 'qainterface'

    # Retrieve session state values
    document_id = st.session_state.get('selected_doc_id')
    auth_token = st.session_state.get('token', None)

    # Ensure that a document is selected and a token is available
    if document_id is None:
        st.warning("Please select a document from the Document Explorer.")
        return
    if auth_token is None:
        st.warning("Authorization token is missing. Please log in again.")
        return
    
    # Clear chat history if a new document is selected
    if st.session_state.get('previous_doc_id') != document_id:
        st.session_state['messages'] = []  # Clear chat messages
        st.session_state['previous_doc_id'] = document_id
    
    # Prompt type and source selection
    st.sidebar.header("Chat Settings")
    prompt_type = st.sidebar.selectbox("Select Prompt Type", ["report", "text"], key="selected_prompt_type")
    source = st.sidebar.selectbox("Select Source", ["Document", "Research notes"], key="selected_source")

    # Persistent message history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages with images if present
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display images if available for this message
            if "image_content" in message:
                for idx, img_data in enumerate(message["image_content"]):
                    image_bytes = base64.b64decode(img_data.encode("utf-8"))
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=f"Image {idx + 1}", use_column_width=True)

    # Collect user input
    user_question = st.chat_input("Ask something:")
    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        # Retrieve response
        selected_prompt_type = "report" if prompt_type == "report" else "default"
        selected_source = "full_text" if source == "Document" else "report"

        data = {
            "question": user_question,
            "prompt_type": selected_prompt_type,
            "source": selected_source
        }
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        # Call API to get LLM response
        response = requests.post(
            f"http://{os.getenv('HOSTNAME')}:8000/chatbot/{document_id}",
            json=data,
            headers=headers
        )

        if response.status_code == HTTPStatus.OK:
            response_data = response.json()

            # Create assistant message structure
            assistant_message = {"role": "assistant", "content": response_data['message']['llm_response']}
            full_response = assistant_message["content"]

            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.markdown(full_response)

                # Trust Score
                if prompt_type == 'report':
                    trust_score = response_data['message'].get('trust_score', "N/A")
                    assistant_message["content"] += f"\n\n**Trust Score:** {trust_score}"
                    response_placeholder.markdown(f"**Trust Score:** {trust_score}")

                # Display and save images if available
                image_content = response_data['message'].get('image_content', [])
                if image_content:
                    assistant_message["image_content"] = image_content  # Attach images to the message
                    for idx, img_data in enumerate(image_content):
                        image_bytes = base64.b64decode(img_data.encode("utf-8"))
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, caption=f"Image {idx + 1}", use_column_width=True)

            # FIXED: Append assistant message with any images to session state to avoid losing images on refresh
            st.session_state.messages.append(assistant_message)
                
        else:
            st.error("Error fetching response. Please try again.")

if __name__ == "__main__":
    display_qa_interface()
