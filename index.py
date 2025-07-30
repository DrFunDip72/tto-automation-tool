# Justin Maxwell

# The home file to call all the other functions from the other python files

# IMPORTS
from playwright.sync_api import * # necessary playwright import
import logging
import glob, os # for file paths and getting file names
from user_input import *
from playwright_launcher import run # 
from first_ignite import *
from formatting_functions import *
from create_pdf import *
from brightspot_functions import *

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

# --- FILE PATH SETUP ---
disclosures_folder = r"C:\Users\justi\Desktop\Desktop\Justin\Coding Projects\Automation\Disclosures"
pdfFiles = glob.glob(os.path.join(disclosures_folder, "*.pdf"))


# --- IF RUNNING LARGE BATCHES, COMMENT OUT THE FOLLOWING LINES --- (confirm images uploaded and get user input for tag types)
# --- unless you want to do that for 50-100 files at a time

# -- CONFIRM PROPER IMAGE UPLOAD TO IMAGES FOLDER ---
# confirm_images_uploaded()

# --- GETS USER INPUT FOR TAG TYPES --- 
# tagTypeSelections = get_user_selections(disclosures_folder)

# --- GETS USER INPUT FOR BRIGHTSPOT LOGIN ---
# --- you can hardcode your username and password here if you want to
# --- but it's not recommended for security reasons
userUsername = ""
userPassword = ""
userUsername, userPassword = input("Enter your BYU Net ID: "), input("Enter your BYU password: ")

