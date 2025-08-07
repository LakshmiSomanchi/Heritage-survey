import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
import shutil
import zipfile
import io
import time

SAVE_DIR = 'survey_responses'
os.makedirs(SAVE_DIR, exist_ok=True)

DRAFT_DIR = os.path.join(SAVE_DIR, 'drafts')
os.makedirs(DRAFT_DIR, exist_ok=True)

TEMP_IMAGE_DIR = os.path.join(SAVE_DIR, 'temp_images')
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

FINAL_IMAGE_DIR = os.path.join(SAVE_DIR, 'final_images')
os.makedirs(FINAL_IMAGE_DIR, exist_ok=True)

st.set_page_config(page_title="Heritage Dairy Survey", page_icon="🐄", layout="centered")

# --- Initializing all session state variables at the beginning ---
# This block should be one of the first things to run in your app
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'form_entry'
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'final_submitted_data' not in st.session_state:
    st.session_state.final_submitted_data = {}
if 'uploaded_temp_photo_paths' not in st.session_state:
    st.session_state.uploaded_temp_photo_paths = []
if 'draft_saved' not in st.session_state:
    st.session_state.draft_saved = False
if 'last_saved_time_persistent' not in st.session_state:
    st.session_state.last_saved_time_persistent = None
# This is the line that was causing the error - let's make sure it's here
if 'all_responses_df' not in st.session_state:
    st.session_state.all_responses_df = pd.DataFrame()

