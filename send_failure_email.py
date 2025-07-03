"""
Purpose  : Sends an email to human in case there is a failure in validating against UIDAI database
@author  : Karthikeyan V
Comments : As the code wants to send email from an application, SMTP_USER
and SMTP_PASS is stored in an .env file. this code uses Gmail SMTP
"""


import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def send_failure_email(to_email: str, name: str, aadhaar: str, phone: str, reason: str):
    """
    Send a simple failure notification email.

    Args:
        to_email: Recipient email address.
        name: Customer name.
        aadhaar: Aadhaar number.
        phone: Customer phone number.
        reason: Reason for failure.
    """
    subject = f"eKYC Validation Failure for {name}"
    body = f"""
    Dear Operator,

    The eKYC validation for the following customer has FAILED:

    Name: {name}
    Aadhaar: {aadhaar}
    Reason: {reason}
    Phone: {phone}

    Please review manually.

    Regards,
    eKYC Agent System
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    # ✅ For quick local test — FIXED: add 'phone'
    send_failure_email(
        to_email="jaidev.karthikeyan@gmail.com",
        name="V Karthikeyan",
        aadhaar="XXXXXXXXX",
        phone="1111111111",  
        reason="Name or DOB mismatch"
    )
