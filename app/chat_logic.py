import re
from datetime import datetime
from app.config import MEMORY_LIMIT, BOOKING_TYPES

# Required fields for booking
BOOKING_FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

def is_booking_intent(text):
    """Detect if user wants to book an appointment"""
    booking_keywords = [
        "book", "appointment", "schedule", "reserve", "booking",
        "want to see", "need to see", "visit", "consultation",
        "available", "slot", "time slot", "doctor", "checkup"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in booking_keywords)

def is_confirmation(text):
    """Check if user is confirming the booking"""
    confirm_words = ["yes", "confirm", "correct", "that's right", "looks good", "proceed", "go ahead", "book it"]
    text_lower = text.lower().strip()
    return any(word in text_lower for word in confirm_words)

def is_rejection(text):
    """Check if user is rejecting/wants to modify"""
    reject_words = ["no", "wrong", "change", "modify", "update", "incorrect", "not right", "cancel"]
    text_lower = text.lower().strip()
    return any(word in text_lower for word in reject_words)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (basic validation)"""
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD) and ensure it's not in the past"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return date_obj >= today
    except ValueError:
        return False

def validate_time(time_str):
    """Validate time format (HH:MM)"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def extract_email(text):
    """Extract email from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def extract_phone(text):
    """Extract phone number from text"""
    patterns = [
        r'\+?[\d\s\-\(\)\.]{10,}',
        r'\d{3}[\s\-\.]?\d{3}[\s\-\.]?\d{4}',
        r'\d{10,}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group(0).strip()
            if validate_phone(phone):
                return phone
    return None

def extract_date(text):
    """Extract date from text"""
    pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.search(pattern, text)
    if match and validate_date(match.group(0)):
        return match.group(0)
    return None

def extract_time(text):
    """Extract time from text"""
    pattern = r'\b([01]?\d|2[0-3]):([0-5]\d)\b'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    
    pattern_12 = r'\b(1[0-2]|0?[1-9]):([0-5]\d)\s*(am|pm|AM|PM)\b'
    match_12 = re.search(pattern_12, text)
    if match_12:
        hour = int(match_12.group(1))
        minute = match_12.group(2)
        period = match_12.group(3).lower()
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute}"
    
    return None

def extract_booking_type(text):
    """Extract booking type from text"""
    text_lower = text.lower()
    for booking_type in BOOKING_TYPES:
        if booking_type.lower() in text_lower:
            return booking_type
    
    type_mapping = {
        "general": "General Consultation",
        "specialist": "Specialist Appointment",
        "follow": "Follow-up Visit",
        "emergency": "Emergency Consultation",
        "checkup": "Health Checkup",
        "check-up": "Health Checkup",
        "check up": "Health Checkup"
    }
    for keyword, booking_type in type_mapping.items():
        if keyword in text_lower:
            return booking_type
    
    return None

def get_missing_fields(booking_state):
    """Get list of missing booking fields"""
    return [field for field in BOOKING_FIELDS if not booking_state.get(field)]

def format_booking_summary(booking_state):
    """Format booking details for confirmation"""
    return f"""
📋 **Booking Summary:**
- **Name:** {booking_state.get('name', 'N/A')}
- **Email:** {booking_state.get('email', 'N/A')}
- **Phone:** {booking_state.get('phone', 'N/A')}
- **Appointment Type:** {booking_state.get('booking_type', 'N/A')}
- **Date:** {booking_state.get('date', 'N/A')}
- **Time:** {booking_state.get('time', 'N/A')}

Is this information correct? Please confirm with **"yes"** or let me know what you'd like to change.
"""

def get_field_prompt(field):
    """Get prompt for missing field"""
    prompts = {
        "name": "What is your full name?",
        "email": "What is your email address?",
        "phone": "What is your phone number?",
        "booking_type": f"What type of appointment would you like?\n\nAvailable options:\n" + "\n".join([f"• {t}" for t in BOOKING_TYPES]),
        "date": "What date would you prefer? (Please use YYYY-MM-DD format, e.g., 2026-01-25)",
        "time": "What time would you prefer? (Please use HH:MM format, e.g., 14:30 for 2:30 PM)"
    }
    return prompts.get(field, f"Please provide your {field}")

def trim_memory(messages, limit=MEMORY_LIMIT):
    """Trim messages to keep only the last 'limit' messages"""
    if len(messages) > limit:
        return messages[-limit:]
    return messages

def extract_name(text, booking_state):
    """Extract name from text"""
    cleaned = text.strip()
    if 2 <= len(cleaned) <= 100 and re.match(r'^[a-zA-Z\s\.\-\']+$', cleaned):
        return cleaned
    return None
