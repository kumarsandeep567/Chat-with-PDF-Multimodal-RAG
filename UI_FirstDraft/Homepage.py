import streamlit as st
import logging
import os

# Create a logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging to write to a file
logging.basicConfig(
    filename='logs/app.log',  # Log file path
    filemode='a',  # Append mode
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up page configuration
st.set_page_config(
    page_title="Document Exploration App",
    page_icon="📄",
    layout="centered"
)

# Home Page Title
st.title("📄 Document Exploration and Analysis App")

# Introduction/Welcome Message
st.markdown("""
Welcome to the Document Exploration and Analysis App! This tool is designed to help users
explore research documents, generate on-the-fly summaries, interact with document content
through question-answering (Q/A) capabilities, and store research notes.

Our goal is to provide an efficient and intuitive interface for exploring and analyzing research publications.
""")

# Login Section
st.header("User Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Check login credentials
if st.button("Login"):
    if username == "admin" and password == "password":  # Replace with your actual authentication logic
        st.success("Logged in successfully!")

        # Log successful login
        logger.info(f"User '{username}' logged in successfully.")

        # Set session state to indicate the user is logged in
        st.session_state['logged_in'] = True
        st.session_state['page'] = "Home"  # Default to home after login

        # Display navigation links after successful login
        st.header("Explore the App")
        st.markdown("Select one of the following sections to get started:")

        # Navigation Buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("Document Explorer"):
                st.session_state.page = "DocumentExplorer"  # Set the session state to load Document Explorer page
                logger.info("Navigated to Document Explorer page.")
                st.experimental_rerun()  # Rerun the app to load the selected page

        with col2:
            if st.button("Summaries"):
                st.session_state.page = "DocumentSummary"  # Set session state for summary page
                logger.info("Navigated to Document Summary page.")
                st.experimental_rerun()  # Rerun the app to load the selected page

        with col3:
            if st.button("Q/A Interface"):
                st.session_state.page = "QAInterface"  # Set session state for Q/A interface page
                logger.info("Navigated to Q/A Interface page.")
                st.experimental_rerun()  # Rerun the app to load the selected page

        with col4:
            if st.button("Research Notes"):
                st.session_state.page = "ResearchNotes"  # Set session state for research notes page
                logger.info("Navigated to Research Notes page.")
                st.experimental_rerun()  # Rerun the app to load the selected page
    else:
        st.error("Invalid username or password. Please try again.")
        # Log failed login attempt
        logger.warning(f"Invalid login attempt for user '{username}'.")

# Display the appropriate page based on session state
if 'page' in st.session_state:
    if st.session_state['page'] == "DocumentExplorer":
        # Call the Document Explorer page function
        display_document_explorer_page()
    elif st.session_state['page'] == "DocumentSummary":
        # Call the Document Summary Generation page function
        display_document_summary_page()
    elif st.session_state['page'] == "QAInterface":
        # Call the Q/A Interface page function
        display_qa_interface_page()
    elif st.session_state['page'] == "ResearchNotes":
        # Call the Research Notes page function
        display_research_notes_page()
    elif st.session_state['page'] == "Home":
        # Keep the homepage content here (optional)
        pass

# Additional Info or Footer (Optional)
st.markdown("---")
st.markdown("**Note:** This app uses advanced machine learning techniques for document exploration and Q/A capabilities, powered by NVIDIA's multimodal RAG.")
