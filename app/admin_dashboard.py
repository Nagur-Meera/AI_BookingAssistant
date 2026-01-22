"""
Admin Dashboard - View and manage bookings
"""
import streamlit as st
import pandas as pd
from db.database import get_connection

def get_all_bookings():
    """Fetch all bookings from database"""
    try:
        conn = get_connection()
        query = """
        SELECT 
            b.id as 'Booking ID',
            c.name as 'Customer Name',
            c.email as 'Email',
            c.phone as 'Phone',
            b.booking_type as 'Appointment Type',
            b.date as 'Date',
            b.time as 'Time',
            b.status as 'Status',
            b.created_at as 'Created At'
        FROM bookings b 
        JOIN customers c ON b.customer_id = c.customer_id
        ORDER BY b.created_at DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()

def update_booking_status(booking_id, new_status):
    """Update booking status"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating status: {str(e)}")
        return False

def delete_booking(booking_id):
    """Delete a booking"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Get customer_id first
        cur.execute("SELECT customer_id FROM bookings WHERE id = ?", (booking_id,))
        result = cur.fetchone()
        if result:
            customer_id = result[0]
            # Delete booking
            cur.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
            # Check if customer has other bookings
            cur.execute("SELECT COUNT(*) FROM bookings WHERE customer_id = ?", (customer_id,))
            count = cur.fetchone()[0]
            if count == 0:
                # Delete customer if no other bookings
                cur.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting booking: {str(e)}")
        return False

def admin_ui():
    """Admin Dashboard UI"""
    st.title("📋 Admin Dashboard")
    st.markdown("Manage and view all bookings")
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Get all bookings
    df = get_all_bookings()
    
    if df.empty:
        st.info("📭 No bookings found. Bookings will appear here once customers make appointments.")
        return
    
    # Statistics
    st.markdown("### 📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bookings", len(df))
    with col2:
        confirmed = len(df[df['Status'] == 'CONFIRMED'])
        st.metric("Confirmed", confirmed)
    with col3:
        cancelled = len(df[df['Status'] == 'CANCELLED'])
        st.metric("Cancelled", cancelled)
    with col4:
        completed = len(df[df['Status'] == 'COMPLETED'])
        st.metric("Completed", completed)
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔍 Filter Bookings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("Search by Name", placeholder="Enter name...")
    with col2:
        search_email = st.text_input("Search by Email", placeholder="Enter email...")
    with col3:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "CONFIRMED", "CANCELLED", "COMPLETED"]
        )
    
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input("Filter by Date", value=None)
    with col2:
        booking_type_filter = st.selectbox(
            "Filter by Appointment Type",
            ["All"] + df['Appointment Type'].unique().tolist() if not df.empty else ["All"]
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_name:
        filtered_df = filtered_df[filtered_df['Customer Name'].str.contains(search_name, case=False, na=False)]
    
    if search_email:
        filtered_df = filtered_df[filtered_df['Email'].str.contains(search_email, case=False, na=False)]
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    
    if date_filter:
        filtered_df = filtered_df[filtered_df['Date'] == str(date_filter)]
    
    if booking_type_filter != "All":
        filtered_df = filtered_df[filtered_df['Appointment Type'] == booking_type_filter]
    
    st.markdown("---")
    
    # Display bookings
    st.markdown(f"### 📅 Bookings ({len(filtered_df)} results)")
    
    if filtered_df.empty:
        st.warning("No bookings match your filters.")
    else:
        # Display as interactive table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Booking ID": st.column_config.NumberColumn("ID", width="small"),
                "Customer Name": st.column_config.TextColumn("Name", width="medium"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Phone": st.column_config.TextColumn("Phone", width="medium"),
                "Appointment Type": st.column_config.TextColumn("Type", width="medium"),
                "Date": st.column_config.TextColumn("Date", width="small"),
                "Time": st.column_config.TextColumn("Time", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Created At": st.column_config.TextColumn("Created", width="medium"),
            }
        )
        
        # Export option
        st.markdown("---")
        st.markdown("### 📤 Export")
        
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="bookings_export.csv",
            mime="text/csv"
        )
    
    # Booking Management Section
    st.markdown("---")
    st.markdown("### ⚙️ Manage Booking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        booking_id_input = st.number_input("Booking ID", min_value=1, step=1, value=1)
    
    with col2:
        action = st.selectbox("Action", ["Update Status", "Delete Booking"])
    
    if action == "Update Status":
        new_status = st.selectbox("New Status", ["CONFIRMED", "COMPLETED", "CANCELLED"])
        if st.button("Update Status", type="primary"):
            if update_booking_status(booking_id_input, new_status):
                st.success(f"✅ Booking #{booking_id_input} status updated to {new_status}")
                st.rerun()
    else:
        st.warning("⚠️ This action cannot be undone!")
        if st.button("Delete Booking", type="primary"):
            if delete_booking(booking_id_input):
                st.success(f"✅ Booking #{booking_id_input} deleted")
                st.rerun()
