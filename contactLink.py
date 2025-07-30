# Justin Maxwell - 3.21.25 
# DESCRIPTION: The python code to automate uploading disclosures into FirstIgnite, generating the report
# Then taking the summary and formatting it in a google doc and exporting as a PDF


# Import the necessary module from Playwright and others
from playwright.sync_api import *
import re
from formatting_functions import * # the other functions that gets the file name and just returns the number values (2022-004)
import glob # to loop through the files in the folder
import os
from time import sleep
from formatting_functions import *
from playwright.sync_api import TimeoutError  # Import the specific error
from tagFinder import *
# from overrideTest import *
import logging

logging.basicConfig(
    filename='error_log.txt',     # Log file name
    filemode='a',                 # Append mode
    level=logging.INFO,           # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Folder containing the disclosures
to_load_folder = r"C:\Users\justi\Desktop\Desktop\Justin\Coding Projects\Automation\Disclosures\Done\To load"

# Get all PDF files
pdfFiles = glob.glob(os.path.join(to_load_folder, "*.pdf"))


# logs into brightspot
def loginFunction(page, userUsername, userPassword) :
    try: # Logs into the Brightspot
        page.get_by_role("link", name="Log in to BYU", exact=True).click()
        page.get_by_role("textbox", name="Net ID").click()
        page.get_by_role("textbox", name="Net ID").fill(userUsername)
        page.get_by_role("textbox", name="Password").click()
        page.get_by_role("textbox", name="Password").fill(userPassword)
        page.get_by_role("button", name="Sign In").click()

        sleep(5)
    except:
        pass


# this one needs to be reinforced to make sure it actually finds the page thing and clicks enter so that it searches properly
# searches for the technology based on the ID
def searchTechnology(page, sCleanID) :
    
    try :
        page.get_by_role("textbox", name="search Search").click()
        page.get_by_role("textbox", name="search Search").type(f"{sCleanID}")
        sleep(1)
    except TimeoutError :
        pass

    tried = ""
    try: 
        page.get_by_role("combobox", name="Type").click()
        for iCount in range (0, 17) : # highlights the text
            page.get_by_role("textbox", name="Search", exact=True).press("ArrowDown")
        sleep(1)
    except :
        print("Couldn't filter")
        tried = "y"
        sleep(1)

    if tried == "y" :
        try: 
            page.get_by_role("combobox", name="Type").locator("div").nth(1).click()
            for iCount in range (0, 17) : # highlights the text
                page.get_by_role("textbox", name="Search", exact=True).press("ArrowDown")
            sleep(1)
        except :
            print("still couldn't filter")

    try : 
        page.get_by_role("textbox", name="Search", exact=True).press("Enter")
        sleep(3)
    except TimeoutError:
        pass

    try :
        page.get_by_role("textbox", name="search Search").fill("")
        page.get_by_role("textbox", name="search Search").type(f"{sCleanID}")
        sleep(2)
    except TimeoutError:
        pass

    # I would need to get the title name of the tech first before doing this one
    # page.get_by_role("link", name="Automatic Marking System for").nth(1).click()

    # if the ID is in this name text, then click on it (EASIER??)
    # page.get_by_role("row", name="Automatic Marking System for Highway Infrastructure Inspection ID: 2015-010 open_in_new Tech 2015: Tag, All Technologies: Tag, Engineering Tue Apr 08 19:49:38 EDT 2025 00000196-17cf-d1ff-a59f-77df37560000 5", exact=True).get_by_role("link").nth(1).click()
    try :
        page.get_by_role("row", name=sCleanID).get_by_role("link").nth(1).click()
    except TimeoutError:
        pass


def insertNewLink(page, fullLink) :

    page.mouse.wheel(0,10000)
    sleep(2)

    tried = ""
    try : 
        page.get_by_text("Rich Text: (RichText Card)").click(timeout=10000)
    except TimeoutError:
        tried = "y"

    if tried == "y" :
        try : 
            page.get_by_role("heading", name="Aside/Below keyboard_arrow_up").locator("div").click()
            page.get_by_text("Rich Text: (RichText Card)").click(timeout=10000)
            sleep(1)
        except TimeoutError: 
            tried = "y2"
    
    if tried == "y2" :
        try : 
            page.get_by_role("heading", name="Aside/Below keyboard_arrow_up").click(timeout=10000)
            page.get_by_text("Rich Text: (RichText Card)").click(timeout=10000)
        except TimeoutError:
            pass

    try : 
        page.get_by_role("link", name="Contact Us").click(timeout=10000)
        page.locator(".ProsemirrorEnhancementMenu-container-button").first.click(timeout=10000)
    except TimeoutError :
        pass


    sleep(1)
    try :
        page.get_by_text("InternalInternalExternal").click()
        page.get_by_role("textbox", name="Search", exact=True).press("ArrowDown")
        page.get_by_role("textbox", name="Search", exact=True).press("Enter")
    except TimeoutError:
        pass

    try :
        sleep(1)
        page.get_by_role("textbox", name="URL").click(timeout=10000)
        page.get_by_role("textbox", name="URL").fill(f"{fullLink}")
        page.get_by_role("button", name="Save & Close").click(timeout=10000)
        sleep(3)
    except :
        pass



# Function that opens the Chrome browser, goes to FirstIgnite, uploads the disclosure (in a for loop), and calls the function to create the sell sheet pdf
def run(playwright: Playwright) -> None:


    # Opens the browser     
    browser = p.chromium.launch_persistent_context(
        user_data_dir=chrome_user_data_path,  # Use your existing Chrome profile
        headless=False,  # Set to False so you can see the browser window
        args=["--disable-blink-features=AutomationControlled"]  # Helps bypass bot detection
    )

    # loops through each exported sell sheet
    for filePath in pdfFiles :
        
        # sets the file name
        sFileName = os.path.basename(filePath)
        
        # from the folder path, cleans the ID and returns it
        try :
            sCleanID = output_name(sFileName)
        except :
            pass
        page = browser.new_page()


        try :
            tagName = findTag(page, sCleanID)
        except TimeoutError:
            logging.warning(f"{sCleanID} - tag not found, skipping.")
            tagName = None

        
        page = browser.new_page()
        page.goto("https://brightspot.byu.edu/cms/logIn.jsp?returnPath=%2Fcms%2Findex.jsp")


        # My username and password
        # REMOVE WHEN PUT ON GITHUB!!!
        userUsername = "justmax"
        userPassword = "newJustinpW10854$"
        
        # logs into brightspot
        try :
            loginFunction(page, userUsername, userPassword) 
        except TimeoutError:
            exit
        
        # searches for the technology
        try :
            searchTechnology(page, sCleanID)
        except :
            try :
                searchTechnology(page, sCleanID)
            except :
                logging.warning(f"{sCleanID} - not able to be searched. Skipping.")
                continue

        try :
            # creates the link that will be inserted
            halfLink = page.get_by_role("textbox", name="Internal Name").input_value()
            fullLink = f"https://techtransfer.byu.edu/contact?technology-id={halfLink}"
        except TimeoutError :
            pass


        try:
            # inserts the link into the contact us link
            insertNewLink(page, fullLink)
        except :
            logging.warning(f"{sCleanID} - contact link not inserted.")

        # 
        if tagName is None :
            # Try clicking "search Engineering", if that fails, try "search Life Sciences"
            logging.warning(f"{sCleanID} - tag not found, skipping.")
        else :
            try:
                page.get_by_role("link", name="search Engineering").click()
                sleep(10)
            except:
                try:
                    page.get_by_role("link", name="search Life Sciences").click()
                    sleep(10)
                except:
                    print("Neither 'search Engineering' nor 'search Life Sciences' found.")
                    pass

            # Then try clicking the actual tag and closing the tag box
            try:
                sleep(10)
                page.get_by_role("link", name=tagName).click(timeout=10000)
                sleep(2)
                page.get_by_title("Close", exact=True).click(timeout=10000)
            except:
                print(f"Could not click tag or close tag modal for {tagName}.")
                logging.warning(f"{sCleanID} - Tag was not changed.")


        try : 
            overrideLink(page, sCleanID)
        except :
            pass

        sleep(3)

        # Publishes it
        try :
            page.get_by_role("button", name="Publish").click()
            sleep(10)
            page.close()
        except TimeoutError:
            print(f"{sCleanID} not published")
            page.close()



# Define the path to your Chrome user data directory.
# Replace "YourUsername" with your actual Windows username.
chrome_user_data_path = r"C:\Users\justi\AppData\Local\Google\Chrome\User Data\Profile 2"

# # # Start Playwright
# with sync_playwright() as p:
#     run(p)

