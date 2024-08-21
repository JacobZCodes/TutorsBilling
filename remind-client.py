import ast
import os
import psycopg2
import ast
from pathlib import Path
from send_file import send_file
from dates import is_sixty_or_more_days_ago, today

def get_download_directory():
    home = Path.home()
    if os.name == 'nt':  # Windows
        return str(home / 'Downloads')
    elif os.name == 'posix':  # Linux and MacOS
        return str(home / 'Downloads')
    else:
        raise NotImplementedError(f"Unsupported OS: {os.name}")

def generateTxt(destination, sessions_as_string):
    with open(rf"{destination}\email.txt", "w") as file:
        file.write(f"Hello, we have recently been doing an audit on our back-billing and have found that you owe the following:\n {sessions_as_string}")
    return (rf"{destination}\email.txt")

def find_key_by_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None  # If the value is not found, return None

# Checks at EOD every day and sends survey email
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
    for row in rows:
        formatted_string = f"[{row[6]}]"
        list_of_lists = ast.literal_eval(formatted_string)
        total = 0
        for list in list_of_lists:
            total+=float(list[1])
        if (total <= 400):
            fullName = row[0] + "_" + row[1]
            owes[fullName] = [list_of_lists, row[2]] # owes["John_Smith"] = [ [ [08/23/23, 45.0], [09/23/23, 45.0] ], "john.smith@gmail.com"]
    
    persons_to_remove = [] # people who never have a session earlier than 60 days
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
        del owes[person]
    
    # REMOVE - TEST RUN FOR FARIS
    for key in owes.keys():
        if key != "***REMOVED***":
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
        for session in owes[person][0]:
            sessions_as_string += owes[person][0][0][0] + " " + owes[person][0][0][1] + "\n"
        path_to_email = generateTxt(get_download_directory(), sessions_as_string=sessions_as_string)
        send_file(email_pass=email_pass, sender=sender, recepient=owes[person][1],content_path=path_to_email)
        

        
        

     
    exit(0)
    # REMOVE PRUNING OF FARIS AND JACOB
    # recepients = []
    # namesToRemove = []
    # for name in addresses.keys():
    #     if name != "***REMOVED***":
    #         namesToRemove.append(name)
    # for name in namesToRemove: 
    #     del addresses[name]
    # recepients.append(os.getenv("GMAIL_RECEPIENT_0"))
    
    # KEEP - ADD CLIENT RECEPIENTS
    # for recepient in addresses.keys():
    #     recepients.append(addresses[recepient])
    
    email_pass = os.getenv("GMAIL_SURVEY_SENDER_PASS")
    sender = os.getenv("GMAIL_SURVEY_SENDER")

    send_file(email_pass=email_pass, sender=sender, recepients=addresses.values(), content_path=generateTxt(get_download_directory()))

    # # CHANGE RECEIVEDSURVEY TO BE TRUE
    # for recepient in addresses.keys():
    #     firstName = recepient.split("_")[0]
    #     lastName = recepient.split("_")[1]
    #     curr.execute(f"""
    #     UPDATE clients
    #     SET receivedsurvey = TRUE
    #     WHERE firstName = %s AND lastName = %s;
    #     """, (firstName, lastName))
    # conn.commit()
    curr.close()
    conn.close()


if __name__ == "__main__":
    remind_client()
