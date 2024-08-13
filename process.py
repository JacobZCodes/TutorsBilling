import dates
from dates import convert_comma_date_to_slash_date, is_past_today
import os
from download import get_download_directory
import json
from send_file import send_file
import psycopg2
import ast

def createBillingDict(df):
    billing = {}
    for index, row in df.iterrows():
        fullName = row['Last Name'] + " " + row['First Name']
        amountOwed = str(row['Appointment Price'])
        sessionDate = dates.convert_comma_date_to_slash_date(row['Start Time'].split()[0] + " " + row['Start Time'].split()[1] + row['Start Time'].split()[2])
        if (fullName not in billing.keys()):
            billing[fullName] = [[sessionDate, amountOwed]]
        else:
            billing[fullName].append([sessionDate, amountOwed])
    return billing

def getTotalOwed(billing):
    total = 0.0
    for value in billing.values():
        for sessionOwePair in value:
            total += float(sessionOwePair[1])
    return total

def generateTxt(destination): # pretty write billing to a .txt
    with open(rf"{destination}\email.txt", "w") as file:
        file.write(f"Hello, thank you for recently joining us at The Tutors! We hope that you have found our services helpful, and we'd appreciate
        your honest feedback on our survey; it shouldn't take more than five minutes. We look forward to meeting with you again!\n")
    return (rf"{destination}\email.txt")

# Alphabetically
def sortBillingKeys(billing):
    tempList = []
    for key in billing.keys():
        tempList.append(key)
    sortedNames = sorted(tempList)
    return sortedNames

# Checks at EOD every day and sends survey email
def send_survey():
    # conn = psycopg2.connect (
    # dbname= os.getenv("DB_NAME"),
    # user=os.getenv("DB_USER"),
    # password=os.getenv("DB_PASS"),
    # host=os.getenv("DB_ENDPOINT"),
    # port='5432' 
    # )
    conn = psycopg2.connect("postgresql://jacob:***REMOVED***@***REMOVED***:5432/***REMOVED***")
    curr = conn.cursor()       
    curr.execute("SELECT * FROM clients WHERE isnewclient = TRUE AND receivedsurvey = FALSE;")
    rows = curr.fetchall()
    email = {}
    for row in rows:
        email[row[0] + "_" + row[1]] = row[2] 
    # Add recepients
    recepients = [] 
    recepients.append(os.getenv("GMAIL_RECEPIENT_1"))
    recepients.append(os.getenv("GMAIL_RECEPIENT_2"))
    recepients.append(os.getenv("GMAIL_RECEPIENT_3")) # keep these for now; staff don't need to receive surveys

    email_pass = os.getenv("GMAIL_SURVEY_SENDER_PASS")
    sender = os.getenv("GMAIL_SURVEY_SENDER")
    # send_file(email_pass=email_pass, sender=sender, recepients=recepients, content_path=content_path)

    # Change receivedsurvey to TRUE
    

    conn.commit()
    curr.close()
    conn.close()


if __name__ == "__main__":
    send_survey()
    # CHANGE LOCAL VAR BACK TO HIDDEN VAR
    # PRUNE JUST FOR FARIS FOR TESTING