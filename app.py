import streamlit as st
import re
import time
import pandas as pd
import io
import zipfile
import tempfile
import os
import logging
import subprocess
import sys
import platform
import asyncio
from pathlib import Path

# Import automation functions
from playwright.sync_api import sync_playwright
from playwright_launcher import run
from first_ignite import launch_first_ignite
from formatting_functions import get_clean_id, format_summary
from create_pdf import create_pdf
from brightspot_functions import *

# --- 1. Session State Initialization ---
def initialize_state():
    if 'pdfs' not in st.session_state:
        st.session_state.pdfs = []
    if 'images' not in st.session_state:
        st.session_state.images = []
    if 'tags_df' not in st.session_state:
        st.session_state.tags_df = None
    if 'run_automation' not in st.session_state:
        st.session_state.run_automation = False
    if 'results' not in st.session_state:
        st.session_state.results = {}
    if 'cancel_processing' not in st.session_state:
        st.session_state.cancel_processing = False
    if 'playwright_installed' not in st.session_state:
        st.session_state.playwright_installed = False

initialize_state()

# --- 2. Helper Functions ---
def install_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    try:
        # Check if browsers are already installed
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Try to launch browser - if it works, browsers are installed
            browser = p.chromium.launch(headless=True)
            browser.close()
            return True
    except Exception:
        # Browsers not installed, install them
        st.info("🔄 Installing Playwright browsers... This may take a few minutes on first run.")
        
        try:
            # Install browsers using subprocess
            result = subprocess.run([
                sys.executable, "-m", "playwright", "install", "chromium"
            ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode == 0:
                st.success("✅ Playwright browsers installed successfully!")
                return True
            else:
                st.error(f"❌ Failed to install browsers: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            st.error("❌ Browser installation timed out. Please try again.")
            return False
        except Exception as e:
            st.error(f"❌ Error installing browsers: {str(e)}")
            return False

def extract_id(filename):
    """Extracts an ID like '2025-001' from a filename using regex."""
    match = re.search(r'(\d{4}-\d{3})', filename)
    if match:
        return match.group(1)
    return None

def save_uploaded_file(uploaded_file, temp_dir):
    """Save uploaded file to temporary directory and return path."""
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def get_error_message(func_name, error):
    """Convert function names to user-friendly error messages."""
    error_messages = {
        "launch_first_ignite": "Failed to extract data from FirstIgnite - the disclosure may not be compatible or the service may be unavailable",
        "format_summary": "Failed to parse the extracted data - the disclosure format may be incorrect",
        "create_pdf": "Failed to generate the sell sheet PDF - there may be an issue with the data or formatting",
        "bs_login": "Failed to log into Brightspot - please check your credentials",
        "bs_template_click": "Failed to access the technology template in Brightspot",
        "bs_display_internal_name": "Failed to set the technology name in Brightspot",
        "bs_title_techID": "Failed to set the technology title and ID in Brightspot",
        "bs_executive_statement": "Failed to set the executive statement in Brightspot",
        "bs_technology_overview": "Failed to set the technology overview in Brightspot",
        "bs_key_advantages": "Failed to set the key advantages in Brightspot",
        "bs_problems_addressed": "Failed to set the problems addressed in Brightspot",
        "bs_market_applications": "Failed to set the market applications in Brightspot",
        "bs_additional_information": "Failed to set additional information in Brightspot",
        "bs_upload_pdf": "Failed to upload the sell sheet PDF to Brightspot",
        "bs_year_tag": "Failed to set the year tag in Brightspot",
        "bs_contact_link": "Failed to set the contact link in Brightspot",
        "bs_override_description": "Failed to update the override description in Brightspot",
        "bs_publish": "Failed to publish the technology page in Brightspot"
    }
    
    base_message = error_messages.get(func_name, f"Failed during {func_name}")
    return f"{base_message}. Error: {str(error)}"

def try_function(func, *args, sCleanID="", func_name="", **kwargs):
    """Tries a function call, returns error message if it fails."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_message = get_error_message(func_name, e)
        logging.warning(f"{sCleanID} - {func_name} failed: {str(e)}")
        return error_message

# --- 3. Main Automation Function ---
def run_automation_process(pdf_files, image_files, tag_df, progress_bar, status_text):
    """Main automation process that runs the entire workflow."""
    successes = []
    failures = []
    generated_sell_sheets = {}
    
    # Create temporary directory for files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded files to temp directory
        pdf_paths = {}
        image_paths = {}
        
        for pdf_file in pdf_files:
            pdf_id = extract_id(pdf_file.name)
            if pdf_id:
                pdf_paths[pdf_id] = save_uploaded_file(pdf_file, temp_dir)
        
        for image_file in image_files:
            image_id = extract_id(image_file.name)
            if image_id:
                image_paths[image_id] = save_uploaded_file(image_file, temp_dir)
        
        # Set up paths for PDF generation
        banner_path = "Images/banner.png"
        footer_banner_path = "Images/footer banner.png"
        export_folder = temp_dir
        
        # Use your existing playwright_launcher
        with sync_playwright() as p:
            browser, context, page = run(p)  # Use your existing launcher
            
            # Create tabs using the same context
            firstignite_page = context.new_page()
            firstignite_page.goto("https://app.firstignite.com/autopilot")
            
            brightspot_page = context.new_page()
            brightspot_page.goto("https://brightspot.byu.edu/cms/logIn.jsp?returnPath=%2Fcms%2Findex.jsp")
            
            time.sleep(75)
            st.success("✅ Login complete! Starting automation for all files...")
            
            # Process each PDF file
            for i, pdf_file in enumerate(pdf_files):
                if st.session_state.cancel_processing:
                    break
                
                pdf_id = extract_id(pdf_file.name)
                if not pdf_id:
                    error_msg = "Could not extract a valid ID from filename"
                    failures.append((pdf_file.name, error_msg))
                    st.error(f"❌ {pdf_file.name}: {error_msg}")
                    continue
                
                # Update progress
                progress = (i + 1) / len(pdf_files)
                progress_bar.progress(progress, f"Processing file {i + 1} of {len(pdf_files)}")
                status_text.text(f"Processing: {pdf_file.name} ({pdf_id})")
                
                file_errors = []
                current_step = 1
                total_steps = 5
                
                try:
                    # Step 1: FirstIgnite Data Extraction
                    st.write(f"📄 **{pdf_id}** - Step {current_step}/{total_steps}: Extracting data from FirstIgnite...")
                    current_step += 1
                    
                    extracted_summary = try_function(
                        launch_first_ignite, firstignite_page, pdf_paths[pdf_id], 
                        sCleanID=pdf_id, func_name="launch_first_ignite"
                    )
                    
                    if isinstance(extracted_summary, str) and extracted_summary.startswith("Failed"):
                        file_errors.append(extracted_summary)
                        st.error(f"❌ {pdf_id}: {extracted_summary}")
                        continue
                    
                    st.success(f"✅ {pdf_id}: FirstIgnite data extracted successfully")
                    
                    # Step 2: Data Formatting
                    st.write(f"📄 **{pdf_id}** - Step {current_step}/{total_steps}: Formatting data...")
                    current_step += 1
                    
                    formatted_data = try_function(
                        format_summary, extracted_summary,
                        sCleanID=pdf_id, func_name="format_summary"
                    )
                    
                    if isinstance(formatted_data, str) and formatted_data.startswith("Failed"):
                        file_errors.append(formatted_data)
                        st.error(f"❌ {pdf_id}: {formatted_data}")
                        continue
                    
                    sTitle, sExecutiveStatement, sDescription, lstAdvantages, lstProblemsSolved, lstMarketApplications = formatted_data
                    st.success(f"✅ {pdf_id}: Data formatted successfully")
                    
                    # Step 3: PDF Creation
                    st.write(f"📄 **{pdf_id}** - Step {current_step}/{total_steps}: Creating PDF...")
                    current_step += 1
                    
                    pdf_result = try_function(
                        create_pdf, sTitle, pdf_id, sExecutiveStatement, sDescription, 
                        lstAdvantages, lstProblemsSolved, lstMarketApplications,
                        banner_path, footer_banner_path, export_folder,  # ← Added these 3 parameters
                        sCleanID=pdf_id, func_name="create_pdf"
                    )
                    
                    if isinstance(pdf_result, str) and pdf_result.startswith("Failed"):
                        file_errors.append(pdf_result)
                        st.error(f"❌ {pdf_id}: {pdf_result}")
                        continue
                    
                    # Read the generated PDF
                    pdf_path = os.path.join(export_folder, f"{pdf_id}_sell_sheet.pdf")
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        generated_sell_sheets[f"sell_sheet_{pdf_id}.pdf"] = pdf_bytes
                        st.success(f"✅ {pdf_id}: PDF created successfully")
                    else:
                        file_errors.append("PDF file was not created")
                        st.error(f"❌ {pdf_id}: PDF file was not created")
                        continue
                    
                    # Step 4: Brightspot Integration
                    st.write(f"📄 **{pdf_id}** - Step {current_step}/{total_steps}: Processing in Brightspot...")
                    current_step += 1
                    
                    # Brightspot functions with detailed error reporting
                    brightspot_functions = [
                        (bs_template_click, "bs_template_click", "Clicking template"),
                        (bs_display_internal_name, "bs_display_internal_name", "Setting technology name", brightspot_page, sTitle, pdf_id),
                        (bs_title_techID, "bs_title_techID", "Setting title and ID", brightspot_page, sTitle, pdf_id),
                        (bs_executive_statement, "bs_executive_statement", "Setting executive statement", brightspot_page, sExecutiveStatement),
                        (bs_technology_overview, "bs_technology_overview", "Setting technology overview", brightspot_page, sDescription),
                        (bs_key_advantages, "bs_key_advantages", "Setting key advantages", brightspot_page, lstAdvantages),
                        (bs_problems_addressed, "bs_problems_addressed", "Setting problems addressed", brightspot_page, lstProblemsSolved),
                        (bs_market_applications, "bs_market_applications", "Setting market applications", brightspot_page, lstMarketApplications),
                        (bs_additional_information, "bs_additional_information", "Setting additional information", brightspot_page, pdf_id),
                        (bs_upload_pdf, "bs_upload_pdf", "Uploading PDF", brightspot_page, pdf_id, export_folder),
                        (bs_year_tag, "bs_year_tag", "Setting year tag", brightspot_page, pdf_id),
                        (bs_contact_link, "bs_contact_link", "Setting contact link", brightspot_page),
                        (bs_override_description, "bs_override_description", "Setting override description", brightspot_page, pdf_id),
                        (bs_publish, "bs_publish", "Publishing page", brightspot_page)
                    ]
                    
                    brightspot_success = True
                    for func_info in brightspot_functions:
                        if len(func_info) == 3:
                            func, func_name, step_desc = func_info
                            st.write(f"📄 **{pdf_id}** - {step_desc}...")
                            error = try_function(func, brightspot_page, sCleanID=pdf_id, func_name=func_name)
                        else:
                            func, func_name, step_desc, *args = func_info
                            st.write(f"📄 **{pdf_id}** - {step_desc}...")
                            error = try_function(func, *args, sCleanID=pdf_id, func_name=func_name)
                        
                        if isinstance(error, str) and error.startswith("Failed"):
                            file_errors.append(error)
                            st.error(f"❌ {pdf_id}: {error}")
                            brightspot_success = False
                            break
                        else:
                            st.success(f"✅ {pdf_id}: {step_desc} completed")
                    
                    # Step 5: Final Status
                    st.write(f"📄 **{pdf_id}** - Step {current_step}/{total_steps}: Finalizing...")
                    
                    # Check if any errors occurred
                    if file_errors:
                        failures.append((pdf_file.name, " | ".join(file_errors)))
                        st.error(f"❌ {pdf_id}: Processing failed")
                    else:
                        successes.append(pdf_id)
                        st.success(f"✅ {pdf_id}: Processing completed successfully!")
                        
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    failures.append((pdf_file.name, error_msg))
                    st.error(f"❌ {pdf_id}: {error_msg}")
            
            browser.close()
    
    return successes, failures, generated_sell_sheets

# --- 4. The Streamlit User Interface ---
st.set_page_config(layout="wide", page_title="TTO Automation Suite")
st.title("🚀 TTO Automation Suite")

# Check if Playwright browsers are installed
if not st.session_state.playwright_installed:
    st.session_state.playwright_installed = install_playwright_browsers()

# --- STAGE 1: PDF UPLOAD ---
st.header("Step 1: Upload PDFs")
uploaded_pdfs = st.file_uploader(
    "Drag and drop all your PDF files here.",
    accept_multiple_files=True,
    type="pdf"
)
if uploaded_pdfs:
    st.session_state.pdfs = uploaded_pdfs
    st.success(f"{len(st.session_state.pdfs)} PDF(s) uploaded successfully.")

# Only proceed if PDFs have been uploaded
if st.session_state.pdfs:
    st.markdown("---")
    
    # --- STAGE 2: CONFIGURATION ---
    st.header("Step 2: Configure Optional Files")
    
    all_checks_passed = True
    validation_errors = []

    # --- Image Matching Logic ---
    include_images = st.toggle("Upload matching images?", key="image_toggle")
    if include_images:
        uploaded_images = st.file_uploader(
            "Upload corresponding images for the PDFs.",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg']
        )
        if uploaded_images:
            st.session_state.images = uploaded_images
            
            pdf_ids = {extract_id(f.name) for f in st.session_state.pdfs if extract_id(f.name)}
            image_ids = {extract_id(f.name) for f in st.session_state.images if extract_id(f.name)}
            
            missing_images = pdf_ids - image_ids
            extra_images = image_ids - pdf_ids
            
            if not missing_images and not extra_images:
                st.success("✅ All PDFs have a matching image.")
            else:
                all_checks_passed = False
                if missing_images:
                    st.warning("The following PDFs are missing an image:")
                    st.json(sorted(list(missing_images)))
                    validation_errors.append("Fix missing images.")
                if extra_images:
                    st.warning("The following images do not have a matching PDF:")
                    st.json(sorted(list(extra_images)))
                    validation_errors.append("Remove extra images.")
        else:
            all_checks_passed = False
            validation_errors.append("Upload images or turn off the image toggle.")

    # --- Tag Matching Logic ---
    include_tags = st.toggle("Upload a tag file?", key="tag_toggle")
    if include_tags:
        tag_file = st.file_uploader(
            "Upload a CSV or Excel file with 'ID' and 'Tag' columns.",
            type=['csv', 'xlsx']
        )
        if tag_file:
            try:
                if tag_file.name.endswith('.csv'):
                    st.session_state.tags_df = pd.read_csv(tag_file)
                else:
                    st.session_state.tags_df = pd.read_excel(tag_file)
                
                # Validation
                tag_ids = set(st.session_state.tags_df['ID'].astype(str))
                pdf_ids = {extract_id(f.name) for f in st.session_state.pdfs if extract_id(f.name)}
                
                missing_tags = pdf_ids - tag_ids
                if not missing_tags:
                    st.success("✅ All PDFs have a matching tag in the file.")
                else:
                    all_checks_passed = False
                    validation_errors.append("Fix missing tags in your file.")
                    st.warning("The following PDFs are missing a tag. Please fix your file and re-upload.")
                    st.json(sorted(list(missing_tags)))

            except Exception as e:
                all_checks_passed = False
                validation_errors.append("The tag file could not be read.")
                st.error(f"Error reading tag file: {e}")
        else:
            all_checks_passed = False
            validation_errors.append("Upload a tag file or turn off the tag toggle.")

    st.markdown("---")

    # --- STAGE 3: EXECUTION ---
    st.header("Step 3: Run Automation")
    
    # Check if Playwright is ready
    if not st.session_state.playwright_installed:
        st.error("Playwright browsers are not installed. Please wait for installation to complete or refresh the page.")
        all_checks_passed = False
    
    if not all_checks_passed:
        st.error(f"Please resolve the following issues before running: {', '.join(validation_errors)}")

    # Manual login instructions
    st.info("""
    **Important:** The browser will open with two tabs and you'll need to login to both services.
    
    1. **Brightspot Login**: Login to Brightspot in the first tab (used for all files)
    2. **FirstIgnite Login**: Login to FirstIgnite in the second tab (used for all files)
    3. **Don't close the browser** - the automation will continue automatically
    4. **Each login has 60 seconds** - complete your login within this time
    5. **After login, all files will be processed automatically**
    """)

    # Run button and cancel button
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🚀 Run Automation", type="primary", use_container_width=True, disabled=not all_checks_passed):
            st.session_state.run_automation = True
            st.session_state.cancel_processing = False
    with col2:
        if st.button("❌ Cancel", type="secondary", use_container_width=True):
            st.session_state.cancel_processing = True

    if st.session_state.run_automation:
        # Create progress indicators
        progress_bar = st.progress(0, "Starting Automation...")
        status_text = st.empty()
        
        # Run the automation
        successes, failures, generated_sell_sheets = run_automation_process(
            st.session_state.pdfs,
            st.session_state.images if include_images else [],
            st.session_state.tags_df if include_tags else None,
            progress_bar,
            status_text
        )
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Store results
        st.session_state.results = {
            "successes": successes, 
            "failures": failures, 
            "sell_sheets": generated_sell_sheets
        }

    # --- STAGE 4: RESULTS & DOWNLOAD ---
    if st.session_state.results:
        st.markdown("---")
        st.header("Step 4: Results")
        
        results = st.session_state.results
        st.subheader(f"Automation Complete: {len(results['successes'])} Succeeded, {len(results['failures'])} Failed")

        if results["failures"]:
            st.error("Encountered the following errors:")
            for name, error in results["failures"]:
                with st.expander(f"❌ {name}"):
                    st.text(error)
        
        if results["sell_sheets"]:
            st.subheader("Download Sell Sheets")
            
            # Create a zip file in memory
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for filename, content in results["sell_sheets"].items():
                    zf.writestr(filename, content)
            
            st.download_button(
                label="⬇️ Download All Sell Sheets (.zip)",
                data=zip_buffer.getvalue(),
                file_name="sell_sheets.zip",
                mime="application/zip",
                use_container_width=True
            )

        st.markdown("---")
        st.info("To start a new automation, please refresh this page (F5 or Cmd+R).")
