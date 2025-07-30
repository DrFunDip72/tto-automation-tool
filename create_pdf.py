# Justin Maxwell - For TTO Website Overhaul Automation
# This code loops through and inserts the corresponding information into the sections to create a sell sheet
# exported as a pdf


# imports pdf functionality
from fpdf import FPDF
import os


# Modify the bullet point sections to use multi_cell instead of cell
def add_bulleted_section(pdf, section_title, items):
    pdf.set_font("NotoSans", style='B', size=12)
    pdf.cell(0, 10, section_title, ln=True)
    pdf.ln(1)  # Space after section
    pdf.set_font("NotoSans", size=12)
    
    bullet = '\u2022'.encode('cp1252').decode('latin1')
    for item in items:
        # Create horizontal space for bullet
        pdf.cell(4)  # Left margin spacer
        
        # Make bullet larger and bold
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(6, 6, bullet, ln=False)
        
        # Reset font for normal text and use multi_cell for wrapping
        pdf.set_font("NotoSans", size=12)
        
        # Use multi_cell with appropriate width and line height
        pdf.multi_cell(0, 6, item, align = 'L')
        
        # Add a small extra line break between bullet points
        pdf.ln(2)


# creates the function
def create_pdf(sTitle, sCleanID, sExectutiveStatement, sDescription, lstAdvantages, lstProblemsSolved, lstMarketApplications) :
    # creates the pdf
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Register Noto Sans Font
    # NOTE: the bullet points use "Arial" 
    pdf.add_font("NotoSans", "", "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Fonts/NotoSans-Regular.ttf",  uni=True)
    pdf.add_font("NotoSans", "B", "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Fonts/NotoSans-Bold.ttf", uni=True)  # Bold version
    

    # pulls and assigns variables
    sTitle = sTitle
    sID = f'ID: {sCleanID}' # formats the cleaned ID with "ID: "
    sExecutiveStatement = sExectutiveStatement
    sTechnologyOverview = sDescription
    lstAdvantages = lstAdvantages
    lstProblemsSolved = lstProblemsSolved
    lstMarketApplications = lstMarketApplications

    # Insert banner image at the top
    banner_path = "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Images/banner.png"
    pdf.image(banner_path, x=0, y=0, w=210)  # Adjust width to fit A4 page
    
    # Set overlay text on the banner
    pdf.set_xy(0, 15)  # Adjust position for overlay text
    pdf.set_text_color(255, 255, 255)  # White text color for contrast
    pdf.set_font("NotoSans", style='B', size=16)

    # Inserts the title text
    pdf.set_x(pdf.get_x() + 5) 
    pdf.cell(200, 10, sTitle, ln=True, align='C')
    
    # Inserts the ID text
    pdf.set_xy(0, 25)  # Adjust position for ID text
    pdf.set_font("NotoSans", size=13)
    pdf.cell(200, 10, sID, ln=True, align='C')

    
    pdf.ln(7.5)  # Space after banner section
    pdf.set_text_color(0, 0, 0)  # Reset text color to black
    
    # Executive Statement
    pdf.ln(4)
    pdf.set_font("NotoSans", style='B', size=12)
    pdf.cell(0, 10, "Executive Statement:", ln=True)
    pdf.set_font("NotoSans", size=12)
    pdf.multi_cell(0, 6, sExecutiveStatement, align='L')

    pdf.ln(2)  # Space after section
    
    # Technology Overview
    pdf.set_font("NotoSans", style='B', size=12)
    pdf.cell(0, 10, "Technology Overview:", ln=True)
    pdf.set_font("NotoSans", size=12)
    pdf.multi_cell(0, 6, sTechnologyOverview, align = 'L')
    
    pdf.ln(2.5)  # Space after section

    # These next three sections make the corresponding title (by calling the function at the top)
    # then loops through a list of sentences in a list and puts them on the page
    # with a bullet point before them (BULLETS use ARIAL)

    # Key Advantages
    add_bulleted_section(pdf, "Key Advantages:", lstAdvantages)
    pdf.ln(2.5)  # Space after section

    # Problems Solved
    add_bulleted_section(pdf, "Problems Addressed:", lstProblemsSolved)        
    pdf.ln(2.5)  # Space after section

    # Market Applications
    add_bulleted_section(pdf, "Market Applications:", lstMarketApplications)

    # Insert footer banner image at the bottom
    footer_banner_path = "C:/Users/justi/Desktop/Desktop/Justin/Coding Projects/Automation/Images/footer banner.png"  # Ensure the correct path
    footer_height = 20
    pdf.image(footer_banner_path, x=0, y= 290 - footer_height, w=210)  # Adjust width to fit A4 page

    # creates the proper output name
    sOutputName = sCleanID + " Sell Sheet.pdf" # Change this dynamically as needed

    # Exports the sell sheet into the Exported Sell Sheet folder
    # the folder to export to
    export_folder = r"C:\Users\justi\Desktop\Desktop\Justin\Coding Projects\Automation\Exported Sell Sheets"
    os.makedirs(export_folder, exist_ok=True)  # Ensure the folder exists

    # Combine folder path with output file name
    sTargetPDF = os.path.join(export_folder, sOutputName)

    # Saves the PDF using the sTargetPDF as the path with the output name
    pdf.output(sTargetPDF)
    return export_folder

