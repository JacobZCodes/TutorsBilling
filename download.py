import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import dates
from pathlib import Path

def get_download_directory():
    home = Path.home()
    if os.name == 'nt':  # Windows
        return home / 'Downloads'
    elif os.name == 'posix':  # Linux and MacOS
        return home / 'Downloads'
    else:
        raise NotImplementedError(f"Unsupported OS: {os.name}")

class Browser:
    browser, service = None, None

    def __init__(self, driver:str):
        self.service = Service(driver)
        self.browser = webdriver.Chrome(service=self.service)
        self.browser.maximize_window()
    
    def open_page(self, url:str):
        self.browser.get(url)
    
    def close_browser(self):
        self.browser.close()
    
    def add_input(self, by:By, value: str, text:str):
        field = self.browser.find_element(by=by, value=value)
        field.send_keys(text)
        time.sleep(1)
    
    def click_button(self, by:By, value:str):
        button = self.browser.find_element(by=by, value=value)
        self.browser.execute_script("arguments[0].click();", button)
        time.sleep(1)

    def login_acuity(self, username: str, password: str):
        self.add_input(by=By.ID, value='username', text=username)
        self.click_button(By.CSS_SELECTOR, "input#next-button[type='submit']")        
        self.add_input(by=By.ID, value='password', text=password)
        self.click_button(By.CSS_SELECTOR, "input#next-button[data-testid='next-button'][type='submit'][name='login'][value='Log in']")

def download_acuity_data():
    browser = Browser(os.getenv("CHROMEDRIVER_PATH")) # path to chromedriver
    browser.open_page("https://acuityscheduling.com/login.php?redirect=1")
    time.sleep(3)
    browser.login_acuity(os.getenv("ACUITY_USER"), os.getenv("ACUITY_PASSWORD")) 
    browser.click_button(By.CSS_SELECTOR, 'a[href="/reports.php"]')
    browser.click_button(By.CSS_SELECTOR, 'a[href="/reports.php?action=importexport"]')
    browser.add_input(By.ID, 'minDay-input', dates.start_date) # set this in dates.py
    browser.add_input(By.ID, 'maxDay-input', dates.today)
    browser.click_button(By.CSS_SELECTOR, 'input[value="Export Appointments"]')
    time.sleep(10)
        
if __name__ == "__main__":
    download_acuity_data()


