import streamlit as st

def display_home_page():
    
    
    st.write("""
    # 📄 Document Exploration and Analysis App

    Experience a powerful, interactive platform designed to rigorously assess OpenAI's GPT models using HuggingFace's GAIA (General AI Assistant) benchmark dataset. Our Streamlit-based application streamlines the process of evaluating GPT's performance by automatically extracting content from PDF files, processing contextual information, and comparing generated responses against annotated solution steps.""")

    st.markdown("""
    Welcome to the Document Exploration and Analysis App! This tool is designed to help users
    explore research documents, generate on-the-fly summaries, interact with document content
    through question-answering (Q/A) capabilities, and store research notes.

    Our goal is to provide an efficient and intuitive interface for exploring and analyzing research publications.
    """)
