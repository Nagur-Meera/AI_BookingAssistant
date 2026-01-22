"""
Booking Flow Manager - Handles multi-turn booking conversation
"""
from app.chat_logic import (
    BOOKING_FIELDS, get_missing_fields, format_booking_summary,
    get_field_prompt, extract_email, extract_phone, extract_date,
    extract_time, extract_booking_type, extract_name,
    validate_email, validate_phone, validate_date, validate_time,
    is_confirmation, is_rejection
)

class BookingFlow:
    """Manages the booking conversation flow"""
    
    def __init__(self, session_state):
        self.session = session_state
        self._init_booking_state()
    
    def _init_booking_state(self):
        """Initialize booking state in session"""
        if "booking_state" not in self.session:
            self.session.booking_state = {}
        if "booking_active" not in self.session:
            self.session.booking_active = False
        if "awaiting_confirmation" not in self.session:
            self.session.awaiting_confirmation = False
        if "current_field" not in self.session:
            self.session.current_field = None
    
    def start_booking(self):
        """Start a new booking flow"""
        self.session.booking_state = {}
        self.session.booking_active = True
        self.session.awaiting_confirmation = False
        self.session.current_field = None
    
    def reset_booking(self):
        """Reset booking state"""
        self.session.booking_state = {}
        self.session.booking_active = False
        self.session.awaiting_confirmation = False
        self.session.current_field = None
    
    def is_active(self):
        """Check if booking flow is active"""
        return self.session.booking_active
    
    def is_awaiting_confirmation(self):
        """Check if waiting for user confirmation"""
        return self.session.awaiting_confirmation
    
    def get_state(self):
        """Get current booking state"""
        return self.session.booking_state
    
    def update_field(self, field, value):
        """Update a booking field"""
        self.session.booking_state[field] = value
    
    def process_input(self, user_input):
        """
        Process user input during booking flow.
        Returns (response_message, booking_complete, booking_data)
        """
        state = self.session.booking_state
        
        # Check if we're waiting for confirmation
        if self.session.awaiting_confirmation:
            if is_confirmation(user_input):
                # User confirmed - return booking data for saving
                self.session.awaiting_confirmation = False
                return None, True, dict(state)
            elif is_rejection(user_input):
                # User wants to modify
                self.session.awaiting_confirmation = False
                return "No problem! What would you like to change? You can tell me the field (name, email, phone, appointment type, date, or time) and the new value.", False, None
            else:
                return "I didn't quite understand. Please say **'yes'** to confirm the booking or tell me what you'd like to change.", False, None
        
        # Try to extract information based on current field being asked
        current_field = self.session.current_field
        extracted = False
        validation_error = None
        
        if current_field == "name":
            name = extract_name(user_input, state)
            if name:
                state["name"] = name
                extracted = True
            else:
                validation_error = "Please provide a valid name (letters only)."
        
        elif current_field == "email":
            email = extract_email(user_input)
            if email:
                if validate_email(email):
                    state["email"] = email
                    extracted = True
                else:
                    validation_error = "That doesn't look like a valid email address. Please try again (e.g., example@email.com)."
            else:
                validation_error = "I couldn't find an email address in your response. Please provide a valid email."
        
        elif current_field == "phone":
            phone = extract_phone(user_input)
            if phone:
                state["phone"] = phone
                extracted = True
            else:
                validation_error = "Please provide a valid phone number (10+ digits)."
        
        elif current_field == "booking_type":
            booking_type = extract_booking_type(user_input)
            if booking_type:
                state["booking_type"] = booking_type
                extracted = True
            else:
                validation_error = "I couldn't identify the appointment type. Please choose from: General Consultation, Specialist Appointment, Follow-up Visit, Emergency Consultation, or Health Checkup."
        
        elif current_field == "date":
            date = extract_date(user_input)
            if date:
                state["date"] = date
                extracted = True
            else:
                validation_error = "Please provide a valid future date in YYYY-MM-DD format (e.g., 2026-01-25)."
        
        elif current_field == "time":
            time = extract_time(user_input)
            if time:
                state["time"] = time
                extracted = True
            else:
                validation_error = "Please provide a valid time in HH:MM format (e.g., 14:30 for 2:30 PM)."
        
        else:
            # Try to extract any field from the input
            email = extract_email(user_input)
            if email and validate_email(email):
                state["email"] = email
                extracted = True
            
            phone = extract_phone(user_input)
            if phone:
                state["phone"] = phone
                extracted = True
            
            date = extract_date(user_input)
            if date:
                state["date"] = date
                extracted = True
            
            time = extract_time(user_input)
            if time:
                state["time"] = time
                extracted = True
            
            booking_type = extract_booking_type(user_input)
            if booking_type:
                state["booking_type"] = booking_type
                extracted = True
        
        # Return validation error if any
        if validation_error:
            return validation_error, False, None
        
        # Check for missing fields
        missing = get_missing_fields(state)
        
        if not missing:
            # All fields collected - ask for confirmation
            self.session.awaiting_confirmation = True
            self.session.current_field = None
            summary = format_booking_summary(state)
            return summary, False, None
        else:
            # Ask for next missing field
            next_field = missing[0]
            self.session.current_field = next_field
            prompt = get_field_prompt(next_field)
            return prompt, False, None
    
    def get_initial_prompt(self):
        """Get the first prompt to start booking"""
        missing = get_missing_fields(self.session.booking_state)
        if missing:
            next_field = missing[0]
            self.session.current_field = next_field
            return f"Great! I'd be happy to help you book an appointment. {get_field_prompt(next_field)}"
        return None
