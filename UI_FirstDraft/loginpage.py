import streamlit as st
import requests

# FastAPI server URL
API_URL = "http://127.0.0.1:8000"  # Update if your FastAPI server is running on a different port or address

# Function to register a new user
def register_user(first_name, last_name, phone, email, password):
    response = requests.post(f"{API_URL}/register", json={
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "email": email,
        "password": password
    })
    return response

# Function to login a user
def login_user(email, password):
    response = requests.post(f"{API_URL}/login", json={
        "email": email,
        "password": password
    })
    return response

# Streamlit UI
st.title("User Registration and Login")

# Tabs for Registration and Login
tab1, tab2 = st.tabs(["Register", "Login"])

# Registration Tab
with tab1:
    st.header("Register a New User")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    
    if st.button("Register"):
        if first_name and last_name and phone and email and password:
            response = register_user(first_name, last_name, phone, email, password)
            if response.status_code == 200:
                st.success("Registration successful!")
            else:
                st.error(response.json().get("message", "Registration failed."))
        else:
            st.warning("Please fill in all fields.")

# Login Tab
with tab2:
    st.header("Login")
    email = st.text_input("Email Address (for Login)")
    password = st.text_input("Password (for Login)", type="password")
    
    if st.button("Login"):
        if email and password:
            response = login_user(email, password)
            if response.status_code == 200:
                st.success("Login successful!")
                st.json(response.json())  # Display the response from the server
            else:
                st.error(response.json().get("message", "Login failed."))
        else:
            st.warning("Please enter your email and password.")
