import hashlib
import streamlit as st
from storage import load_users, save_users

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_ui():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and users[username] == hash_password(password):
            st.session_state.user = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

def signup_ui():
    st.subheader("🆕 Create Account")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")

    if st.button("Signup"):
        users = load_users()
        if username in users:
            st.error("User already exists")
            return
        users[username] = hash_password(password)
        save_users(users)
        st.success("Account created. Please login.")

def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
