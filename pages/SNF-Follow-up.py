import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO
import datetime
from PIL import Image 

# --- ADDED FOR DEBUGGING: Print current working directory ---
st.write(f"**Current Working Directory:** `{os.getcwd()}`")
st.write("---") 
# --- END DEBUGGING ADDITION ---


st.set_page_config(
    page_title="SNF Follow-up Survey App",
    layout="wide",
    initial_sidebar_state="auto"
)

st.title("SNF Follow-up Survey")


PHOTOS_DIR = "photos"        
RESPONSES_CSV = "responses.csv" 



os.makedirs(PHOTOS_DIR, exist_ok=True)


ADMIN_EMAILS = [
    "mkaushal@tns.org",
    "rsomanchi@tns.org",
    "kbalaji@tns.org",
    "gmreddy@tns.org"
]



if 'form_data' not in st.session_state:
    st.session_state.form_data = {} 
if 'uploaded_photo_info' not in st.session_state:
    st.session_state.uploaded_photo_info = None 
if 'show_review_page' not in st.session_state:
    st.session_state.show_review_page = False 
if 'admin_unlocked' not in st.session_state:
    st.session_state.admin_unlocked = False 
if 'validation_errors' not in st.session_state:
    st.session_state.validation_errors = [] 



def get_field_value(key, default=""):
    return st.session_state.form_data.get(key, default)

def set_field_value(key, value):
    st.session_state.form_data[key] = value



