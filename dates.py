from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

today = datetime.now().strftime("%m/%d/%Y")

start_date = '08/01/2023'

month_dict = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"
}
def convert_comma_date_to_slash_date(comma_date): # November 12,2024 -> 11/12/2024
    tempSplit = comma_date.split(",") # [November 12, 2024]
    month_day_list = tempSplit[0].split() # [November, 12]
    year = tempSplit[1]
    month = month_day_list[0]
    day = month_day_list[1]
    if int(day) < 10:
        day = "0" + day # ensure 1 -> 01
    return month_dict[month] + "/" + day + "/" +  year

def is_past_today(slash_date_current, slash_date_today): 
    date_current =  datetime.strptime(slash_date_current, '%m/%d/%Y')
    date_today = datetime.strptime(slash_date_today, '%m/%d/%Y')
    if (date_current > date_today):
        return True # date is in the future
    else:
        return False # date is today or in the past

def is_sixty_or_more_days_ago(slash_date_current, slash_date_today):
    date_current = datetime.strptime(slash_date_current, '%m/%d/%Y')
    date_today = datetime.strptime(slash_date_today, '%m/%d/%Y')
    
    # Calculate the difference in days
    difference = (date_today - date_current).days
    
    # Check if the difference is greater than or equal to 30 days
    if difference >= 60:
        return True
    else:
        return False

def is_fourteen_or_less_days_ago(slash_date_current, slash_date_today):
    date_current = datetime.strptime(slash_date_current, '%m/%d/%Y')
    date_today = datetime.strptime(slash_date_today, '%m/%d/%Y')
    
    # Calculate the difference in days
    difference = (date_today - date_current).days
    
    # Check if the difference is greater than or equal to 14 days
    if difference <= 14:
        return True
    else:
        return False
