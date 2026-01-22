def is_booking_intent(text):
    keywords = ["book", "appointment", "schedule", "doctor"]
    return any(k in text.lower() for k in keywords)
