import os
import smtplib
import psycopg2
from email.message import EmailMessage
from dates import today

def send_file(full_name, email_pass, sender, recipient, content_path):
    first_name = full_name.split("_")[0]
    last_name = full_name.split("_")[1]
    conn = psycopg2.connect(os.getenv("DB_CONN"))
    curr = conn.cursor() 
    me = sender
    you = recipient  # Recipient's email address

    # Read the contents of your text file
    with open(content_path) as fp:
        file_content = fp.read()

    # Wrap the content in basic responsive HTML
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 10px;
                margin: 0;
                line-height: 1.6;
            }}
            .content {{
                max-width: 600px;
                margin: auto;
                padding: 20px;
                background-color: #f4f4f4;
                border-radius: 10px;
            }}
            h1 {{
                font-size: 24px;
            }}
            p {{
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="content">
            {file_content}
        </div>
    </body>
    </html>
    """

    # Create the email message object
    msg = EmailMessage()
    msg['Subject'] = 'The Tutors: Outstanding Balance'
    msg['From'] = me
    msg['To'] = you

    # Add the HTML content to the email
    msg.add_alternative(html_content, subtype='html')

    # Gmail SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Port for starttls
    gmail_password = email_pass

    # Send the message via Gmail SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as s:
        s.starttls()  # Secure the connection
        s.login(me, gmail_password)  # Login with your Gmail credentials
        s.send_message(msg)  # Send the email
        curr.execute("""UPDATE clients SET datereminded = %s WHERE firstname = %s AND lastname = %s;""", (today,first_name,last_name,)) #
        s.quit()  # Close the connection