FORM_FIELDS_MAP = {
    "surveyor_name": {"label": "Surveyor Name", "widget": "selectbox", "options": ["Guru", "Balaji"]},
    "date_of_visit": {"label": "Date of Visit (DD-MM-YYYY)", "widget": "text_input", "validation": "date"},
    "hpc_code": {"label": "HPC Code", "widget": "text_input"},
    "hpc_name": {"label": "HPC Name", "widget": "text_input"},
    "farmer_name": {"label": "Farmer Name", "widget": "text_input"},
    "farmer_code": {"label": "Farmer Code", "widget": "text_input"},
    "gender": {"label": "Gender", "widget": "selectbox", "options": ["Male", "Female", "Other"]},
    "fat_list": {"label": "Fat in the list (%)", "widget": "text_input", "validation": "numeric"},
    "snf_list": {"label": "SNF in the list (%)", "widget": "text_input", "validation": "numeric"},
    "vol_list": {"label": "Vol in the list (LPD)", "widget": "text_input", "validation": "numeric"},
    "as_on_date_fat": {"label": "Fat in the farmer slip (%)", "widget": "text_input", "validation": "numeric"},
    "as_on_date_snf": {"label": "SNF in the farmer slip (%)", "widget": "text_input", "validation": "numeric"},
    "as_on_date_vol": {"label": "Vol in the farmer slip (LPD)", "widget": "text_input", "validation": "numeric"},
    "number_of_cows": {"label": "Total Number of Cows", "widget": "text_input", "validation": "numeric"},
    "jersey_cross": {"label": "Jersey /Cross (Count)", "widget": "text_input", "validation": "numeric"},
    "hf_cross": {"label": "HF/Cross (Count)", "widget": "text_input", "validation": "numeric"},
    "jersey_milk": {"label": "No. of Jersey cows in milk", "widget": "text_input", "validation": "numeric"},
    "jersey_vol_lpd": {"label": "Vol-LPD (Jersey Cows)", "widget": "text_input", "validation": "numeric"},
    "jersey_fat": {"label": "Fat (Jersey Cows) (%)", "widget": "text_input", "validation": "numeric"},
    "jersey_snf": {"label": "SNF (Jersey Cows) (%)", "widget": "text_input", "validation": "numeric"},
    "hf_milk": {"label": "No. of HF cows in milk", "widget": "text_input", "validation": "numeric"},
    "hf_vol_lpd": {"label": "Vol-LPD (HF Cows)", "widget": "text_input", "validation": "numeric"},
    "hf_fat": {"label": "Fat (HF Cows) (%)", "widget": "text_input", "validation": "numeric"},
    "hf_snf": {"label": "SNF (HF Cows) (%)", "widget": "text_input", "validation": "numeric"},
    "desi_milk": {"label": "No. of Desi cows in milk", "widget": "text_input", "validation": "numeric"},
    "desi_vol_lpd": {"label": "Vol-LPD (Desi Cows)", "widget": "text_input", "validation": "numeric"},
    "desi_fat": {"label": "Fat (Desi Cows) (%)", "widget": "text_input", "validation": "numeric"},
    "desi_snf": {"label": "SNF (Desi Cows) (%)", "widget": "text_input", "validation": "numeric"},
    "buffalo_milk": {"label": "No. of Buffalo in milk", "widget": "text_input", "validation": "numeric"},
    "buffalo_vol_lpd": {"label": "Vol-LPD (Buffalo)", "widget": "text_input", "validation": "numeric"},
    "green_fodder": {"label": "Green Fodder Available?", "widget": "selectbox", "options": ["Yes", "No"]},
    "green_fodder_type": {"label": "Type of Green Fodder (if Yes)", "widget": "text_input", "conditional_required_if": {"field": "green_fodder", "value": "Yes"}},
    "green_fodder_qty": {"label": "Quantity of Green Fodder (Kg/day)", "widget": "text_input", "validation": "numeric", "conditional_required_if": {"field": "green_fodder", "value": "Yes"}},
    "dry_fodder": {"label": "Dry Fodder Available?", "widget": "selectbox", "options": ["Yes", "No"]},
    "dry_fodder_type": {"label": "Type of Dry Fodder (if Yes)", "widget": "text_input", "conditional_required_if": {"field": "dry_fodder", "value": "Yes"}},
    "dry_fodder_qty": {"label": "Quantity of Dry Fodder (Kg/day)", "widget": "text_input", "validation": "numeric", "conditional_required_if": {"field": "dry_fodder", "value": "Yes"}},
    "pellet_feed": {"label": "Pellet Feed Used?", "widget": "selectbox", "options": ["Yes", "No"]},
    "heritage_feed": {"label": "If Yes, Heritage Feed (Yes/No)", "widget": "text_input", "conditional_required_if": {"field": "pellet_feed", "value": "Yes"}},
    "feed_variant": {"label": "If Yes, Mention the Feed Variant", "widget": "text_input", "conditional_required_if": {"field": "pellet_feed", "value": "Yes"}},
    "feed_brand": {"label": "If No, Mention the Feed Brand", "widget": "text_input", "conditional_required_if": {"field": "pellet_feed", "value": "No"}},
    "pellet_qty": {"label": "Quantity of Pellet Feed (Kg/day)", "widget": "text_input", "validation": "numeric", "conditional_required_if": {"field": "pellet_feed", "value": "Yes"}},
    "mineral_mix": {"label": "Mineral Mixture Used?", "widget": "selectbox", "options": ["Yes", "No"]},
    "mineral_mix_brand": {"label": "Mineral Mixture Brand (if Yes)", "widget": "text_input", "conditional_required_if": {"field": "mineral_mix", "value": "Yes"}},
    "mineral_mix_qty": {"label": "Quantity of Mineral Mixture (gm/day)", "widget": "text_input", "validation": "numeric", "conditional_required_if": {"field": "mineral_mix", "value": "Yes"}},
    "key_insights": {"label": "Key Insights/Observations", "widget": "text_area"},
}


