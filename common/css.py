import streamlit as st

def apply_css():
    st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-left: 5rem;
            padding-right: 5rem;
            max-width: 100% !important;
        }
        h1 {
            text-align: left !important;
        }
    </style>
    """, unsafe_allow_html=True)