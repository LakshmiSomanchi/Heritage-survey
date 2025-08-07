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


### New Code for Form Entry

if st.session_state.current_step == 'form_entry':
    st.title("Heritage Dairy Survey 🐄")
    st.write("Please fill out the survey form below.")

    # A simple function to save draft data
    def save_draft():
        with open(os.path.join(DRAFT_DIR, "current_draft.json"), "w") as f:
            json.dump(st.session_state.form_data, f)
        st.session_state.draft_saved = True
        st.session_state.last_saved_time_persistent = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # A simple function to load draft data
    def load_draft():
        try:
            with open(os.path.join(DRAFT_DIR, "current_draft.json"), "r") as f:
                st.session_state.form_data = json.load(f)
            st.session_state.draft_saved = True
            st.success("Draft loaded successfully!")
        except FileNotFoundError:
            st.info("No saved draft found.")

    # A simple function to reset form data
    def reset_form():
        st.session_state.form_data = initial_values_defaults.copy()
        st.session_state.uploaded_temp_photo_paths = []
        st.session_state.draft_saved = False
        st.session_state.last_saved_time_persistent = None
        st.info("Form has been reset.")
        st.rerun()

    # Create columns for draft and reset buttons
    col_draft1, col_draft2 = st.columns([1, 1])
    with col_draft1:
        if st.button("Load Draft"):
            load_draft()
            # After loading, update the form with the loaded data
            for key, value in st.session_state.form_data.items():
                st.session_state[f'widget_{key}'] = value
            st.rerun() # Rerun to refresh the form widgets
    with col_draft2:
        if st.button("Reset Form"):
            reset_form()

    if st.session_state.last_saved_time_persistent:
        st.info(f"Draft last saved at: {st.session_state.last_saved_time_persistent}")

    # Use a form to group all input widgets and a submit button
    with st.form("survey_form", clear_on_submit=True):
        st.header("Farmer Details")
        st.session_state.form_data['Surveyor'] = st.selectbox(labels["Surveyor"], options=options["Surveyor"], index=options["Surveyor"].index(st.session_state.form_data.get('Surveyor', initial_values_defaults['Surveyor'])), key='widget_Surveyor')
        st.session_state.form_data['Date'] = st.date_input(labels["Date"], value=pd.to_datetime(st.session_state.form_data.get('Date', initial_values_defaults['Date'])), key='widget_Date')
        
        # HPC details
        hpc_code = st.selectbox(labels["HPC Code"], options=options["HPC Code"], index=options["HPC Code"].index(st.session_state.form_data.get('HPC Code', initial_values_defaults['HPC Code'])), key='widget_HPC Code')
        st.session_state.form_data['HPC Code'] = hpc_code
        st.session_state.form_data['HPC Name'] = st.text_input(labels["HPC Name"], value=st.session_state.form_data.get('HPC Name', ''), key='widget_HPC Name')

        # Farmer details
        farmer_code = st.selectbox(labels["Farmer Code"], options=list(FARMER_LOOKUP.keys()), index=list(FARMER_LOOKUP.keys()).index(st.session_state.form_data.get('Farmer Code', initial_values_defaults['Farmer Code'])), key='widget_Farmer Code')
        st.session_state.form_data['Farmer Code'] = farmer_code
        st.session_state.form_data['Farmer Name'] = FARMER_LOOKUP[farmer_code]['name']
        st.session_state.form_data['Mobile Number'] = FARMER_LOOKUP[farmer_code]['mobile']
        st.write(f"**{labels['Farmer Name']}**: {st.session_state.form_data['Farmer Name']}")
        st.write(f"**{labels['Mobile Number']}**: {st.session_state.form_data['Mobile Number']}")

        st.markdown("---")
        st.header("Cattle and Milk Production")
        st.session_state.form_data['Total Cows'] = st.number_input(labels["Total Cows"], min_value=0, value=st.session_state.form_data.get('Total Cows', 0), key='widget_Total Cows')
        st.session_state.form_data['Cows in Milk'] = st.number_input(labels["Cows in Milk"], min_value=0, value=st.session_state.form_data.get('Cows in Milk', 0), key='widget_Cows in Milk')
        st.session_state.form_data['Dry Cows'] = st.number_input(labels["Dry Cows"], min_value=0, value=st.session_state.form_data.get('Dry Cows', 0), key='widget_Dry Cows')
        st.session_state.form_data['Heifers'] = st.number_input(labels["Heifers"], min_value=0, value=st.session_state.form_data.get('Heifers', 0), key='widget_Heifers')
        st.session_state.form_data['Calves'] = st.number_input(labels["Calves"], min_value=0, value=st.session_state.form_data.get('Calves', 0), key='widget_Calves')
        st.session_state.form_data['Milk Yield (LPD)'] = st.number_input(labels["Milk Yield (LPD)"], min_value=0.0, value=st.session_state.form_data.get('Milk Yield (LPD)', 0.0), key='widget_Milk Yield (LPD)')
        st.session_state.form_data['Fat (%)'] = st.number_input(labels["Fat (%)"], min_value=0.0, max_value=10.0, value=st.session_state.form_data.get('Fat (%)', 0.0), step=0.1, format="%.2f", key='widget_Fat (%)')
        st.session_state.form_data['SNF (%)'] = st.number_input(labels["SNF (%)"], min_value=0.0, max_value=15.0, value=st.session_state.form_data.get('SNF (%)', 0.0), step=0.1, format="%.2f", key='widget_SNF (%)')
        st.session_state.form_data['Protein (%)'] = st.number_input(labels["Protein (%)"], min_value=0.0, max_value=10.0, value=st.session_state.form_data.get('Protein (%)', 0.0), step=0.1, format="%.2f", key='widget_Protein (%)')
        st.session_state.form_data['TDS (%)'] = st.number_input(labels["TDS (%)"], min_value=0.0, value=st.session_state.form_data.get('TDS (%)', 0.0), step=0.1, format="%.2f", key='widget_TDS (%)')
        st.session_state.form_data['Last Calving Date'] = st.date_input(labels["Last Calving Date"], value=pd.to_datetime(st.session_state.form_data.get('Last Calving Date', datetime.date.today())), key='widget_Last Calving Date')
        st.session_state.form_data['Cattle Breed'] = st.selectbox(labels["Cattle Breed"], options=options["Cattle Breed"], index=options["Cattle Breed"].index(st.session_state.form_data.get('Cattle Breed', initial_values_defaults['Cattle Breed'])), key='widget_Cattle Breed')
        
        st.markdown("---")
        st.header("Feeding and Health")
        st.session_state.form_data['Green Fodder'] = st.radio(labels["Green Fodder"], options=options['Green Fodder'], index=options['Green Fodder'].index(st.session_state.form_data.get('Green Fodder', 'Yes')), key='widget_Green Fodder')
        if st.session_state.form_data['Green Fodder'] == 'Yes':
            st.session_state.form_data['Green Fodder Source'] = st.text_input(labels["Green Fodder Source"], value=st.session_state.form_data.get('Green Fodder Source', ''), key='widget_Green Fodder Source')
        else:
            st.session_state.form_data['Green Fodder Source'] = ''
        
        st.session_state.form_data['Dry Fodder'] = st.radio(labels["Dry Fodder"], options=options['Dry Fodder'], index=options['Dry Fodder'].index(st.session_state.form_data.get('Dry Fodder', 'No')), key='widget_Dry Fodder')
        if st.session_state.form_data['Dry Fodder'] == 'Yes':
            st.session_state.form_data['Dry Fodder Source'] = st.text_input(labels["Dry Fodder Source"], value=st.session_state.form_data.get('Dry Fodder Source', ''), key='widget_Dry Fodder Source')
        else:
            st.session_state.form_data['Dry Fodder Source'] = ''
        
        st.session_state.form_data['Concentrated Feed'] = st.radio(labels["Concentrated Feed"], options=options['Concentrated Feed'], index=options['Concentrated Feed'].index(st.session_state.form_data.get('Concentrated Feed', 'Yes')), key='widget_Concentrated Feed')
        if st.session_state.form_data['Concentrated Feed'] == 'Yes':
            st.session_state.form_data['Feed Brand'] = st.text_input(labels["Feed Brand"], value=st.session_state.form_data.get('Feed Brand', ''), key='widget_Feed Brand')
        else:
            st.session_state.form_data['Feed Brand'] = ''

        st.session_state.form_data['Mineral Mixture'] = st.radio(labels["Mineral Mixture"], options=options['Mineral Mixture'], index=options['Mineral Mixture'].index(st.session_state.form_data.get('Mineral Mixture', 'Yes')), key='widget_Mineral Mixture')
        if st.session_state.form_data['Mineral Mixture'] == 'Yes':
            st.session_state.form_data['Mineral Mixture Brand'] = st.text_input(labels["Mineral Mixture Brand"], value=st.session_state.form_data.get('Mineral Mixture Brand', ''), key='widget_Mineral Mixture Brand')
        else:
            st.session_state.form_data['Mineral Mixture Brand'] = ''
            
        st.session_state.form_data['Other Feed'] = st.text_area(labels["Other Feed"], value=st.session_state.form_data.get('Other Feed', ''), key='widget_Other Feed')
        
        st.session_state.form_data['Any Disease Outbreak'] = st.radio(labels["Any Disease Outbreak"], options=options['Any Disease Outbreak'], index=options['Any Disease Outbreak'].index(st.session_state.form_data.get('Any Disease Outbreak', 'No')), key='widget_Any Disease Outbreak')
        if st.session_state.form_data['Any Disease Outbreak'] == 'Yes':
            st.session_state.form_data['Disease Name'] = st.text_input(labels["Disease Name"], value=st.session_state.form_data.get('Disease Name', ''), key='widget_Disease Name')
        else:
            st.session_state.form_data['Disease Name'] = ''

        st.session_state.form_data['Veterinary Visit'] = st.radio(labels["Veterinary Visit"], options=options['Veterinary Visit'], index=options['Veterinary Visit'].index(st.session_state.form_data.get('Veterinary Visit', 'No')), key='widget_Veterinary Visit')
        if st.session_state.form_data['Veterinary Visit'] == 'Yes':
            st.session_state.form_data['Last Vet Visit Date'] = st.date_input(labels["Last Vet Visit Date"], value=pd.to_datetime(st.session_state.form_data.get('Last Vet Visit Date', datetime.date.today())), key='widget_Last Vet Visit Date')
        else:
            st.session_state.form_data['Last Vet Visit Date'] = ''

        st.session_state.form_data['AI/Services'] = st.radio(labels["AI/Services"], options=options['AI/Services'], index=options['AI/Services'].index(st.session_state.form_data.get('AI/Services', 'No')), key='widget_AI/Services')
        if st.session_state.form_data['AI/Services'] == 'Yes':
            st.session_state.form_data['Last AI Date'] = st.date_input(labels["Last AI Date"], value=pd.to_datetime(st.session_state.form_data.get('Last AI Date', datetime.date.today())), key='widget_Last AI Date')
        else:
            st.session_state.form_data['Last AI Date'] = ''

        st.markdown("---")
        st.header("Farm Infrastructure")
        st.session_state.form_data['Manure Management'] = st.radio(labels["Manure Management"], options=options['Manure Management'], index=options['Manure Management'].index(st.session_state.form_data.get('Manure Management', 'No')), key='widget_Manure Management')
        st.session_state.form_data['Shed Type'] = st.selectbox(labels["Shed Type"], options=options['Shed Type'], index=options['Shed Type'].index(st.session_state.form_data.get('Shed Type', 'Pukka')), key='widget_Shed Type')
        st.session_state.form_data['Water Source'] = st.selectbox(labels["Water Source"], options=options['Water Source'], index=options['Water Source'].index(st.session_state.form_data.get('Water Source', 'Borewell')), key='widget_Water Source')

        st.markdown("---")
        st.header("Observations")
        st.session_state.form_data['Key Insights'] = st.text_area(labels["Key Insights"], value=st.session_state.form_data.get('Key Insights', ''), key='widget_Key Insights')

        # --- Photo Upload Section ---
        st.markdown("---")
        st.subheader(labels['Upload Photos'])
        uploaded_files = st.file_uploader(
            "Choose images...",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key='photo_uploader'
        )

        current_photo_count = len(st.session_state.uploaded_temp_photo_paths)
        if uploaded_files:
            new_photos_added = False
            for uploaded_file in uploaded_files:
                temp_path = os.path.join(TEMP_IMAGE_DIR, uploaded_file.name)
                # Check if the file has already been processed to avoid duplicates
                if temp_path not in st.session_state.uploaded_temp_photo_paths:
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.session_state.uploaded_temp_photo_paths.append(temp_path)
                    new_photos_added = True

            # If new photos were added, clear the uploader to prevent re-uploading on rerun
            if new_photos_added:
                # This reruns the script, effectively clearing the file uploader widget
                st.experimental_rerun()
        
        # Displaying uploaded photos with a remove button
        if st.session_state.uploaded_temp_photo_paths:
            st.write("Current Photos:")
            for i, photo_path in enumerate(st.session_state.uploaded_temp_photo_paths):
                col_photo, col_remove = st.columns([0.8, 0.2])
                with col_photo:
                    st.image(photo_path, caption=os.path.basename(photo_path), width=200)
                with col_remove:
                    if st.button("Remove", key=f"remove_{i}"):
                        try:
                            os.remove(photo_path)
                            st.session_state.uploaded_temp_photo_paths.pop(i)
                            st.rerun() # Rerun to update the photo list
                        except OSError as e:
                            st.error(f"Error removing file: {e}")
            st.session_state.form_data['Photos'] = ", ".join([os.path.basename(path) for path in st.session_state.uploaded_temp_photo_paths])
        else:
            st.session_state.form_data['Photos'] = ""
            st.info("No photos uploaded yet.")
        
        # --- Form Submit and Draft Buttons ---
        submit_button = st.form_submit_button("Submit for Review")
        
    # Actions after form submission
    if submit_button:
        # Check for required fields and validate data
        if not all([st.session_state.form_data.get(k) for k in ['Surveyor', 'Farmer Code', 'HPC Code', 'Date']]):
            st.error("Please fill in all required fields.")
        else:
            st.session_state.final_submitted_data = st.session_state.form_data.copy()
            st.session_state.current_step = 'review'
            st.rerun()

    # Draft save button outside of the form to avoid clearing on submit
    if st.button("Save Draft"):
        save_draft()
        st.success("Draft saved successfully!")
        st.rerun()