def validate_form_data():
    st.session_state.validation_errors = [] 
    data = st.session_state.form_data 

    
    
    general_required_fields = [
        "surveyor_name", "date_of_visit", "hpc_code", "hpc_name", "farmer_name", "farmer_code", "gender",
        "green_fodder", "dry_fodder", "pellet_feed", "mineral_mix"
    ]
    for key in general_required_fields:
        if not data.get(key):
            st.session_state.validation_errors.append(f"'{FORM_FIELDS_MAP[key]['label']}' is a required field.")

    
    for key, details in FORM_FIELDS_MAP.items():
        if details.get("validation") == "numeric":
            value = data.get(key)
            if value: 
                try:
                    num_val = float(value)
                    if num_val < 0:
                        st.session_state.validation_errors.append(f"'{details['label']}' must be a non-negative number.")
                except ValueError:
                    st.session_state.validation_errors.append(f"'{details['label']}' must be a valid number.")

    
    date_str = data.get("date_of_visit")
    if date_str:
        try:
            datetime.datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            st.session_state.validation_errors.append("Date of Visit must be in DD-MM-YYYY format.")

    
    for key, details in FORM_FIELDS_MAP.items():
        if "conditional_required_if" in details:
            condition = details["conditional_required_if"]
            if data.get(condition["field"]) == condition["value"]:
                if not data.get(key):
                    st.session_state.validation_errors.append(f"'{details['label']}' is required because '{FORM_FIELDS_MAP[condition['field']]['label']}' is '{condition['value']}'.")

    return not st.session_state.validation_errors 


if not st.session_state.show_review_page:
    with st.form("survey_form", clear_on_submit=False):
        st.header("Farmer Survey Details")

        
        for key, details in FORM_FIELDS_MAP.items():
            label = details["label"]
            current_value = get_field_value(key) 

            if details["widget"] == "selectbox":
                selected_option = st.selectbox(label, options=details["options"],
                                               index=details["options"].index(current_value) if current_value in details["options"] else 0,
                                               key=f"form_widget_{key}")
                set_field_value(key, selected_option) 
            elif details["widget"] == "text_input":
                entered_text = st.text_input(label, value=current_value, key=f"form_widget_{key}")
                set_field_value(key, entered_text) 
            elif details["widget"] == "text_area":
                entered_text = st.text_area(label, value=current_value, key=f"form_widget_{key}")
                set_field_value(key, entered_text) 

        
        
        if st.session_state.uploaded_photo_info:
            st.image(BytesIO(st.session_state.uploaded_photo_info['data']), caption="Previously uploaded photo", width=100)
            if st.button("Clear Photo", key="clear_photo_form"):
                st.session_state.uploaded_photo_info = None
                st.rerun()  

        new_uploaded_photo = st.file_uploader("Upload a photo (optional)", type=["jpg", "jpeg", "png"], key="form_photo_uploader")
        
        if new_uploaded_photo:
            
            st.session_state.uploaded_photo_info = {
                "name": new_uploaded_photo.name,
                "data": new_uploaded_photo.getvalue(),
                "type": new_uploaded_photo.type
            }

        
        submitted = st.form_submit_button("Review & Submit")

        if submitted:
            if validate_form_data(): 
                st.session_state.show_review_page = True
                st.rerun()  
            else:
                for error in st.session_state.validation_errors:
                    st.error(error)


if st.session_state.show_review_page:
    st.header("Review Your Submission")
    st.info("Please review the details below. If everything is correct, confirm and submit.")

    
    for key, details in FORM_FIELDS_MAP.items():
        label = details["label"]
        display_value = get_field_value(key, "N/A") 
        st.write(f"**{label}:** {display_value}")
    
    if st.session_state.uploaded_photo_info:
        st.write("---") 
        st.write("**Uploaded Photo:**")
        image_data = BytesIO(st.session_state.uploaded_photo_info['data'])
        st.image(image_data, caption=st.session_state.uploaded_photo_info['name'], width=300)

    
    confirm = st.checkbox("I confirm that the above information is correct.", key="review_confirm_checkbox")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Edit Responses", key="edit_responses_button"):
            st.session_state.show_review_page = False
            st.rerun()  
    with col2:
        if confirm and st.button("Confirm & Final Submit", key="final_submit_button"):
            
            photo_filename = "" 
            if st.session_state.uploaded_photo_info:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = os.path.splitext(st.session_state.uploaded_photo_info['name'])[1]
                
                identifier = get_field_value("farmer_code") or \
                             get_field_value("farmer_name") or "unknown_farmer"
                
                photo_filename = f"{identifier}_{timestamp}{file_extension}"
                photo_path = os.path.join(PHOTOS_DIR, photo_filename)
                
                try:
                    with open(photo_path, "wb") as f:
                        f.write(st.session_state.uploaded_photo_info["data"])
                    st.success(f"Photo uploaded and saved as {photo_filename}.")
                except Exception as e:
                    st.error(f"Error saving photo: {e}")
                      

            
            row_data = []
            columns_for_csv = []
            for key, details in FORM_FIELDS_MAP.items():
                columns_for_csv.append(details["label"])
                row_data.append(get_field_value(key))
            
            columns_for_csv.append("Photo Filename")
            row_data.append(photo_filename)

            df_new_row = pd.DataFrame([row_data], columns=columns_for_csv)

            
            try:
                if os.path.exists(RESPONSES_CSV):
                    df_new_row.to_csv(RESPONSES_CSV, mode="a", header=False, index=False)
                else:
                    df_new_row.to_csv(RESPONSES_CSV, index=False)
                
                st.success("Your response has been submitted successfully!")
                st.balloons()

                
                st.session_state.form_data = {}
                st.session_state.uploaded_photo_info = None
                st.session_state.show_review_page = False
                st.session_state.validation_errors = []
                st.rerun()  
            except Exception as e:
                st.error(f"Error saving survey data to CSV: {e}")




