FIELDS = ["name", "email", "phone", "booking_type", "date", "time"]

def missing_fields(state):
    return [f for f in FIELDS if f not in state]

def summarize(state):
    return f"""
    Please confirm:
    Name: {state['name']}
    Email: {state['email']}
    Phone: {state['phone']}
    Type: {state['booking_type']}
    Date: {state['date']}
    Time: {state['time']}
    """
