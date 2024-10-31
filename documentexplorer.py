import streamlit as st
import requests
from http import HTTPStatus
import os
from overview import display_overview_page

# Function to display the Document Explorer page
def display_document_explorer():
    st.title("Document Explorer")

    # Back button to return to the home (login) page
    if st.button("Logout", key="logout_top"):
        if 'token' in st.session_state:
            del st.session_state['token']
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'overview'
        st.success("Logged out successfully!")
        return  # Exit function to avoid further execution

    auth_token = st.session_state.get('token', None)

    if st.button("Fetch Documents", key="fetch_documents"):
        # Simulate document fetching without backend
        st.success("Simulated fetch documents successfully!")

        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Fetch documents from the backend
        response = requests.get(f"http://{os.getenv('HOSTNAME')}:8000/exploredocs?count=5", headers=headers)
        response_data = response.json()

        if response.status_code == HTTPStatus.OK and 'message' in response_data:
            documents_list = response_data['message']
            documents_dict = {item['question']: item['document_id'] for item in documents_list}
            st.session_state['documents'] = list(documents_dict.keys())
            st.session_state['documents_dict'] = documents_dict
        else:
            st.error("Failed to fetch documents from the server.")

    # Check if documents are available in session_state
    if 'documents' in st.session_state:
        documents = st.session_state['documents']
        documents_dict = st.session_state['documents_dict']

        # Display the fetched documents in a selectbox
        selected_document = st.selectbox("Select a document:", documents)

        # Store the selected document in session_state
        if selected_document:
            st.session_state['selected_document'] = selected_document
            st.session_state['document_id'] = documents_dict[selected_document]

    # Check if a document has been selected
    if 'selected_document' in st.session_state:
        document_id = st.session_state['document_id']

        # Load Data button after document selection
        if st.button("Load Document", key="load_document"):
            # Simulate loading data without backend
            st.success("Simulated data load successfully!")

            url = f"http://{os.getenv('HOSTNAME')}:8000"
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            # Fetch the data for the selected document using the task ID
            load_response = requests.get(f"{url}/load_docs/{document_id}", headers=headers)
            load_docs = load_response.json()
            
            if load_response.status_code == HTTPStatus.OK and 'message' in load_docs:
                document_id = load_docs['message'].get('document_id', 'Unknown ID')
                title = load_docs['message'].get('title', 'Untitled Document')
                image_url = load_docs['message'].get('image', '')

                # Display document details
                st.text_input("Document ID", value=document_id, key="document_id_display", disabled=True)
                st.text_input("Title", value=title, key="title", disabled=True)

                # Display image if available
                if image_url:
                    st.image(image_url, caption="Document Image", use_column_width=True)
                else:
                    st.warning("No image available for this document.")
            else:
                st.error("Failed to load document data.")

# Code for main application logic and navigation
st.sidebar.title("Navigation")
nav_option = st.sidebar.radio(
    "Choose a page:",
    ('Overview', 'Document Explorer', 'Summary Generation', 'QA Interface', 'Report')
)

if nav_option == 'Overview':
    st.session_state['page'] = 'overview'
elif nav_option == 'Document Explorer':
    st.session_state['page'] = 'documentexplorer'
elif nav_option == 'Summary Generation':
    st.session_state['page'] = 'summarygeneration'
elif nav_option == 'QA Interface':
    st.session_state['page'] = 'qainterface'    
elif nav_option == 'Report':
    st.session_state['page'] = 'report' 
       
# Display the selected page based on session state
if st.session_state.get('page') == 'documentexplorer':
    display_document_explorer()
elif st.session_state.get('page') == 'overview':
    display_overview_page()
# elif other pages as needed...
