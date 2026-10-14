# theme.py
import streamlit as st

def apply_theme():
    st.markdown(
        """
        <style>
        /* --- MAIN BACKGROUND --- */
        .main {
            background: #0f172a !important;  /* dark blue-grey */
            color: #e2e8f0;
        }

        /* --- SIDEBAR --- */
        section[data-testid="stSidebar"] {
            background: #1e293b !important;
            border-right: 1px solid #334155;
        }

        section[data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
            font-weight: 500 !important;
        }

        /* --- HEADER TEXT --- */
        h1, h2, h3 {
            color: #f8fafc !important;
            font-weight: 700 !important;
        }

        /* --- METRICS CARDS --- */
        div[data-testid="metric-container"] {
            background-color: #1e293b !important;
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid #334155;
        }

        /* --- BUTTONS --- */
        button[kind="primary"] {
            border-radius: 8px !important;
            padding: 0.5rem 1.2rem !important;
            font-weight: 600 !important;
            border: 0 !important;
            background: linear-gradient(90deg, #22c55e, #16a34a) !important;
            color: white !important;
        }

        /* Hover effect */
        button[kind="primary"]:hover {
            background: linear-gradient(90deg, #16a34a, #15803d) !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