# --- Dictionaries and Options (Replicating your existing code) ---
dict_translations = {
    "Surveyor": "Surveyor Name", "Date": "Date of Visit", "HPC Code": "HPC Code", "HPC Name": "HPC Name", "Farmer Code": "Farmer Code", "Farmer Name": "Farmer Name", "Mobile Number": "Mobile Number", "Milk Yield (LPD)": "Milk Yield (LPD)", "Last Calving Date": "Last Calving Date", "Cattle Breed": "Cattle Breed", "Total Cows": "Total Cows", "Cows in Milk": "Cows in Milk", "Dry Cows": "Dry Cows", "Heifers": "Heifers", "Calves": "Calves", "Fat (%)": "Fat (%)", "SNF (%)": "SNF (%)", "Protein (%)": "Protein (%)", "TDS (%)": "TDS (%)", "Green Fodder": "Green Fodder (Yes/No)", "Green Fodder Source": "Source of Green Fodder", "Dry Fodder": "Dry Fodder (Yes/No)", "Dry Fodder Source": "Source of Dry Fodder", "Concentrated Feed": "Concentrated Feed (Yes/No)", "Feed Brand": "Brand of Feed", "Mineral Mixture": "Mineral Mixture (Yes/No)", "Mineral Mixture Brand": "Brand of Mineral Mixture", "Other Feed": "Other Feed (if any)", "Any Disease Outbreak": "Any Disease Outbreak (Yes/No)", "Disease Name": "Name of Disease", "Veterinary Visit": "Veterinary Visit (Yes/No)", "Last Vet Visit Date": "Last Vet Visit Date", "AI/Services": "AI/Services (Yes/No)", "Last AI Date": "Last AI Date", "Manure Management": "Manure Management (Yes/No)", "Shed Type": "Shed Type", "Water Source": "Water Source", "Photos": "Photos", "Key Insights": "Key Insights"
}
FARMER_LOOKUP = {
    "FARMER001": {"name": "Ram Patil", "mobile": "9876543210"},
    "FARMER002": {"name": "Sita Desai", "mobile": "9988776655"},
    "FARMER003": {"name": "Laxman Rao", "mobile": "9012345678"}
}
options = {
    "Surveyor": ["Guru", "Balaji", "Nilesh", "Aniket"],
    "HPC Code": ["HPC001", "HPC002", "HPC003"],
    "Cattle Breed": ["Jersey", "HF", "Gir", "Sahiwal", "Crossbred"],
    "Green Fodder": ["Yes", "No"], "Dry Fodder": ["Yes", "No"],
    "Concentrated Feed": ["Yes", "No"], "Mineral Mixture": ["Yes", "No"],
    "Any Disease Outbreak": ["Yes", "No"], "Veterinary Visit": ["Yes", "No"],
    "AI/Services": ["Yes", "No"], "Manure Management": ["Yes", "No"],
    "Shed Type": ["Pukka", "Kutcha", "No Shed"], "Water Source": ["Borewell", "River", "Tap Water", "Other"]
}
initial_values_defaults = {
    "Surveyor": options['Surveyor'][0], "HPC Code": options['HPC Code'][0],
    "Farmer Code": list(FARMER_LOOKUP.keys())[0], "Cattle Breed": options['Cattle Breed'][0],
    "Date": datetime.date.today().strftime('%Y-%m-%d')
}
labels = {
    "Surveyor": "Surveyor Name", "Date": "Date of Visit", "HPC Code": "HPC Code",
    "HPC Name": "HPC Name", "Farmer Code": "Farmer Code", "Farmer Name": "Farmer Name",
    "Mobile Number": "Mobile Number", "Last Calving Date": "Last Calving Date",
    "Cattle Breed": "Cattle Breed", "Total Cows": "Total Cows",
    "Cows in Milk": "Cows in Milk", "Dry Cows": "Dry Cows", "Heifers": "Heifers",
    "Calves": "Calves", "Milk Yield (LPD)": "Milk Yield (LPD)", "Fat (%)": "Fat (%)",
    "SNF (%)": "SNF (%)", "Protein (%)": "Protein (%)", "TDS (%)": "TDS (%)",
    "Green Fodder": "Green Fodder Available?",
    "Green Fodder Source": "Source of Green Fodder (e.g., silage, maize, etc.)",
    "Dry Fodder": "Dry Fodder Available?",
    "Dry Fodder Source": "Source of Dry Fodder (e.g., sugarcane tops, jowar, etc.)",
    "Concentrated Feed": "Concentrated Feed Used?", "Feed Brand": "Brand of Feed",
    "Mineral Mixture": "Mineral Mixture Used?", "Mineral Mixture Brand": "Brand of Mineral Mixture",
    "Other Feed": "Other Feed (if any)",
    "Any Disease Outbreak": "Any Disease Outbreak?", "Disease Name": "Name of Disease",
    "Veterinary Visit": "Veterinary Visit?", "Last Vet Visit Date": "Last Vet Visit Date",
    "AI/Services": "AI/Services Availed?", "Last AI Date": "Last AI Date",
    "Manure Management": "Manure Management Practice?", "Shed Type": "Shed Type",
    "Water Source": "Water Source", "Key Insights": "Key Insights/Observations",
    "Upload Photos": "Upload Photos",
    "Review Your Submission": "Review Your Submission",
    "Confirm and Submit": "Confirm and Submit", "Edit Form": "Edit Form",
    "Successfully Submitted!": "Successfully Submitted!",
    "Fill Another Form": "Fill Another Form",
    "Download All Responses (CSV)": "Download All Responses (CSV)",
    "Download All Responses (Excel)": "Download All Responses (Excel)",
    "Download All Photos (ZIP)": "Download All Photos (ZIP)"
}
# --- End of Replicated Code ---

def load_all_data():
    master_file = os.path.join(SAVE_DIR, "survey_responses_master.csv")
    if not os.path.exists(master_file):
        return pd.DataFrame()
    try:
        return pd.read_csv(master_file)
    except Exception as e:
        st.warning(f"Could not read {master_file}: {e}")
        return pd.DataFrame()

# Data loading on app start: This loads the data into session state
if st.session_state.all_responses_df.empty:
    st.session_state.all_responses_df = load_all_data()

def get_all_responses_df():
    return st.session_state.all_responses_df

# ... [all other functions unchanged] ...

