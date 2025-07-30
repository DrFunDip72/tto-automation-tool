import streamlit as st
import re
import time
import pandas as pd
import io
import zipfile

# --- 1. Session State Initialization ---
# We define all the variables the app will need to remember.
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

initialize_state()

# --- 2. Helper Functions ---
def extract_id(filename):
    """Extracts an ID like '2025-001' from a filename using regex."""
    match = re.search(r'(\d{4}-\d{3})', filename)
    if match:
        return match.group(1)
    return None

# --- 3. Placeholder Backend Functions ---
def fake_automation_process(pdf_file, image_file, tag_info):
    """Simulates the entire automation process for one PDF."""
    pdf_id = extract_id(pdf_file.name)
    st.write(f"  - Processing {pdf_id}...")
    time.sleep(1) # Simulate work
    
    # Simulate potential failure
    if "fail" in pdf_file.name.lower():
        raise ValueError("This PDF has a formatting error.")
        
    # Simulate creating a sell sheet PDF
    sell_sheet_content = f"This is the sell sheet for {pdf_id}.".encode('utf-8')
    return pdf_id, sell_sheet_content

# --- 4. The Streamlit User Interface ---
st.set_page_config(layout="wide", page_title="Automation Suite")
st.title("🚀 Company Automation Suite")

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
    if not all_checks_passed:
        st.error(f"Please resolve the following issues before running: {', '.join(validation_errors)}")

    if st.button("🚀 Run Automation", type="primary", use_container_width=True, disabled=not all_checks_passed):
        st.session_state.run_automation = True

    if st.session_state.run_automation:
        successes = []
        failures = []
        generated_sell_sheets = {} # Dict to store {filename: content}

        pdf_map = {extract_id(f.name): f for f in st.session_state.pdfs if extract_id(f.name)}
        img_map = {extract_id(f.name): f for f in st.session_state.images if extract_id(f.name)}
        
        progress_bar = st.progress(0, "Starting Automation...")
        total_files = len(st.session_state.pdfs)

        for i, pdf_file in enumerate(st.session_state.pdfs):
            pdf_id = extract_id(pdf_file.name)
            if not pdf_id:
                failures.append((pdf_file.name, "Could not extract a valid ID."))
                continue

            # Update progress bar
            progress_bar.progress((i + 1) / total_files, f"Processing: {pdf_file.name}")

            try:
                # Gather corresponding files and data
                image_file = img_map.get(pdf_id) if include_images else None
                tag_info = "Some Tag" # Replace with real lookup from st.session_state.tags_df
                
                # Run the main process
                processed_id, sell_sheet_bytes = fake_automation_process(pdf_file, image_file, tag_info)
                successes.append(processed_id)
                generated_sell_sheets[f"sell_sheet_{processed_id}.pdf"] = sell_sheet_bytes

            except Exception as e:
                failures.append((pdf_file.name, str(e)))
        
        progress_bar.empty()
        st.session_state.results = {"successes": successes, "failures": failures, "sell_sheets": generated_sell_sheets}

    # --- STAGE 4: RESULTS & DOWNLOAD ---
    if st.session_state.results:
        st.markdown("---")
        st.header("Step 4: Results")
        
        results = st.session_state.results
        st.subheader(f"Automation Complete: {len(results['successes'])} Succeeded, {len(results['failures'])} Failed")

        if results["failures"]:
            st.error("Encountered the following errors:")
            for name, error in results["failures"]:
                st.text(f"- {name}: {error}")
        
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
