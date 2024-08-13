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

def generateTxt(destination, sortedNames, billing): # pretty write billing to a .txt
    with open(rf"{destination}\email.txt", "w") as file:
        file.write(f"TOTAL - {getTotalOwed(billing=billing)}\n")
        for name in sortedNames: 
            file.write("\n")
            file.write(name.replace("_", " ") + "\n")
            for sessionOwePair in billing[name]:
                file.write(sessionOwePair[0] + " " + sessionOwePair[1] + "\n")
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
    billing = {}
    for row in rows:
        fullName = row[0] + "_"  + row[1]
        indebted_sessions_list = ast.literal_eval("[" + row[6] + "]")
        billing[fullName] = indebted_sessions_list
    
    sortedNames = sortBillingKeys(billing=billing)
    total = getTotalOwed(billing)
    content_path  = generateTxt(destination=get_download_directory(), sortedNames=sortedNames, billing=billing)
    recepients = [] # TO DO - READ IN ENV VARS AS LIST
    recepients.append(os.getenv("GMAIL_RECEPIENT_1"))
    recepients.append(os.getenv("GMAIL_RECEPIENT_2"))
    recepients.append(os.getenv("GMAIL_RECEPIENT_3"))
    email_pass = os.getenv("GMAIL_PASS")
    sender = os.getenv("GMAIL_SEND_ADDRESS")
    send_file(email_pass=email_pass, sender=sender, recepients=recepients, content_path=content_path)


if __name__ == "__main__":
    read_and_send_debt_data()