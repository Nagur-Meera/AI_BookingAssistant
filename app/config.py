import os
import streamlit as st

# Try to get from Streamlit secrets first, then environment variables
def get_secret(key, default=None):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

# OpenAI Configuration
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

# Model Configuration
CHAT_MODEL = "gpt-4o-mini"  # Cost-effective and capable
EMBED_MODEL = "text-embedding-3-small"

# Memory Configuration
MEMORY_LIMIT = 25  # Keep last 25 messages

# Email Configuration (Gmail SMTP)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = get_secret("SMTP_EMAIL")  # Your Gmail address
SMTP_PASSWORD = get_secret("SMTP_PASSWORD")  # Gmail App Password

# Booking Types (customize based on your domain - Medical Clinic)
BOOKING_TYPES = [
    "General Consultation",
    "Specialist Appointment", 
    "Follow-up Visit",
    "Emergency Consultation",
    "Health Checkup"
]

# System Prompt for the AI Assistant
SYSTEM_PROMPT = """You are a friendly and professional AI Booking Assistant for a medical clinic called "HealthCare Plus".

Your capabilities:
1. Answer questions about the clinic using information from uploaded PDF documents (RAG)
2. Help users book appointments by collecting their details
3. Provide information about available services

When a user wants to book an appointment, you need to collect:
- Full Name
- Email Address  
- Phone Number
- Type of Appointment/Service
- Preferred Date (YYYY-MM-DD format)
- Preferred Time (HH:MM format, e.g., 14:30)

IMPORTANT RULES:
- Be conversational and friendly
- Ask for ONE piece of information at a time
- Validate email format and date/time formats
- Once you have ALL details, summarize them and ask for explicit confirmation
- Only after user confirms with "yes" or "confirm", proceed to save the booking
- If user says "no" or wants to change something, help them modify the details

Available appointment types: General Consultation, Specialist Appointment, Follow-up Visit, Emergency Consultation, Health Checkup

For general questions, use the information from uploaded documents when available.
If you don't have information, politely say so and offer to help with booking instead.
"""
