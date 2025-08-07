import streamlit as st
import pandas as pd
import datetime
import os
import json
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

# --- Dictionaries and Options ---
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

def load_all_data():
    master_file = os.path.join(SAVE_DIR, "survey_responses_master.csv")
    if not os.path.exists(master_file):
        return pd.DataFrame()
    try:
        return pd.read_csv(master_file)
    except Exception as e:
        st.warning(f"Could not read {master_file}: {e}")
        return pd.DataFrame()

if st.session_state.all_responses_df.empty:
    st.session_state.all_responses_df = load_all_data()

def get_all_responses_df():
    return st.session_state.all_responses_df

def save_draft():
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    try:
        data_to_save = st.session_state.form_data.copy()
        
        for key, value in data_to_save.items():
            if isinstance(value, datetime.date):
                data_to_save[key] = value.strftime('%Y-%m-%d')
            elif isinstance(value, pd.Timestamp):
                 data_to_save[key] = value.date().strftime('%Y-%m-%d')
        
        with open(draft_filename, "w") as f:
            json.dump(data_to_save, f, indent=4)
            
        st.session_state.draft_saved = True
        st.session_state.last_saved_time_persistent = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    except Exception as e:
        st.error(f"Error saving draft: {e}")
        return False

def load_draft():
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    try:
        with open(draft_filename, "r") as f:
            loaded_data = json.load(f)
            
        for key, value in loaded_data.items():
            if key in ['Date', 'Last Calving Date', 'Last Vet Visit Date', 'Last AI Date']:
                if value:
                    try:
                        loaded_data[key] = datetime.datetime.strptime(value, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        loaded_data[key] = None
        
        st.session_state.form_data = loaded_data
        st.session_state.draft_saved = True
        st.success("Draft loaded successfully!")
        return True
    except FileNotFoundError:
        st.info("No saved draft found.")
        return False
    except Exception as e:
        st.error(f"Error loading draft: {e}")
        return False
    
# --- Application Logic Based on Session State ---
if st.session_state.current_step == 'form_entry':
    st.title("Heritage Dairy Survey 🐄")
    st.write("Please fill out the survey form below.")

    col_draft1, col_draft2 = st.columns([1, 1])
    with col_draft1:
        if st.button("Load Draft"):
            if load_draft():
                st.rerun() 
    with col_draft2:
        if st.button("Reset Form"):
            reset_form()
            st.rerun() 

    if st.session_state.last_saved_time_persistent:
        st.info(f"Draft last saved at: {st.session_state.last_saved_time_persistent}")

    with st.form("survey_form"):
        st.header("Farmer Details")
        st.session_state.form_data['Surveyor'] = st.selectbox(labels["Surveyor"], options=options["Surveyor"], index=options["Surveyor"].index(st.session_state.form_data.get('Surveyor', initial_values_defaults['Surveyor'])))
        st.session_state.form_data['Date'] = st.date_input(labels["Date"], value=pd.to_datetime(st.session_state.form_data.get('Date', initial_values_defaults['Date'])))
        
        hpc_code = st.selectbox(labels["HPC Code"], options=options["HPC Code"], index=options["HPC Code"].index(st.session_state.form_data.get('HPC Code', initial_values_defaults['HPC Code'])))
        st.session_state.form_data['HPC Code'] = hpc_code
        st.session_state.form_data['HPC Name'] = st.text_input(labels["HPC Name"], value=st.session_state.form_data.get('HPC Name', ''))

        farmer_code = st.selectbox(labels["Farmer Code"], options=list(FARMER_LOOKUP.keys()), index=list(FARMER_LOOKUP.keys()).index(st.session_state.form_data.get('Farmer Code', initial_values_defaults['Farmer Code'])))
        st.session_state.form_data['Farmer Code'] = farmer_code
        st.session_state.form_data['Farmer Name'] = FARMER_LOOKUP[farmer_code]['name']
        st.session_state.form_data['Mobile Number'] = FARMER_LOOKUP[farmer_code]['mobile']
        st.write(f"**{labels['Farmer Name']}**: {st.session_state.form_data['Farmer Name']}")
        st.write(f"**{labels['Mobile Number']}**: {st.session_state.form_data['Mobile Number']}")

        st.markdown("---")
        st.header("Cattle and Milk Production")
        st.session_state.form_data['Total Cows'] = st.number_input(labels["Total Cows"], min_value=0, value=st.session_state.form_data.get('Total Cows', 0))
        st.session_state.form_data['Cows in Milk'] = st.number_input(labels["Cows in Milk"], min_value=0, value=st.session_state.form_data.get('Cows in Milk', 0))
        st.session_state.form_data['Dry Cows'] = st.number_input(labels["Dry Cows"], min_value=0, value=st.session_state.form_data.get('Dry Cows', 0))
        st.session_state.form_data['Heifers'] = st.number_input(labels["Heifers"], min_value=0, value=st.session_state.form_data.get('Heifers', 0))
        st.session_state.form_data['Calves'] = st.number_input(labels["Calves"], min_value=0, value=st.session_state.form_data.get('Calves', 0))
        st.session_state.form_data['Milk Yield (LPD)'] = st.number_input(labels["Milk Yield (LPD)"], min_value=0.0, value=st.session_state.form_data.get('Milk Yield (LPD)', 0.0), step=0.1, format="%.2f")
        st.session_state.form_data['Fat (%)'] = st.number_input(labels["Fat (%)"], min_value=0.0, max_value=10.0, value=st.session_state.form_data.get('Fat (%)', 0.0), step=0.1, format="%.2f")
        st.session_state.form_data['SNF (%)'] = st.number_input(labels["SNF (%)"], min_value=0.0, max_value=15.0, value=st.session_state.form_data.get('SNF (%)', 0.0), step=0.1, format="%.2f")
        st.session_state.form_data['Protein (%)'] = st.number_input(labels["Protein (%)"], min_value=0.0, max_value=10.0, value=st.session_state.form_data.get('Protein (%)', 0.0), step=0.1, format="%.2f")
        st.session_state.form_data['TDS (%)'] = st.number_input(labels["TDS (%)"], min_value=0.0, value=st.session_state.form_data.get('TDS (%)', 0.0), step=0.1, format="%.2f")
        st.session_state.form_data['Last Calving Date'] = st.date_input(labels["Last Calving Date"], value=pd.to_datetime(st.session_state.form_data.get('Last Calving Date', datetime.date.today())))
        st.session_state.form_data['Cattle Breed'] = st.selectbox(labels["Cattle Breed"], options=options["Cattle Breed"], index=options["Cattle Breed"].index(st.session_state.form_data.get('Cattle Breed', initial_values_defaults['Cattle Breed'])))
        
        st.markdown("---")
        st.header("Feeding and Health")
        st.session_state.form_data['Green Fodder'] = st.radio(labels["Green Fodder"], options=options['Green Fodder'], index=options['Green Fodder'].index(st.session_state.form_data.get('Green Fodder', 'Yes')))
        if st.session_state.form_data['Green Fodder'] == 'Yes':
            st.session_state.form_data['Green Fodder Source'] = st.text_input(labels["Green Fodder Source"], value=st.session_state.form_data.get('Green Fodder Source', ''))
        else:
            st.session_state.form_data['Green Fodder Source'] = ''
        
        st.session_state.form_data['Dry Fodder'] = st.radio(labels["Dry Fodder"], options=options['Dry Fodder'], index=options['Dry Fodder'].index(st.session_state.form_data.get('Dry Fodder', 'No')))
        if st.session_state.form_data['Dry Fodder'] == 'Yes':
            st.session_state.form_data['Dry Fodder Source'] = st.text_input(labels["Dry Fodder Source"], value=st.session_state.form_data.get('Dry Fodder Source', ''))
        else:
            st.session_state.form_data['Dry Fodder Source'] = ''
        
        st.session_state.form_data['Concentrated Feed'] = st.radio(labels["Concentrated Feed"], options=options['Concentrated Feed'], index=options['Concentrated Feed'].index(st.session_state.form_data.get('Concentrated Feed', 'Yes')))
        if st.session_state.form_data['Concentrated Feed'] == 'Yes':
            st.session_state.form_data['Feed Brand'] = st.text_input(labels["Feed Brand"], value=st.session_state.form_data.get('Feed Brand', ''))
        else:
            st.session_state.form_data['Feed Brand'] = ''

        st.session_state.form_data['Mineral Mixture'] = st.radio(labels["Mineral Mixture"], options=options['Mineral Mixture'], index=options['Mineral Mixture'].index(st.session_state.form_data.get('Mineral Mixture', 'Yes')))
        if st.session_state.form_data['Mineral Mixture'] == 'Yes':
            st.session_state.form_data['Mineral Mixture Brand'] = st.text_input(labels["Mineral Mixture Brand"], value=st.session_state.form_data.get('Mineral Mixture Brand', ''))
        else:
            st.session_state.form_data['Mineral Mixture Brand'] = ''
            
        st.session_state.form_data['Other Feed'] = st.text_area(labels["Other Feed"], value=st.session_state.form_data.get('Other Feed', ''))
        
        st.session_state.form_data['Any Disease Outbreak'] = st.radio(labels["Any Disease Outbreak"], options=options['Any Disease Outbreak'], index=options['Any Disease Outbreak'].index(st.session_state.form_data.get('Any Disease Outbreak', 'No')))
        if st.session_state.form_data['Any Disease Outbreak'] == 'Yes':
            st.session_state.form_data['Disease Name'] = st.text_input(labels["Disease Name"], value=st.session_state.form_data.get('Disease Name', ''))
        else:
            st.session_state.form_data['Disease Name'] = ''

        st.session_state.form_data['Veterinary Visit'] = st.radio(labels["Veterinary Visit"], options=options['Veterinary Visit'], index=options['Veterinary Visit'].index(st.session_state.form_data.get('Veterinary Visit', 'No')))
        if st.session_state.form_data['Veterinary Visit'] == 'Yes':
            st.session_state.form_data['Last Vet Visit Date'] = st.date_input(labels["Last Vet Visit Date"], value=pd.to_datetime(st.session_state.form_data.get('Last Vet Visit Date', datetime.date.today())))
        else:
            st.session_state.form_data['Last Vet Visit Date'] = ''

        st.session_state.form_data['AI/Services'] = st.radio(labels["AI/Services"], options=options['AI/Services'], index=options['AI/Services'].index(st.session_state.form_data.get('AI/Services', 'No')))
        if st.session_state.form_data['AI/Services'] == 'Yes':
            st.session_state.form_data['Last AI Date'] = st.date_input(labels["Last AI Date"], value=pd.to_datetime(st.session_state.form_data.get('Last AI Date', datetime.date.today())))
        else:
            st.session_state.form_data['Last AI Date'] = ''

        st.markdown("---")
        st.header("Farm Infrastructure")
        st.session_state.form_data['Manure Management'] = st.radio(labels["Manure Management"], options=options['Manure Management'], index=options['Manure Management'].index(st.session_state.form_data.get('Manure Management', 'No')))
        st.session_state.form_data['Shed Type'] = st.selectbox(labels["Shed Type"], options=options['Shed Type'], index=options['Shed Type'].index(st.session_state.form_data.get('Shed Type', 'Pukka')))
        st.session_state.form_data['Water Source'] = st.selectbox(labels["Water Source"], options=options['Water Source'], index=options['Water Source'].index(st.session_state.form_data.get('Water Source', 'Borewell')))

        st.markdown("---")
        st.header("Observations")
        st.session_state.form_data['Key Insights'] = st.text_area(labels["Key Insights"], value=st.session_state.form_data.get('Key Insights', ''))

        st.markdown("---")
        st.subheader(labels['Upload Photos'])
        uploaded_files = st.file_uploader(
            "Choose images...",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )

        if uploaded_files:
            new_photos_added = False
            for uploaded_file in uploaded_files:
                temp_path = os.path.join(TEMP_IMAGE_DIR, uploaded_file.name)
                if temp_path not in st.session_state.uploaded_temp_photo_paths:
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.session_state.uploaded_temp_photo_paths.append(temp_path)
                    new_photos_added = True
            if new_photos_added:
                st.rerun()
        
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
                            st.rerun()
                        except OSError as e:
                            st.error(f"Error removing file: {e}")
            st.session_state.form_data['Photos'] = ", ".join([os.path.basename(path) for path in st.session_state.uploaded_temp_photo_paths])
        else:
            st.session_state.form_data['Photos'] = ""
            st.info("No photos uploaded yet.")
        
        submit_button = st.form_submit_button("Submit for Review")
        
    if submit_button:
        if not all([st.session_state.form_data.get(k) for k in ['Surveyor', 'Farmer Code', 'HPC Code', 'Date']]):
            st.error("Please fill in all required fields.")
        else:
            st.session_state.final_submitted_data = st.session_state.form_data.copy()
            st.session_state.current_step = 'review'
            st.rerun()

    if st.button("Save Draft"):
        if save_draft():
            st.success("Draft saved successfully!")
            st.rerun()

elif st.session_state.current_step == 'review':
    st.title(labels['Review Your Submission'])
    st.write("Please review the information below before final submission.")
    
    data_to_review = st.session_state.final_submitted_data

    if data_to_review:
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
                
                df_new_entry = pd.DataFrame([data_to_review])

                master_file = os.path.join(SAVE_DIR, "survey_responses_master.csv")
                try:
                    file_exists = os.path.exists(master_file)
                    df_new_entry.to_csv(master_file, mode='a', header=not file_exists, index=False)
                    
                    if not st.session_state.all_responses_df.empty:
                        st.session_state.all_responses_df = pd.concat([st.session_state.all_responses_df, df_new_entry], ignore_index=True)
                    else:
                        st.session_state.all_responses_df = df_new_entry
                    
                    st.session_state.current_step = 'submitted'
                    st.session_state.last_saved_time_persistent = None
                    
                    for f in os.listdir(TEMP_IMAGE_DIR):
                        os.remove(os.path.join(TEMP_IMAGE_DIR, f))
                    st.session_state.uploaded_temp_photo_paths = []

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
