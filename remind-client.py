import ast
import os
import psycopg2
import ast
from pathlib import Path
from send_file import send_file
from dates import is_sixty_or_more_days_ago, is_fourteen_or_more_days_ago, today

def get_download_directory():
    home = Path.home()
    if os.name == 'nt':  # Windows
        return str(home / 'Downloads')
    elif os.name == 'posix':  # Linux and MacOS
        return str(home / 'Downloads')
    else:
        raise NotImplementedError(f"Unsupported OS: {os.name}")

def generateTxt(destination, sessions_as_string, full_name_underscore):
    first_name = full_name_underscore.split("_")[0]
    last_name = full_name_underscore.split("_")[1]
    with open(rf"{destination}\email.txt", "w") as file:
        file.write(f"Dear Parents,<br><br>We have been doing an internal review of our billing, and our system shows that the following<br>dates of service from the past year have not been paid for {first_name} {last_name}:<br><br>{sessions_as_string}<br>Often this is due to an expired card or security block. Because we run billing session by session,<br> occasionally some billing also slips through the cracks. Please let us know if we can proceed in<br>running these sessions by replying to this email. If you have changed your card, you can call us<br>at (901) 590-3318 so that we can update your billing information.<br><br> If you have any questions or concerns, don’t hesitate to reach out and we would be happy to address them.<br><br>Thanks,<br><br>Faris and Zane<br>The Tutors<br><br>")
    return (rf"{destination}\email.txt")

def find_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None  # If the value is not found, return None

# Runs at 10am Mondays
def remind_client():
    # CHANGE THESE BACK TO VARS
    conn = psycopg2.connect(os.getenv("DB_CONN"))
    curr = conn.cursor()       
    curr.execute("""
    SELECT * 
    FROM clients 
    WHERE owes IS NOT NULL;
""")
    owes = {}
    rows = curr.fetchall()
    # ADD PEOPLE FROM OWES WHO OWE <= 400 DOLLARS
    for row in rows:
        formatted_string = f"[{row[6]}]"
        list_of_lists = ast.literal_eval(formatted_string)
        total = 0
        for list in list_of_lists:
            total+=float(list[1])
        if (total <= 400):
            # If datereminded is NOT fourteen or more days ago, skip over this person
            if (is_fourteen_or_more_days_ago(row[7) == False):
                print(f"Skipping {row[0]}")
                continue
            fullName = row[0] + "_" + row[1]
            owes[fullName] = [list_of_lists, row[2]] # owes["John_Smith"] = [ [ [08/23/23, 45.0], [09/23/23, 45.0] ], "john.smith@gmail.com"]
    
    persons_to_remove = [] # people who never have a session earlier than 60 days
    # ONLY EMAIL THOSE WHO HAVE AT LEAST ONE SESSION 60 OR MORE DAYS AGO
    for value in owes.values():
        will_be_emailed = False
        session_list = value[0]
        for session in session_list:
            if is_sixty_or_more_days_ago(session[0], today): # this person will be emailed
                # print(find_key_by_value(owes,value))
                will_be_emailed = True
                break
        if will_be_emailed:
            continue
        person_to_remove = find_key_by_value(owes, value)
        persons_to_remove.append(person_to_remove)
    
    for person in persons_to_remove:
        try:
            del owes[person]
        except KeyError:
            continue
    
    # REMOVE - TEST RUN FOR FARIS
    for key in owes.keys():
        if key != "Faris_Haykal":
            persons_to_remove.append(key)
    
    for person in persons_to_remove:
        try:
            del owes[person]
        except KeyError:
            continue

    # Email each person in owes
    email_pass = os.getenv("GMAIL_REMINDER_SENDER_PASS")
    sender = os.getenv("GMAIL_REMINDER_SENDER")
    for person in owes.keys():
        sessions_as_string = ""
        for index,session in enumerate(owes[person][0]):
            sessions_as_string += owes[person][0][index][0] + " " + owes[person][0][index][1] + "<br>"
        path_to_email = generateTxt(get_download_directory(), sessions_as_string=sessions_as_string, full_name_underscore=person)
        send_file(email_pass=email_pass, sender=sender, recipient=owes[person][1],content_path=path_to_email)

    for person in owes.keys():
        first_name = person.split("_")[0]
        last_name = person.split("_")[1]
        curr.execute("""UPDATE clients SET datereminded = %s WHERE firstname = %s AND lastname = %s;""", (today,first_name,last_name,))
    conn.commit()
    curr.close()
    conn.close()

if __name__ == "__main__":
    remind_client()
