import numpy as np
import pandas as pd
import download
from CSV import findMostRecentCSV, csv_to_txt
import dates
from dates import convert_comma_date_to_slash_date, is_past_today
from download import download_acuity_data

invalid_meeting_types = ['Short Meeting', 'Meeting', 'Business Meeting', 'ACT Diagnostic']
destination = r"C:\Users\Jacob\Downloads" # processed info goes here
download_directory = r"C:\Users\Jacob\Downloads" # default download location

def clean_df(df):
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
        for session in value:
            total += float(session[1])
    return total

def generateTxt(fileName, destination, names, billing, total): # pretty write billing to a .txt
    with open(rf"{destination}\{fileName}", "w") as file:
        file.write(f"TOTAL - {total}\n")
        for name in names: 
            file.write("\n")
            file.write(name + "\n")
            for session in billing[name]:
                file.write(session[0] + " " + session[1] + "\n")

def process_billing_csv():
    # download_acuity_data() # downloads billing CSV from Acuity
    csv_path = findMostRecentCSV(download_directory) 
    df_all = pd.read_csv(csv_path)
    df_not_paid = clean_df(df_all)
    billing = createBillingDict(df_not_paid)
    # Sort names alphabetically
    tempList = []
    for key in billing.keys():
        tempList.append(key)
    sortedNames = sorted(tempList)
    fileName = csv_to_txt(csv_path) # schedule.txt
    total = getTotalOwed(billing)
    print(total)
    generateTxt(fileName=fileName, destination=destination, names=sortedNames, billing=billing, total=total)
    path = rf"{destination}\{fileName}"
    return path

if __name__ == "__main__":
    process_billing_csv()