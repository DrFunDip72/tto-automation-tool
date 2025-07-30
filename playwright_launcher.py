# Justin Maxwell - Playwright Launcher

# This python file launches playwright so it can be used to do other things


# Import the necessary module from Playwright and others
from playwright.sync_api import *
from time import sleep

chrome_user_data_path = r"C:\Users\justi\AppData\Local\Google\Chrome\User Data\Profile 2"

# Function that opens the Chrome browser, goes to FirstIgnite, uploads the disclosure (in a for loop), and calls the function to create the sell sheet pdf
def run(playwright: Playwright) -> None:
    # Opens the browser     
    # browser = playwright.chromium.launch(headless=False)
    # Opens the browser     
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=chrome_user_data_path,  # Use your existing Chrome profile
        headless=False,  # Set to False so you can see the browser window
        args=["--disable-blink-features=AutomationControlled"]  # Helps bypass bot detection
    )
    page = browser.new_page()
    # Navigate to the website you want to automate
    sleep(4)
    return browser, page