if st.session_state.current_step == 'review':
    st.title(labels['Review Your Submission'])
    st.write("Please review the information below before final submission.")

    data_to_review = st.session_state.final_submitted_data

    if data_to_review:
        # --- Display review (replicated for context) ---
        for key, value in data_to_review.items():
            st.markdown(f"**{dict_translations.get(key, key)}:** {value}")
        
        st.write("---")
        st.subheader("Uploaded Photos")
        if st.session_state.uploaded_temp_photo_paths:
            for photo_path in st.session_state.uploaded_temp_photo_paths:
                if os.path.exists(photo_path):
                    with open(photo_path, "rb") as image_file:
                        st.image(image_file.read(), caption=os.path.basename(photo_path), width=300)
                else:
                    st.warning(f"Photo not found: {os.path.basename(photo_path)}")
        else:
            st.info("No photos uploaded.")
        # --- End of review display ---
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(labels['Confirm and Submit'], key="confirm_submit_button"):
                final_photo_paths = []
                for temp_path in st.session_state.uploaded_temp_photo_paths:
                    if os.path.exists(temp_path):
                        final_image_name = os.path.basename(temp_path)
                        final_path = os.path.join(FINAL_IMAGE_DIR, final_image_name)
                        try:
                            shutil.move(temp_path, final_path)
                            final_photo_paths.append(final_path)
                        except Exception as e:
                            st.error(f"Error moving photo {os.path.basename(temp_path)}: {e}")
                            final_photo_paths.append(temp_path)
                    else:
                        st.warning(f"Temporary photo {os.path.basename(temp_path)} not found during final submission. Skipping.")

                data_to_review["Photo Paths"] = ", ".join(final_photo_paths)
                
                # Convert the single submission to a DataFrame
                df_new_entry = pd.DataFrame([data_to_review])

                # Append to master file
                master_file = os.path.join(SAVE_DIR, "survey_responses_master.csv")
                try:
                    file_exists = os.path.exists(master_file)
                    df_new_entry.to_csv(master_file, mode='a', header=not file_exists, index=False)
                    
                    # Update session state DataFrame for real-time reflection
                    if not st.session_state.all_responses_df.empty:
                        st.session_state.all_responses_df = pd.concat([st.session_state.all_responses_df, df_new_entry], ignore_index=True)
                    else:
                        st.session_state.all_responses_df = df_new_entry
                    
                    st.session_state.current_step = 'submitted'
                    st.session_state.last_saved_time_persistent = None
                    
                    # Clean up temporary images
                    for f in os.listdir(TEMP_IMAGE_DIR):
                        os.remove(os.path.join(TEMP_IMAGE_DIR, f))
                    st.session_state.uploaded_temp_photo_paths = []

                    # Clean up draft file
                    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
                    if os.path.exists(draft_filename):
                        os.remove(draft_filename)

                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving data: {e}")
        with col2:
            if st.button(labels['Edit Form'], key="edit_form_button"):
                st.session_state.current_step = 'form_entry'
                st.rerun()
    else:
        st.warning("No data found to review. Please go back and fill the form.")
        if st.button(labels['Edit Form']):
            st.session_state.current_step = 'form_entry'
            st.rerun()

elif st.session_state.current_step == 'submitted':
    st.balloons()
    st.success(labels['Successfully Submitted!'])
    st.write("Thank you for your submission!")
    if st.button(labels['Fill Another Form']):
        st.session_state.form_data = initial_values_defaults.copy()
        st.session_state.uploaded_temp_photo_paths = []
        st.session_state.current_step = 'form_entry'
        st.rerun()

# --- Sidebar for Download Options ---
st.sidebar.markdown("---")
st.sidebar.header("Download Options")

all_responses_df = get_all_responses_df()
if not all_responses_df.empty:
    csv_data = all_responses_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label=labels['Download All Responses (CSV)'],
        data=csv_data,
        file_name="all_survey_responses.csv",
        mime="text/csv",
        key="download_all_csv"
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        all_responses_df.to_excel(writer, index=False, sheet_name='SurveyResponses')
    excel_buffer.seek(0)
    st.sidebar.download_button(
        label=labels['Download All Responses (Excel)'],
        data=excel_buffer.getvalue(),
        file_name="all_survey_responses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_all_excel"
    )
else:
    st.sidebar.info("No survey responses available for download (CSV/Excel).")

def create_zip_file():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(FINAL_IMAGE_DIR):
            for file in files:
                zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), FINAL_IMAGE_DIR))
    zip_buffer.seek(0)
    return zip_buffer

if os.path.exists(FINAL_IMAGE_DIR) and os.listdir(FINAL_IMAGE_DIR):
    zip_buffer = create_zip_file()
    st.sidebar.download_button(
        label=labels['Download All Photos (ZIP)'],
        data=zip_buffer,
        file_name="all_survey_photos.zip",
        mime="application/zip",
        key="download_all_photos_zip"
    )
else:
    st.sidebar.info("No photos available for download (ZIP).")
