import streamlit as st
from db.database import get_connection

def admin_ui():
    st.title("📋 Admin Dashboard")

    conn = get_connection()
    data = conn.execute("""
    SELECT b.id, c.name, c.email, b.booking_type, b.date, b.time
    FROM bookings b JOIN customers c
    ON b.customer_id = c.customer_id
    """).fetchall()

    st.table(data)
