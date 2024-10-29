import streamlit as st

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

# Navigation Section
st.header("Explore the App")
st.markdown("Select one of the following sections to get started:")

# Navigation Buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Document Explorer"):
        st.write("Navigate to Document Explorer section.")
        # Here you can use st.experimental_rerun() or some other method to load the section
        # when other pages are implemented.

with col2:
    if st.button("Summaries"):
        st.write("Navigate to Summaries section.")
        
with col3:
    if st.button("Q/A Interface"):
        st.write("Navigate to Q/A Interface section.")
        
with col4:
    if st.button("Research Notes"):
        st.write("Navigate to Research Notes section.")

# Additional Info or Footer (Optional)
st.markdown("---")
st.markdown("**Note:** This app uses advanced machine learning techniques for document exploration and Q/A capabilities, powered by NVIDIA's multimodal RAG.")

