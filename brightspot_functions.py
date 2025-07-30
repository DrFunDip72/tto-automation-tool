# Justin Maxwell

# BRIGHTSPOT FUNCTIONS
    # logs into brightspot
    # clicks on the template
    # changes DISPLAY & INTERNAL NAME
    # inserts TECH NAME + ID
    # inserts EXECUTIVE STATEMENT
    # FUTURE FUNCTIONALITY -> searches for/uploads the image and changes it
    # inserts TECHNOLOGY OVERVIEW
    # inserts KEY ADVANTAGES, PROBLEMS ADDRESSED, MARKET APPLICATIONS
    # inserts the additional information, uploads and links the pdf sell sheet
    # changes the TAGS (year of technology, type[engineering or life science, etc.])
    # updates the link inside the CONTACT US card so that it can be autopopulated in the contact us page
    # OVERRIDE tab -> inserts TECH ID into the description and (FUTURE) searches for and updates the image
    # PUBLISH


from datetime import datetime # to get the current day and time to put in the additional information section
from time import sleep
import re
import os


# LOGS INTO BRIGHTSPOT
def bs_login(page, userUsername, userPassword) :
    # You can either hardcode your username and password here or use environment variables
    # For security reasons, it's better to use environment variables

    page.get_by_role("link", name="Log in to BYU", exact=True).click()
    sleep(3)
    if page.get_by_role("textbox", name="Net ID").is_visible(timeout=3000):
        page.get_by_role("textbox", name="Net ID").fill(userUsername)
        page.get_by_role("textbox", name="Password").fill(userPassword)
        page.get_by_role("button", name="Sign In").click()
        sleep(3)

# Selects the TEMPLATE
def bs_template_click(page) :
    page.get_by_role("link", name="Technology Page Template").click()
    sleep(4)

# Changes the DISPLAY and INTERNAL name 
def bs_display_internal_name(page, sTitle, sCleanID) :
    page.get_by_role("textbox", name="Display Name").fill(f'{sTitle}')
    page.get_by_role("textbox", name="Internal Name").fill(f"{sTitle} ID: {sCleanID}")

# Inserts the TITLE for TECH ID + CLEAN ID
def bs_title_techID(page, sTitle, sCleanID) :
    page.locator(".repeatableLabel").first.click()
    page.get_by_role("list").filter(has_text="Rich Text: (RichText)").locator("bsp-line").click()
    page.locator("div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").fill(f"{sTitle} ID: {sCleanID}")
    page.locator("div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").press("ControlOrMeta+Shift+ArrowUp")
    page.get_by_role("link", name="H2").nth(1).click()

# Inserts the EXECUTIVE STATEMENT
def bs_executive_statement(page, sExecutiveStatement) :
    page.locator(".is-collapsed > .repeatableLabel").first.click()
    page.mouse.wheel(0,500) # scrolls so it can find the next locator
    sleep(2)
    # page.locator("bsp-line").nth(2).click()
    page.locator("li:nth-child(2) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").fill(f"{sExecutiveStatement}")
    sleep(1)
    page.locator("li:nth-child(2) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").press("ControlOrMeta+Shift+ArrowUp")
    sleep(1)
    page.get_by_role("link", name="H4").nth(2).click()

# Inserts the IMAGE on the MAIN PAGE
def bs_image_main_page(page, sCleanID) :
    # Step 1: Build the image path using sCleanID
    image_path = os.path.join(
        r"C:\Users\justi\Desktop\Desktop\Justin\Coding Projects\Automation\Images",
        f"{sCleanID} image.jpeg"  # Or .png, if you're using PNGs
    )

    page.locator("li:nth-child(3) > .repeatableLabel").click()
    page.locator("bsp-image").get_by_text("Edit").click()
    page.get_by_role("link", name="technology placeholder image").click()
    page.get_by_role("button", name="New Image").click()
    sleep(3) # so it can load
    
    # Upload file
    page.get_by_role("textbox", name="Choose").set_input_files(image_path)
    sleep(10)
    page.locator("form").filter(has_text=f"New Image: {sCleanID}-image").locator("button[name=\"action-publish\"]").click() # NOT WORKING
    sleep(10)
    page.get_by_text("Back", exact=True).click()
    page.get_by_role("link", name=f"{sCleanID}-image.jpeg", exact=True).click()
    page.get_by_role("button", name="Save & Close").click()
    page.locator("li:nth-child(3) > .repeatableLabel").click()


# Inserts the TECHNOLOGY OVERVIEW (DESCRIPTION)
def bs_technology_overview(page, sDescription) :
    page.locator("li:nth-child(5) > .repeatableLabel").click()
    # page.locator("bsp-line").nth(4).click()
    page.locator("li:nth-child(5) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").fill(f"{sDescription}")

