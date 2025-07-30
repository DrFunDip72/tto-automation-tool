# Confidguration file for web development automation
# Contains all of the file paths and other configurations needed for the automation script

import os
import glob
import logging

# --- LOGGING SETUP ---
logging.basicConfig(
    filename='error_log.txt',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- HELPER FUNCTION ---
def try_function(func, *args, sCleanID="", func_name=""):
    """Tries a function call, logs if it fails."""
    try:
        func(*args)
    except Exception as e:
        error_message = f"{sCleanID} - {func_name} failed: {str(e)}"
        logging.warning(error_message)

# User login function
def user_login() :
    userUsername, userPassword = input("Enter your BYU Net ID: "), input("Enter your BYU password: ")
    return userUsername, userPassword

# Path to the Chrome user data directory
chrome_user_data_path = r"C:\Users\justi\AppData\Local\Google\Chrome\User Data\Profile 2"

# Used in MAIN.PY to get the file paths of all the pdf files in the disclosures folder
disclosures_folder = "C:/Users/justi/Downloads/web_dev_automation-main/web_dev_automation-main/Disclosures"
pdfFiles = glob.glob(os.path.join(disclosures_folder, "*.pdf"))

# Path to the folder where images are stored
images_folder = r"C:\Users\justi\Desktop\Desktop\Justin\Coding Projects\Automation\Images"

# Path to the where the fonts are stored
# you need both the regular one and the bold version
noto_sans_r = "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Fonts/NotoSans-Regular.ttf"
noto_sans_b = "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Fonts/NotoSans-Bold.ttf"

# Path to the banner image and foote image
banner_path = "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Images/banner.png"
footer_banner_path = "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Images/footer banner.png"  # Ensure the correct path

# The folder where the exported sell sheets will be saved
export_folder = r"C:\Users\justi\Desktop\Desktop\Justin\Coding Projects\Automation\Exported Sell Sheets"