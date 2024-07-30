import smtplib
from email.message import EmailMessage
from process import process_billing_csv
from dates import today
from credentials import gmail_pass, gmail_recepients, gmail_send_address

mostRecentData = process_billing_csv()
textfile = rf"C:\Users\Jacob\Desktop\TutorsBilling\{mostRecentData}" 
me = gmail_send_address

for recipient in gmail_recepients:
    you = recipient  # Recipient's email address

    # Read the contents of your text file
    with open(textfile) as fp:
        msg = EmailMessage()
        msg.set_content(fp.read())

    msg['Subject'] = f'Tutors Billing {today}'
    msg['From'] = me
    msg['To'] = you

    # Gmail SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Port for starttls
    gmail_password = gmail_pass

    # Send the message via Gmail SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as s:
        s.starttls()  # Secure the connection
        s.login(me, gmail_password)  # Login with your Gmail credentials
        s.send_message(msg)  # Send the email
        s.quit()  # Close the connection
