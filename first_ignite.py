# Justin Maxwell - first_ingite function
# Goes to first ignite, loads the disclosure, then extracts the necessary information

# IMPORTS
from time import sleep # for sleeping, first ingnite needs to load
import re # to find the proper text


# Function that uploads a file into firstignite, runs it, then extracts the text from the summary tab
    # it first locates the toggle that allows pdf files to be inserted, launches it, navigates to the summary tab, then extracts all the text
    # and returns just the summary text (which will then be formatted and cleaned) 

def launch_first_ignite(page, filePath):
    page.locator("div").filter(has_text=re.compile(r"^TextFile$")).locator("label span").click() # turns on the toggle that allows files to be uploaded
    sleep(1)

    page.get_by_role("textbox", name="󰕒 Drop your file here or").set_input_files(filePath) # uploads the file being used in the for loop
    page.get_by_text("Launch 🚀").click() # launches

    sleep(60) # waits for it to load
    page.locator("#Summary-label").click(timeout=500*1000) # locates where all the text is in the summary tab

    # locates where the text is then gets it
    summaryText = page.locator(".editor__content").text_content()
    return summaryText