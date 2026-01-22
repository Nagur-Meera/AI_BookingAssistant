import streamlit as st
from db.models import create_tables
from app.admin_dashboard import admin_ui

create_tables()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat", "Admin"])

if page == "Admin":
    admin_ui()
else:
    st.title("🤖 AI Booking Assistant")
    st.chat_input("Ask me anything...")