# Inserts the KEY ADVANTAGES
def bs_key_advantages(page, lstAdvantages) :
    page.locator("li:nth-child(8) > .repeatableLabel").click()
    page.locator("li:nth-child(8) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror > bsp-line").click()
    page.locator("li:nth-child(8) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirrorToolbar > ul > li:nth-child(7) > .rte2-toolbar-ul").click()
    
    # Join all advantages with a line break and fill them
    advantagesText = "\n".join(adv.strip() for adv in lstAdvantages if adv.strip())
    page.locator("li:nth-child(8) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").fill(advantagesText)
    
# Inserts the PROBLEMS ADDRESSED
def bs_problems_addressed(page, lstProblemsAddressed) :
    page.locator("li:nth-child(10) > .repeatableLabel").click()
    page.locator("li:nth-child(10) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror > bsp-line").click()
    page.locator("li:nth-child(10) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirrorToolbar > ul > li:nth-child(7) > .rte2-toolbar-ul").click()
                
    # Join and fill the Problems Solved list automatically
    problemsText = "\n".join(problem.strip() for problem in lstProblemsAddressed if problem.strip())
    page.locator("li:nth-child(10) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").fill(problemsText)

# Inserts the MARKET APPLICATIONS
def bs_market_applications(page, lstMarketApplications) :
    page.locator("li:nth-child(13) > .repeatableLabel").click()
    page.locator("li:nth-child(13) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror > bsp-line").click()
    page.locator("li:nth-child(13) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirrorToolbar > ul > li:nth-child(7) > .rte2-toolbar-ul").click()

    # Bullet points for market applications
    marketApplicationsText = "\n".join(app.strip() for app in lstMarketApplications if app.strip())
    page.locator("li:nth-child(13) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").fill(marketApplicationsText)

# Inserts the ADDITIONAL INFORMATION information
def bs_additional_information(page, sCleanID) :
    page.locator("li:nth-child(16) > .repeatableLabel").click()
    page.locator("li:nth-child(16) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror > bsp-line").click()
    date_published = datetime.now().strftime("%d %B, %Y")  # Example: "21 April, 2025"
    page.locator("li:nth-child(16) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirror").fill(f"Technology ID: {sCleanID}\nSell Sheet: Download the Sell Sheet here\nMarket Analysis: Contact us for a more in-depth market report\nDate Published: {date_published}")

# Uploads the exported sell sheet pdf into the "Download the Sell Sheet here" text
def bs_upload_pdf(page, sCleanID, exportFolder) :
    # moves the cursor and highlights the corresponding text "Download the Sell Sheet here"
    for iCount in range(0, 91) : # moves the cursor
        page.get_by_text(f"Technology ID: {sCleanID}Sell").press("ArrowLeft")
    
    for iCount in range (0, 28) : # highlights the text
        page.get_by_text(f"Technology ID: {sCleanID}Sell").press("Shift+ArrowLeft")

    # Uploads the PDF and links it
    page.locator("li:nth-child(16) > .objectInputs > div:nth-child(3) > div:nth-child(2) > .ProseMirrorContainer > .ProseMirrorToolbar > ul > li:nth-child(24) > .brightspot-core-link-LinkRichTextElement").click()
    page.get_by_role("link", name="(Required) search").click()
    page.locator("div").filter(has_text=re.compile(r"^Article$")).nth(2).click()
    page.get_by_role("textbox", name="Search", exact=True).press("ArrowDown")
    page.get_by_role("textbox", name="Search", exact=True).press("Enter")
    page.get_by_role("button", name="New").click()
    pdf_path = os.path.join(exportFolder, f"{sCleanID} Sell Sheet.pdf")
    page.get_by_role("textbox", name="Choose").set_input_files(pdf_path)
    sleep(5)
    page.locator("form").filter(has_text=f"New Attachment: {sCleanID}-sell").locator("button[name=\"action-publish\"]").click()
    sleep(5)
    page.get_by_text("Back", exact=True).click()
    sleep(3)
    firstNum, lastNum = sCleanID.split('-') # splits the sCleanID so I can get the last digits to be able to link it
    page.get_by_role("link", name=f"-{lastNum}-sell-sheet.pdf").first.click()
    page.get_by_role("button", name="Save & Close").click()

