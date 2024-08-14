import os
import json
import psycopg2
import ast
from pathlib import Path
from send_file import send_file

def get_download_directory():
    home = Path.home()
    if os.name == 'nt':  # Windows
        return str(home / 'Downloads')
    elif os.name == 'posix':  # Linux and MacOS
        return str(home / 'Downloads')
    else:
        raise NotImplementedError(f"Unsupported OS: {os.name}")

def generateTxt(destination): # pretty write generic survey reminder as a .txt
    survey_url = "https://youtube.com/" # CHANGE ME

    # Write the email content with a hyperlink
    with open(rf"{destination}\email.txt", "w") as file:
        # file.write(f"Hello, thank you for recently joining us at The Tutors! We hope that you have found our services helpful, and we'd appreciate your honest feedback on our survey; it shouldn't take more than five minutes. We look forward to meeting with you again!\nYou can find the link to the survey <a href='{survey_url}'>here</a>.<br><br>Best,<br>Name and Name")
        file.write("10")

    return (rf"{destination}\email.txt")

# Checks at EOD every day and sends survey email
def send_survey():
    conn = psycopg2.connect (
    dbname= os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_ENDPOINT"),
    port='5432' 
    )
    curr = conn.cursor()       
    curr.execute("SELECT * FROM clients WHERE isnewclient = TRUE AND receivedsurvey = FALSE;")
    rows = curr.fetchall()
    # REMOVE SHOWING WHO IS VALID RECEPIENT
    for row in rows:
        print(row)
    # POPULATE EMAIL DICT 
    addresses = {}
    for row in rows:
        name = row[0] + "_" + row[1]
        email_address = row[2]
        addresses[name] = email_address
    # REMOVE PRUNING OF FARIS
    namesToRemove = []
    for name in addresses.keys():
        if name != "***REMOVED***":
            namesToRemove.append(name)
    for name in namesToRemove:
        del addresses[name]
    print("printing pruned emails..\n")
    print(addresses)

    # REMOVE - ADD STAFF RECEPIENTS FOR TESTING
    recepients = []
    recepients.append(os.getenv("GMAIL_RECEPIENT_0"))

    # KEEP - ADD CLIENT RECEPIENTS
    for recepient in addresses.keys():
        recepients.append(addresses[recepient])

    # REMOVE - SHOW RECEPIENTS
    print("Recepients:")
    for recepient in recepients:
        print(recepient)
    
    email_pass = os.getenv("GMAIL_SURVEY_SENDER_PASS")
    sender = os.getenv("GMAIL_SURVEY_SENDER")

    send_file(email_pass=email_pass, sender=sender, recepients=recepients, content_path=generateTxt(get_download_directory()))

    # CHANGE RECEIVEDSURVEY TO BE TRUE
    for recepient in addresses.keys():
        firstName = recepient.split("_")[0]
        lastName = recepient.split("_")[1]
        curr.execute(f"""
        UPDATE clients
        SET receivedsurvey = TRUE
        WHERE firstName = %s AND lastName = %s;
        """, (firstName, lastName))
    conn.commit()
    curr.close()
    conn.close()


if __name__ == "__main__":
    send_survey()