# --- PLAYWRIGHT SESSION ---
with sync_playwright() as p:
    browser, page = run(p)

    for filePath in pdfFiles:
        try:
            # # --- GET CLEAN ID ---
            sFileName = os.path.basename(filePath)
            sCleanID = get_clean_id(sFileName)

            # --- FIRST IGNITE ---
            try:
                page = browser.new_page()
                page.goto("https://app.firstignite.com/autopilot")
                sleep(2)
                extractedSummaryText = launch_first_ignite(page, filePath)
            except Exception as e:
                logging.warning(f"{sCleanID} - launch_first_ignite failed: {str(e)}")
                continue
              
            # # --- DATA EXTRACTION & PDF CREATION ---
            try:
                sTitle, sExecutiveStatement, sDescription, lstAdvantages, lstProblemsSolved, lstMarketApplications = format_summary(extractedSummaryText)
                exportFolder = create_pdf(sTitle, sCleanID, sExecutiveStatement, sDescription, lstAdvantages, lstProblemsSolved, lstMarketApplications)
            except Exception as e:
                logging.warning(f"{sCleanID} - format_summary or create_pdf failed: {str(e)}")
                continue  # Skip this file if critical data missing

            # --- FOR TESTING WHEN COMMENTING OUT THE ABOVE FUNCTION --- 
            # This is so you don't have to run the first ignite function every time to debug and test
            # sCleanID = "2025-001"
            # sTitle = 'Constitutively Active Death Receptor (CADRE)'
            # sExecutiveStatement = 'A revolutionary anticancer therapeutic designed to specifically induce apoptosis in cancer cells.'
            # sDescription = 'The Constitutively Active Death Receptor (CADRE) represents a novel approach to cancer therapy, utilizing a modified death receptor that triggers apoptosis directly within cancer cells, bypassing common resistance mechanisms. This technology leverages a unique amino acid sequence and delivery system to target cancer cells selectively, minimizing harm to normal cells.'
            # lstAdvantages = ['High specificity to cancer cells, reducing potential side effects', 'Overcomes resistance mechanisms present in traditional therapies', 'Applicability across a broad range of cancer types', 'Potential to complement existing treatments like chemotherapy and radiotherapy', 'Innovative delivery methods using bacterial vesicles and p', 'H-sensitive peptides enhance targeting capabilities']
            # lstProblemsSolved = ['Resistance to traditional cancer therapies such as chemotherapy and radiotherapy', 'Non-specific targeting of cancer cells, leading to damage of healthy cells and tissues', 'Limited efficacy of current treatments across diverse cancer types']
            # lstMarketApplications = ['Novel anticancer therapeutics', 'Complementary treatment to enhance efficacy of existing cancer therapies', 'Targeted cancer therapy research and development', 'Potential for personalized cancer treatment strategies']
            # exportFolder = r"C:\Users\justi\Desktop\Desktop\Justin\Coding Projects\Automation\Exported Sell Sheets"
            # sTypeTag = "Engineered Structures & Materials"

            # --- BRIGHTSPOT WORKFLOW ---
            try:
                page.goto("https://brightspot.byu.edu/cms/logIn.jsp?returnPath=%2Fcms%2Findex.jsp")
                sleep(3)
                bs_login(page, userUsername, userPassword)
            except Exception as e:
                logging.warning(f"{sCleanID} - bs_login failed: {str(e)}")
                continue  # Can't continue without login

            # --- SEARCH FOR TECHNOLOGY ---
            # Uncomment this if you want to search for the technology (if going back to change things --> like type tags or images)
            # Then comment out the bs_template_click function --> that way it searches for the technology rather than clicking on the template
            # try_function(bs_search_technology, page, sCleanID=sCleanID, func_name="bs_search_technology")

            # --- BRIGHTSPOT FUNCTIONS (INDIVIDUAL TRY) ---
            try_function(bs_template_click, page, sCleanID=sCleanID, func_name="bs_template_click")
            try_function(bs_display_internal_name, page, sTitle, sCleanID, sCleanID=sCleanID, func_name="bs_display_internal_name")
            try_function(bs_title_techID, page, sTitle, sCleanID, sCleanID=sCleanID, func_name="bs_title_techID")
            try_function(bs_executive_statement, page, sExecutiveStatement, sCleanID=sCleanID, func_name="bs_executive_statement")
            # try_function(bs_image_main_page, page, sCleanID, sCleanID=sCleanID, func_name="bs_image_main_page") --> I comment this out when running large batches because I don't have all the photos
            try_function(bs_technology_overview, page, sDescription, sCleanID=sCleanID, func_name="bs_technology_overview")
            try_function(bs_key_advantages, page, lstAdvantages, sCleanID=sCleanID, func_name="bs_key_advantages")
            try_function(bs_problems_addressed, page, lstProblemsSolved, sCleanID=sCleanID, func_name="bs_problems_addressed")
            try_function(bs_market_applications, page, lstMarketApplications, sCleanID=sCleanID, func_name="bs_market_applications")
            try_function(bs_additional_information, page, sCleanID, sCleanID=sCleanID, func_name="bs_additional_information")
            try_function(bs_upload_pdf, page, sCleanID, exportFolder, sCleanID=sCleanID, func_name="bs_upload_pdf")
            try_function(bs_year_tag, page, sCleanID, sCleanID=sCleanID, func_name="bs_year_tag")
            # try_function(bs_type_tag, page, sCleanID, tagTypeSelections, sCleanID=sCleanID, func_name="bs_type_tag") --> I comment this out when running large batches because I don't have all the tags
            try_function(bs_contact_link, page, sCleanID=sCleanID, func_name="bs_contact_link")
            try_function(bs_override_description, page, sCleanID, sCleanID=sCleanID, func_name="bs_override_description")
            # try_function(bs_override_image, page, sCleanID, sCleanID=sCleanID, func_name="bs_override_image") --> I comment this out when running large batches because I don't have all the photos
            try_function(bs_publish, page, sCleanID=sCleanID, func_name="bs_publish")

            # Closes the page
            page.close()
  
        except Exception as e:
            # Catches if anything fatally wrong happens per disclosure
            logging.warning(f"{sCleanID} - Fatal error in main loop: {str(e)}")
            page.close()
