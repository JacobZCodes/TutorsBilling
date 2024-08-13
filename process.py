import numpy as np
import pandas as pd
import psycopg2
import download
from CSV import findMostRecentCSV, csv_to_txt
import dates
from dates import convert_comma_date_to_slash_date, is_past_today, is_new_client
from download import download_acuity_data
import os
from download import get_download_directory
import json
from send_file import send_file

invalid_meeting_types = ['Short Meeting', 'Meeting', 'Business Meeting', 'ACT Diagnostic']
destination = get_download_directory()
download_directory = get_download_directory()

conn_string = os.getenv("DB_CONN_STRING") # remote deployment

def partial_clean_df(df): # remove people who are not getting tutored
    indices_to_drop = []
    for index, row in df.iterrows():
        curr_date = convert_comma_date_to_slash_date((row['Start Time'].split()[0] + " " + row['Start Time'].split()[1] + row['Start Time'].split()[2]))
        if row['Type'] in invalid_meeting_types: # remove people who are not getting tutored
            indices_to_drop.append(index)
        if is_past_today(curr_date, dates.today): # Acuity bug - grabs more dates than I want, so remove all rows whose dates are past today's date
            indices_to_drop.append(index)
    return df.drop(indices_to_drop)

def clean_df(df): # remove people who have already paid and who are not getting tutored
    indices_to_drop = []
    for index, row in df.iterrows():
        curr_date = convert_comma_date_to_slash_date((row['Start Time'].split()[0] + " " + row['Start Time'].split()[1] + row['Start Time'].split()[2]))
        if row['Paid?'] == 'yes': # remove people who have already paid
            indices_to_drop.append(index)
        if row['Type'] in invalid_meeting_types: # remove people who are not getting tutored
            indices_to_drop.append(index)
        if is_past_today(curr_date, dates.today): # Acuity bug - grabs more dates than I want, so remove all rows whose dates are past today's date
            indices_to_drop.append(index)
    return df.drop(indices_to_drop)


def createBillingDict(df):
    billing = {}
    for index, row in df.iterrows():
        fullName = row['First Name'] + "_" + row['Last Name']
        amountOwed = str(row['Appointment Price'])
        sessionDate = dates.convert_comma_date_to_slash_date(row['Start Time'].split()[0] + " " + row['Start Time'].split()[1] + row['Start Time'].split()[2])
        if (fullName not in billing.keys()):
            billing[fullName] = [[sessionDate, amountOwed]]
        else:
            billing[fullName].append([sessionDate, amountOwed])
    return billing

# CHANGE ME TO getTotalOwed on main func
def getTotalOwed(billing):
    total = 0.0
    for value in billing.values():
        total += value
    return total

def generateTxt(filename, destination, names, billing, total): # pretty write billing to a .txt
    with open(rf"{destination}/{filename}", "w") as file:
        file.write(f"TOTAL - {total}\n")
        for name in names: 
            file.write("\n")
            file.write(name + "\n")
            for session in billing[name]:
                file.write(session[0] + " " + session[1] + "\n")
    return rf"{destination}/{filename}"

def get_df_all():
    csv_path = findMostRecentCSV(download_directory) 
    return pd.read_csv(csv_path)

def createDatesDict(df_partial_clean):
    dateDict = {}
    for index, row in df_partial_clean.iterrows():
        firstName = row['First Name']
        lastName = row['Last Name']
        fullName = firstName + "_" + lastName
        if (fullName not in dateDict.keys()):
            dateDict[fullName] = [convert_comma_date_to_slash_date((row['Start Time'].split()[0] + " " + row['Start Time'].split()[1] + row['Start Time'].split()[2]))]
        else:
            dateDict[fullName].append(convert_comma_date_to_slash_date((row['Start Time'].split()[0] + " " + row['Start Time'].split()[1] + row['Start Time'].split()[2])))
    # print it out
    for key in dateDict.keys():
        print(key, dateDict[key])
    return dateDict
        

