import os
import smtplib
from email.message import EmailMessage

def send_file(email_pass, sender, recepient, content_path):
    me = sender
    you = recepient  # Recipient's email address

    # Read the contents of your text file
    with open(content_path) as fp:
        file_content = fp.read()

    # Create the email message object
    msg = EmailMessage()
    msg['Subject'] = 'Tutors Billing'
    msg['From'] = me
    msg['To'] = you

    # Add the HTML content to the email
    msg.add_alternative(file_content, subtype='html')

    # Gmail SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Port for starttls
    gmail_password = email_pass

    # Send the message via Gmail SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as s:
        s.starttls()  # Secure the connection
        s.login(me, gmail_password)  # Login with your Gmail credentials
        s.send_message(msg)  # Send the email
        s.quit()  # Close the connection

