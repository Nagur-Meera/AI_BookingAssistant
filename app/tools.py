from db.database import get_connection

def save_booking(data):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO customers (name,email,phone) VALUES (?,?,?)",
        (data["name"], data["email"], data["phone"])
    )
    customer_id = cur.lastrowid

    cur.execute(
        """INSERT INTO bookings 
        (customer_id, booking_type, date, time, status)
        VALUES (?,?,?,?,?)""",
        (customer_id, data["booking_type"], data["date"], data["time"], "CONFIRMED")
    )

    booking_id = cur.lastrowid
    conn.commit()
    conn.close()

    return booking_id

def send_email(to_email, body):
    try:
        # Dummy for assignment
        print("Email sent to", to_email)
        return True
    except:
        return False