if not st.session_state.admin_unlocked:
    with st.expander("Admin Access (Login)", expanded=False): 
        admin_email_input = st.text_input("Enter admin email", key="admin_email_input")
        if st.button("Login as Admin", key="admin_login_button"):
            if admin_email_input in ADMIN_EMAILS:
                st.session_state.admin_unlocked = True
                st.rerun()  
            else:
                st.error("Access denied. Please check your admin email.")
else: 
    with st.expander("Admin Access (Features)", expanded=True): 
        st.success("Admin access granted.")

        
        st.subheader("Download Options")
        
        
        if os.path.exists(RESPONSES_CSV):
            with open(RESPONSES_CSV, "rb") as f:
                st.download_button(
                    label="Download All Survey Responses (CSV)",
                    data=f,
                    file_name="responses.csv",
                    mime="text/csv",
                    key="download_csv_button"
                )
        else:
            st.info("No survey responses recorded yet.")

        
        photo_files_in_dir = [f for f in os.listdir(PHOTOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if photo_files_in_dir:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf: 
                for photo_file in photo_files_in_dir:
                    file_path = os.path.join(PHOTOS_DIR, photo_file)
                    try:
                        
                        Image.open(file_path).verify()
                        zf.write(file_path, os.path.basename(file_path))
                    except Exception as e:
                        st.warning(f"Skipping corrupted image {photo_file} in ZIP: {e}")
            zip_buffer.seek(0) 
            st.download_button(
                label="Download All Photos (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="photos.zip",
                mime="application/zip",
                key="download_photos_button"
            )
        else:
            st.info("No photos uploaded yet.")

        
        st.subheader("View Real-time Data")
        
        
        if os.path.exists(RESPONSES_CSV):
            st.write("#### Survey Responses Table")
            try:
                df_responses = pd.read_csv(RESPONSES_CSV)
                if not df_responses.empty: 
                    st.dataframe(df_responses, use_container_width=True)
                else:
                    st.info("The CSV file exists but contains no data.") 
            except pd.errors.EmptyDataError:
                st.info("The CSV file exists but is empty.")
            except Exception as e:
                st.error(f"Error reading responses CSV: {e}")
        else:
            st.info("No survey responses to display.")

        
        st.write("#### Uploaded Photos")
        
        if photo_files_in_dir:
            num_cols = 3 
            cols = st.columns(num_cols)
            for i, photo_file in enumerate(photo_files_in_dir):
                with cols[i % num_cols]:
                    file_path = os.path.join(PHOTOS_DIR, photo_file)
                    try:
                        Image.open(file_path).verify() 
                        st.image(file_path, caption=photo_file, use_column_width="always")
                    except Exception as e:
                        st.warning(f"⚠️ Unable to display image: {photo_file}. Error: {str(e)}")
        else:
            st.info("No photos to display.")