# Populates a first,last,email columns and returns a list of client first last names
def populate_first_last_email(df_partial_clean):
    clientNames = []
    # download_acuity_data() # downloads billing CSV from Acuity
    conn = psycopg2.connect(conn_string)
    curr = conn.cursor()    


    for index, row in df_partial_clean.iterrows(): # Populate first name, last name, and email
        print(index)
        firstName = row['First Name']
        lastName = row['Last Name']
        fullName = firstName + "_" + lastName
        if fullName in clientNames:
            pass
        else:
            clientNames.append(fullName)
        email = row['Email']

        # Convert email NaN to empty string
        if pd.isna(email):
            email = ''

        # Check if record already exists -- skip over it if it does
        curr.execute("""SELECT 1 FROM clients WHERE firstName=%s AND lastName = %s;""", (firstName,lastName))
        exists = curr.fetchone()       
        if exists:
            continue
        curr.execute(f"""INSERT INTO clients (firstName, lastName, email) VALUES (%s,%s,%s)""", (firstName, lastName, email))
        

    conn.commit()

    curr.close()
    conn.close()
    return clientNames

def populate_owes(df_all):
    conn = psycopg2.connect(conn_string)
    curr = conn.cursor()    
    df_clean = clean_df(df_all) # Create a separate df whose members include only people who OWE money
    billing = createBillingDict(df_clean)
    for key in billing.keys(): # Add to owes column
        firstName = key.split("_")[0]
        lastName = key.split("_")[1]
        owesValue = ""
        for value in billing[key]: # [session date, amount owed]
            owesValue += str(value) + " ,"

        curr.execute(f"""
        UPDATE clients
        SET owes = %s
        WHERE firstName = %s AND lastName = %s;
        """, (owesValue, firstName, lastName))
    conn.commit()

    curr.close()
    conn.close()

def populate_startdate(datesDict):
    conn = psycopg2.connect(conn_string)
    curr = conn.cursor()    
    # code goes here
    for key in datesDict.keys():
        firstName = key.split("_")[0]
        lastName = key.split("_")[1]
        startDate = datesDict[key][0]
        print(startDate)
        curr.execute("""UPDATE clients SET startdate = %s WHERE firstname = %s AND lastname = %s""", (startDate, firstName, lastName))
    
    conn.commit()

    curr.close()
    conn.close()

def populate_isnewclient():
    conn = psycopg2.connect(conn_string)
    curr = conn.cursor()
    
    curr.execute("""SELECT * FROM clients;""")
    records = curr.fetchall()
    survey_recepients = {}
    for record in records:
        if is_new_client(record[3], dates.today):
            fullName = record[0] + "_" + record[1]
            curr.execute("""UPDATE clients
SET isnewclient = TRUE
WHERE %s = firstname AND %s = lastname
""", (record[0], record[1]))

    conn.commit()
    curr.close()
    conn.close()

# def sendBillingReminder(df_clean, csv_path):
#     billing = createBillingDict(df_clean)
#     # Sort names alphabetically
#     tempList = []
#     for key in billing.keys():
#         tempList.append(key)
#     sortedNames = sorted(tempList)
#     fileName = csv_to_txt(csv_path) # schedule.txt
#     total = getTotalOwed(billing)
#     content_path = generateTxt(fileName=fileName, destination=destination, names=sortedNames, billing=billing, total=total)
#     recepients = [] # TO DO - READ IN ENV VARS AS LIST
#     recepients.append(os.getenv("GMAIL_RECEPIENT_1"))
#     recepients.append(os.getenv("GMAIL_RECEPIENT_2"))
#     recepients.append(os.getenv("GMAIL_RECEPIENT_3"))
#     email_pass = os.getenv("GMAIL_PASS")
#     sender = os.getenv("GMAIL_SEND_ADDRESS")
#     send_file(email_pass=email_pass, sender=sender, recepients=recepients, content_path=content_path)




# Updates AWS database with data from Acuity CSV -- run this hourly
def update_database():
    download_acuity_data()
    df_all = get_df_all()
    df_partial_clean = partial_clean_df(df_all)
    populate_first_last_email(df_partial_clean)
    populate_owes(df_all)
    populate_startdate(createDatesDict(df_partial_clean))   
    populate_isnewclient()

if __name__ == "__main__":
    update_database()
    # csv_path = findMostRecentCSV(download_directory)
    # sendBillingReminder(csv_path=csv_path)
