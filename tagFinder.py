# Finds the tag of the technology on the main tech transfer website
# then returns that variable and has the code insert that tag type into the corresponding tag

# NOW figure out how to return this and have the tag be chosen in the main playwright script
# then how to connect this to the contactLink function too so it can do that at the same time


# Import the necessary module from Playwright and others
from playwright.sync_api import *
import re
from formatting_functions import * # the other functions that gets the file name and just returns the number values (2022-004)
import glob # to loop through the files in the folder
import os
from time import sleep
from formatting_functions import *
from playwright.sync_api import TimeoutError  # Import the specific error

def findTag(page, sCleanID) :
    # goes to tech transfer website
    # page = browser.new_page()
    try :
        page.goto("https://techtransfer.byu.edu")
        page.get_by_role("link", name="Technologies", exact=True).click()
    except TimeoutError:
        exit

    # searches for the tech with the ID
    try :
        page.locator("#SearchResultsPageInput").click()
        page.locator("#SearchResultsPageInput").fill(f"{sCleanID}")
        page.locator("#SearchResultsPageSubmit").click()    
    except TimeoutError :
        pass
    
    # Get the full text that includes the ID
    try :
        full_text = page.get_by_text(f"ID: {sCleanID}").first.inner_text()
    except :
        return

    # Extract the part after the ID
    try :
        match = re.search(f"ID: {sCleanID} (.+)", full_text)
        if match:
            title_text = match.group(1)
        else:
            raise ValueError("Could not extract title text from result")
    except :
        pass

    # clicks on the link that contains the name of the tech
    try :
        page.get_by_role("link", name=title_text).first.click()
    except :
        pass

    # Get all elements near the word "TAGS"
    sleep(1) # sleep is needed or it doesn't load
    try :
        tag_elements = page.locator("text=TAGS").locator("xpath=..").locator("a")  # Assuming tags are links
        sleep(1)
    except :
        pass

    try :
        # Store the tag names in a list
        tag_list = [tag.inner_text().strip() for tag in tag_elements.all()]
        tag_name = tag_list[0] if tag_list else None
        tag_name = tag_name.lower().capitalize()
    except :
        pass
    sleep(1)
    page.close()
    return tag_name

