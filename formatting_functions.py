# Justin Maxwell
# generates the outpath and name of the document for each disclosure in the loop

import re
from time import sleep

# GET_CLEAN_ID Funtion
# function that cleans the file name
def get_clean_id(sFileName):
    sCleanID = re.sub(r'[^0-9-]', '', sFileName)     # Use regex to extract only numbers and hyphens
    return sCleanID # returns just the cleaned file name

# Formats the summary information and returns all the variables
def format_summary(extractedSummaryText):
    formattedOut = re.findall("Title:(.+)Category:.+Executive Statement:(.+)Description:(.+)Key Advantages:(.+)Problems Solved:(.+)Market Applications:(.+)",extractedSummaryText)[0]
    # assigns the tuple value to these variables
    sTitle = formattedOut[0]
    sExecutiveStatement = formattedOut[1]
    sDescription = formattedOut[2]
    sAdvantages = formattedOut[3]
    sProblemsSolved = formattedOut[4]
    sMarketApplications = formattedOut[5]

    # splits the tuple by each period to add to each list to be made into buller points in create_pdf()
    lstAdvantages = [
        item.strip() 
        for item in re.sub(r"([a-z])([A-Z])", r"\1. \2", sAdvantages).split(".") 
        if item.strip()
    ]

    lstProblemsSolved = [
        item.strip() 
        for item in re.sub(r"([a-z])([A-Z])", r"\1. \2", sProblemsSolved).split(".") 
        if item.strip()
    ]

    lstMarketApplications = [
        item.strip() 
        for item in re.sub(r"([a-z])([A-Z])", r"\1. \2", sMarketApplications).split(".") 
        if item.strip()
    ]

    return sTitle, sExecutiveStatement, sDescription, lstAdvantages, lstProblemsSolved, lstMarketApplications



# Finds the tag of the technology on the main tech transfer website
# then returns that variable and has the code insert that tag type into the corresponding tag
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