# Changes the YEAR TAG
def bs_year_tag(page, sCleanID) :
    # Depending on the year of the tech, chooses that Tag
    years = ["2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    yearTag = next((year for year in years if year in sCleanID), None)

    # Chooses the tags
    page.get_by_role("link", name="search Tech 2024: Tag").click(timeout=300*10000)
    page.get_by_role("link", name="chevron_right").click(timeout=300*10000)
    page.get_by_role("link", name=f"Tech {yearTag}: Tag").click(timeout=300*10000)
    sleep(10) # so it can publish

def bs_type_tag(page, sCleanID, tagTypeSelections) :
    sTypeTag = tagTypeSelections.get(sCleanID, "Select one")
    if sTypeTag != "Select One" :
        page.get_by_role("link", name="add Add Item").click()
        page.get_by_role("link", name="search", exact=True).first.click()
        sleep(12) # so it can load
        page.get_by_role("link", name=sTypeTag, exact=False).click() 
        page.get_by_title("Close", exact=True).click()

# Inserts a NEW LINK inside the contact us link so that it can autopopulate the tech ID box with the tech name and ID
def bs_contact_link(page) :
    # Step 1: Build the contact link
    halfLink = page.get_by_role("textbox", name="Internal Name").input_value()
    fullLink = f"https://techtransfer.byu.edu/contact?technology-id={halfLink}"

    # Step 2: Expand Aside/Below if the Rich Text card is not visible
    page.mouse.wheel(0,500) # scrolls so it can find the next locator
    sleep(2)
    rich_text = page.get_by_text("Rich Text: (RichText Card)")
    if not rich_text.is_visible():
        page.get_by_role("heading", name="Aside/Below keyboard_arrow_up").locator("div").click()
        sleep(1)

    # Step 3: Open Rich Text card
    page.get_by_text("Rich Text: (RichText Card)").click(timeout=10000)
    sleep(1)

    # Step 4: Click Contact Us link and open editor
    page.mouse.wheel(0,500) # scrolls so it can find the next locator
    sleep(1)
    page.get_by_role("link", name="Contact Us").click(timeout=10000)
    page.locator(".ProsemirrorEnhancementMenu-container-button").first.click(timeout=10000)
    sleep(1)

    # Step 5: Set link type to External
    page.get_by_text("InternalInternalExternal").click()
    search_box = page.get_by_role("textbox", name="Search", exact=True)
    search_box.press("ArrowDown")
    search_box.press("Enter")
    sleep(1)

    # Step 6: Fill in the URL
    page.get_by_role("textbox", name="URL").fill(fullLink)
    page.get_by_role("button", name="Save & Close").click(timeout=10000)
    sleep(3)

# Changes the OVERRIDE DESCRIPTION to the tech ID
def bs_override_description(page, sCleanID):
# Step 1: Click the Overrides tab
    page.get_by_role("link", name="Overrides").first.click(timeout=5000)

    # Step 2: Define the promo selector
    promo_selector = page.locator("div").filter(has_text=re.compile(r"^ID: \d{4}-\d{3}$"))

    # Step 3: Expand Promo Module Overrides if needed
    if not promo_selector.is_visible():
        page.get_by_role("heading", name=re.compile("Promo Module Overrides", re.IGNORECASE)).locator("div").click(timeout=5000)

    # Step 4: If visible, check and update
    if promo_selector.is_visible():
        if promo_selector.inner_text(timeout=3000).strip() != f"ID: {sCleanID}":
            promo_selector.click(timeout=5000)
            promo_selector.fill(f"ID: {sCleanID}")

# Changes the OVERRIDE IMAGE
def bs_override_image(page, sCleanID) :
    page.get_by_role("link", name="technology placeholder image").click()
    page.locator("form").filter(has_text="SearchGoAny Publish").get_by_label("Search").click()
    page.locator("form").filter(has_text="SearchGoAny Publish").get_by_label("Search").type(f"{sCleanID}")
    page.get_by_role("link").filter(has_text=sCleanID).first.click()

# PUBLISHES the page
def bs_publish(page) :
    page.get_by_role("button", name="Publish").click()
    sleep(10)
    page.close()

# Searches for the technology ID in the search bar
def bs_search_technology(page, sCleanID) :
    
    page.get_by_role("textbox", name="search Search").click()
    page.get_by_role("textbox", name="search Search").type(f"{sCleanID}")
    sleep(1)

    tried = False
    # Tries to change the search type to Page
    # If it didn't work, then it tries the second method
    try: 
        page.get_by_role("combobox", name="Type").click()
        for iCount in range (0, 17) : # highlights the text
            page.get_by_role("textbox", name="Search", exact=True).press("ArrowDown")
        sleep(1)
    except :
        tried = True
        sleep(1)

    # Second attempt using a different page.get_by_role
    if tried == True :
        page.get_by_role("combobox", name="Type").locator("div").nth(1).click()
        for iCount in range (0, 17) : # highlights the text
            page.get_by_role("textbox", name="Search", exact=True).press("ArrowDown")
        sleep(1)

    # Selects it by pressing enter
    page.get_by_role("textbox", name="Search", exact=True).press("Enter")
    sleep(3)

    # Clears the search box and types in the ID again to load the results
    page.get_by_role("textbox", name="search Search").fill("")
    page.get_by_role("textbox", name="search Search").type(f"{sCleanID}")
    sleep(2)
    
    # Selects the technology ID from the search results
    page.get_by_role("row", name=sCleanID).get_by_role("link").nth(1).click()
