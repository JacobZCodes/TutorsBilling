import dates
from dates import convert_comma_date_to_slash_date, is_past_today
import os
from download import get_download_directory
import json
from send_file import send_file
import psycopg2
import ast


def generateTxt(destination): # pretty write billing to a .txt
    with open(rf"{destination}\email.txt", "w") as file:
        file.write("""Hello, thank you for recently joining us at The Tutors! We hope that you have found our services helpful, and we'd appreciate
        your honest feedback on our survey; it shouldn't take more than five minutes. We look forward to meeting with you again!\n""")
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
    email = {}

    # REMOVE PRUNING OF FARIS
    namesToRemove = []
    for name in email.keys():
        if name != "***REMOVED***":
            namesToRemove.append(name)
    for name in namesToRemove:
        del email[name]
    print("printing pruned emaisl...\n")
    print(email)

    # REMOVE - ADD STAFF RECEPIENTS
    recepients = [] 
    recepients.append(os.getenv("GMAIL_RECEPIENT_1"))
    # recepients.append(os.getenv("GMAIL_RECEPIENT_2"))
    # recepients.append(os.getenv("GMAIL_RECEPIENT_3")) 

    # KEEP - ADD CLIENT RECEPIENTS
    for recepient in email.keys():
        recepients.append(email[recepient])

    email_pass = os.getenv("GMAIL_SURVEY_SENDER_PASS")
    sender = os.getenv("GMAIL_SURVEY_SENDER")

    # send_file(email_pass=email_pass, sender=sender, recepients=recepients, content_path=generateTxt(get_download_directory()))

    # CHANGE RECEIVEDSURVEY TO BE TRUE
    for recepient in email.keys():
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