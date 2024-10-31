import streamlit as st
import requests
from http import HTTPStatus
import os
from dotenv import load_dotenv

load_dotenv()

def register(first_name, last_name, email, phone, password):
    data = { 
        'first_name': first_name,
        'last_name': last_name, 
        'phone': phone,
        'email': email, 
        'password': password
    }
    response = requests.post('http://127.0.0.1:8000/register', json=data)  
    return response.json()

def display_register_page():
    st.title("Register Page")

    first_name = st.text_input("First Name", key="register_first_name")
    last_name = st.text_input("Last Name", key="register_last_name")
    email = st.text_input("Email", key="register_email")
    phone = st.text_input("Phone", key="register_phone")
    password = st.text_input("Password", type="password", key="register_password")
    
    if st.button("SignUp"):
        # Commenting out the actual registration call for testing purposes
        # response = register(first_name, last_name, email, phone, password)
        # print(response)  # For debugging purposes
        
        # Directly navigate to the document explorer page for testing
        st.session_state["logged_in"] = True  # Assuming you want to simulate a logged-in state
        st.session_state['page'] = 'documentexplorer'  # Navigate to the document explorer page
        
        # Optionally display a message indicating navigation for testing purposes
        st.success("Navigating to the document explorer...")

