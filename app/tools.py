"""
Tools - Database operations and Email functionality
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from db.database import get_connection
from app.config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD

def save_booking(data):
    """
    Save booking to database.
    
    Args:
        data: dict with keys: name, email, phone, booking_type, date, time
    
    Returns:
        tuple: (success: bool, booking_id: int or None, error_message: str or None)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Insert customer
        cur.execute(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            (data["name"], data["email"], data["phone"])
        )
        customer_id = cur.lastrowid

        # Insert booking
        cur.execute(
            """INSERT INTO bookings 
            (customer_id, booking_type, date, time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (customer_id, data["booking_type"], data["date"], data["time"], 
             "CONFIRMED", datetime.now().isoformat())
        )
        booking_id = cur.lastrowid
        
        conn.commit()
        conn.close()

        return True, booking_id, None
        
    except Exception as e:
        return False, None, str(e)

def get_booking_by_id(booking_id):
    """Retrieve a booking by ID"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, c.name, c.email, c.phone, b.booking_type, b.date, b.time, b.status, b.created_at
            FROM bookings b 
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.id = ?
        """, (booking_id,))
        result = cur.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "email": result[2],
                "phone": result[3],
                "booking_type": result[4],
                "date": result[5],
                "time": result[6],
                "status": result[7],
                "created_at": result[8]
            }
        return None
    except Exception as e:
        print(f"Error retrieving booking: {e}")
        return None

def get_bookings_by_email(email):
    """Retrieve all bookings for an email"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT b.id, c.name, c.email, c.phone, b.booking_type, b.date, b.time, b.status, b.created_at
            FROM bookings b 
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE c.email = ?
            ORDER BY b.created_at DESC
        """, (email,))
        results = cur.fetchall()
        conn.close()
        
        bookings = []
        for result in results:
            bookings.append({
                "id": result[0],
                "name": result[1],
                "email": result[2],
                "phone": result[3],
                "booking_type": result[4],
                "date": result[5],
                "time": result[6],
                "status": result[7],
                "created_at": result[8]
            })
        return bookings
    except Exception as e:
        print(f"Error retrieving bookings: {e}")
        return []

def send_email(to_email, subject, body):
    """
    Send email using SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (HTML supported)
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "Email not configured. SMTP credentials missing."
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        
        # Create HTML version
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        
        return True, None
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please check SMTP credentials."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Email error: {str(e)}"

def send_booking_confirmation(booking_data, booking_id):
    """
    Send booking confirmation email.
    
    Args:
        booking_data: dict with booking details
        booking_id: The booking ID
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    subject = f"Booking Confirmation - #{booking_id} | HealthCare Plus"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c5282;">✅ Booking Confirmed!</h2>
            
            <p>Dear <strong>{booking_data['name']}</strong>,</p>
            
            <p>Thank you for booking with <strong>HealthCare Plus</strong>. Your appointment has been confirmed.</p>
            
            <div style="background: #f7fafc; border-left: 4px solid #4299e1; padding: 15px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c5282;">Booking Details</h3>
                <table style="width: 100%;">
                    <tr>
                        <td style="padding: 5px 0;"><strong>Booking ID:</strong></td>
                        <td>#{booking_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Name:</strong></td>
                        <td>{booking_data['name']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Appointment Type:</strong></td>
                        <td>{booking_data['booking_type']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Date:</strong></td>
                        <td>{booking_data['date']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Time:</strong></td>
                        <td>{booking_data['time']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px 0;"><strong>Phone:</strong></td>
                        <td>{booking_data['phone']}</td>
                    </tr>
                </table>
            </div>
            
            <p><strong>Important:</strong> Please arrive 10 minutes before your scheduled appointment time.</p>
            
            <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
            
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
            
            <p style="color: #718096; font-size: 12px;">
                This is an automated message from HealthCare Plus Booking System.<br>
                Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    return send_email(booking_data['email'], subject, body)

def process_booking(booking_data):
    """
    Complete booking process: save to DB and send email.
    
    Args:
        booking_data: dict with booking details
    
    Returns:
        dict: Result with booking_id, db_success, email_success, messages
    """
    result = {
        "booking_id": None,
        "db_success": False,
        "email_success": False,
        "db_message": None,
        "email_message": None
    }
    
    # Save to database
    db_success, booking_id, db_error = save_booking(booking_data)
    result["db_success"] = db_success
    result["booking_id"] = booking_id
    
    if not db_success:
        result["db_message"] = f"Failed to save booking: {db_error}"
        return result
    
    result["db_message"] = "Booking saved successfully"
    
    # Send confirmation email
    email_success, email_error = send_booking_confirmation(booking_data, booking_id)
    result["email_success"] = email_success
    
    if email_success:
        result["email_message"] = "Confirmation email sent"
    else:
        result["email_message"] = f"Email could not be sent: {email_error}"
    
    return result
