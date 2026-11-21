import hashlib
import hmac
import os
import streamlit as st
from storage import load_users, save_users

PBKDF2_ROUNDS = 200_000


def hash_password(password, salt=None):
    """Salted PBKDF2-SHA256 hash, stored as 'pbkdf2$<salt>$<hash>'."""
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PBKDF2_ROUNDS).hex()
    return f"pbkdf2${salt}${digest}"


def verify_password(password, stored):
    if stored.startswith("pbkdf2$"):
        _, salt, _ = stored.split("$")
        return hmac.compare_digest(hash_password(password, salt), stored)
    # Older accounts were saved as plain SHA-256
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), stored)


def login_ui():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and verify_password(password, users[username]):
            st.session_state.user = username
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


def signup_ui():
    st.subheader("🆕 Create Account")
    st.caption("Demo app: please don't reuse a password you use anywhere else.")

    username = st.text_input("Choose Username")
    password = st.text_input("Choose Password", type="password")

    if st.button("Signup"):
        users = load_users()
        if not username or not password:
            st.error("Enter a username and password")
            return
        if username in users or username == "guest":
            st.error("User already exists")
            return
        users[username] = hash_password(password)
        save_users(users)
        st.success("Account created. Please login.")


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
