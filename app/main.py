"""
AI Booking Assistant - Main Streamlit Application
A medical clinic booking assistant with RAG capabilities
"""
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
from openai import OpenAI
from db.models import create_tables
from app.admin_dashboard import admin_ui
from app.config import OPENAI_API_KEY, CHAT_MODEL, SYSTEM_PROMPT, MEMORY_LIMIT
from app.chat_logic import is_booking_intent, trim_memory
from app.booking_flow import BookingFlow
from app.rag_pipeline import ingest_pdfs, rag_query, create_rag_prompt
from app.tools import process_booking

# Page configuration
st.set_page_config(
    page_title="HealthCare Plus - AI Booking Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if "db_init" not in st.session_state:
    create_tables()
    st.session_state.db_init = True

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False

def get_openai_client():
    """Get OpenAI client"""
    if not OPENAI_API_KEY:
        return None
    return OpenAI(api_key=OPENAI_API_KEY)

def get_chat_response(client, messages, user_input, vectorstore=None):
    """Get response from OpenAI with optional RAG context"""
    try:
        # Build message history
        chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add RAG context if available
        if vectorstore:
            context = rag_query(vectorstore, user_input)
            if context:
                rag_context = f"\n\n[CONTEXT FROM DOCUMENTS]:\n{context}\n[END CONTEXT]\n\nUse the above context to help answer the user's question if relevant."
                chat_messages[0]["content"] += rag_context
        
        # Add conversation history
        for msg in messages:
            chat_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current user input
        chat_messages.append({"role": "user", "content": user_input})
        
        # Get response
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=chat_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def chat_interface():
    """Main chat interface"""
    st.title("🏥 HealthCare Plus - AI Booking Assistant")
    st.markdown("Welcome! I can help you book appointments and answer questions about our clinic.")
    
    # Check API key
    client = get_openai_client()
    if not client:
        st.error("⚠️ OpenAI API key not configured. Please add your API key to `.streamlit/secrets.toml`")
        st.code('OPENAI_API_KEY = "your-api-key-here"', language="toml")
        return
    
    # Initialize booking flow
    booking_flow = BookingFlow(st.session_state)
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.markdown("### 📄 Upload Documents (RAG)")
        uploaded_files = st.file_uploader(
            "Upload PDFs for Q&A",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload clinic documents, FAQs, or service information"
        )
        
        if uploaded_files:
            if st.button("🔄 Process PDFs", use_container_width=True):
                with st.spinner("Processing documents..."):
                    try:
                        vectorstore = ingest_pdfs(uploaded_files)
                        if vectorstore:
                            st.session_state.vectorstore = vectorstore
                            st.session_state.pdf_processed = True
                            st.success(f"✅ Processed {len(uploaded_files)} document(s)")
                        else:
                            st.error("Failed to process documents")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.pdf_processed:
            st.success("📚 Documents loaded for RAG")
        
        st.markdown("---")
        st.markdown("### 🗑️ Clear Chat")
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            booking_flow.reset_booking()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ Quick Help")
        st.markdown("""
        - Ask questions about our clinic
        - Say "book appointment" to start booking
        - Upload PDFs for document Q&A
        """)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        
        # Process the message
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = None
                
                # Check if booking flow is active
                if booking_flow.is_active():
                    # Process booking input
                    booking_response, booking_complete, booking_data = booking_flow.process_input(prompt)
                    
                    if booking_complete and booking_data:
                        # Save booking and send email
                        result = process_booking(booking_data)
                        
                        if result["db_success"]:
                            response = f"""
✅ **Booking Confirmed!**

Your appointment has been successfully booked.

**Booking ID:** #{result['booking_id']}
**Name:** {booking_data['name']}
**Appointment:** {booking_data['booking_type']}
**Date:** {booking_data['date']}
**Time:** {booking_data['time']}

"""
                            if result["email_success"]:
                                response += f"📧 A confirmation email has been sent to **{booking_data['email']}**."
                            else:
                                response += f"⚠️ {result['email_message']}\n\nPlease save your Booking ID for reference."
                            
                            # Reset booking flow
                            booking_flow.reset_booking()
                        else:
                            response = f"❌ Sorry, there was an error saving your booking: {result['db_message']}\n\nPlease try again."
                            booking_flow.reset_booking()
                    else:
                        response = booking_response
                
                # Check for booking intent
                elif is_booking_intent(prompt):
                    booking_flow.start_booking()
                    response = booking_flow.get_initial_prompt()
                
                # Regular chat with RAG
                else:
                    response = get_chat_response(
                        client, 
                        st.session_state.messages[:-1],  # Exclude current message
                        prompt,
                        st.session_state.vectorstore
                    )
                
                st.markdown(response)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Trim memory
        st.session_state.messages = trim_memory(st.session_state.messages, MEMORY_LIMIT)

def main():
    """Main application"""
    # Navigation
    st.sidebar.title("🏥 HealthCare Plus")
    page = st.sidebar.radio("Navigation", ["💬 Chat", "📋 Admin Dashboard"])
    
    if page == "📋 Admin Dashboard":
        admin_ui()
    else:
        chat_interface()

if __name__ == "__main__":
    main()
