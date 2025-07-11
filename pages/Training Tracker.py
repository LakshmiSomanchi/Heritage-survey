import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile
from io import BytesIO

# ---- SETUP ---- #
st.set_page_config(page_title="Training Tracker", layout="wide")

ADMIN_EMAILS = [
    "mkaushal@tns.org",
    "rsomanchi@tns.org",
    "gmreddy@tns.org",
    "kbalaji@tns.org"
]
DATA_FILE = "submissions.csv"
PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

# Initialize session state for multi-step form and email
if 'show_review' not in st.session_state:
    st.session_state.show_review = False
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'uploaded_photo' not in st.session_state:
    st.session_state.uploaded_photo = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = "" # Initialize user_email in session state

# Helper function to save submission data and photo
def save_submission(data, photo_file):
    # Prepare data for DataFrame
    # Ensure all columns exist, even if value is None, to prevent pandas from complaining
    # Create a dictionary with all expected columns and default None values
    all_columns = [
        "timestamp", "date", "hpc_code", "hpc_name", "trainer", "topic",
        "volume", "avg_fat", "avg_snf", "pourers_total", "pourers_attended",
        "heritage_users", "non_heritage_users", "awareness_feed",
        "awareness_supplements", "awareness_vet", "awareness_ai",
        "awareness_loans", "awareness_insurance", "awareness_gpa",
        "key_insights", "email", "photo_filename" # Added photo_filename column
    ]
    
    # Create a dictionary with default None values for all columns
    row_data = {col: None for col in all_columns}
    # Update with actual data
    row_data.update(data)

    df_new_entry = pd.DataFrame([row_data])

    # Load existing data or create new DataFrame
    if os.path.exists(DATA_FILE):
        df_existing = pd.read_csv(DATA_FILE)
        df = pd.concat([df_existing, df_new_entry], ignore_index=True)
    else:
        df = df_new_entry

    # Save form data to CSV
    df.to_csv(DATA_FILE, index=False)

    # Save photo if provided
    photo_filename_in_csv = "" # Default to empty string
    if photo_file is not None:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        identifier = data.get('hpc_code', '').replace(' ', '_') or \
                     data.get('hpc_name', '').replace(' ', '_') or \
                     f"submission_{timestamp_str}" # Fallback if both empty
        file_extension = os.path.splitext(photo_file.name)[1]
        photo_filename = f"{identifier}_{timestamp_str}{file_extension}"
        photo_path = os.path.join(PHOTO_DIR, photo_filename)
        
        with open(photo_path, "wb") as f:
            f.write(photo_file.getbuffer()) # Use getbuffer() for Streamlit UploadedFile
        
        photo_filename_in_csv = photo_filename # Store only the filename in CSV

    return photo_filename_in_csv # Return the filename saved in the system

# Helper function to get all submission data
def get_all_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame()

# Helper function to get paths of all photos
def get_all_photos_paths():
    if os.path.exists(PHOTO_DIR):
        image_files = [f for f in os.listdir(PHOTO_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))]
        return [os.path.join(PHOTO_DIR, f) for f in image_files]
    else:
        return []

# ---- MAIN APP ---- #
st.title("Training Tracker")

# Authentication: email input (use session state to retain value)
user_email_input = st.text_input("Enter your email:", value=st.session_state.user_email, key="user_email_input").strip()

if user_email_input != st.session_state.user_email:
    st.session_state.user_email = user_email_input
    # If email changes, re-run to update admin access status for tabs
    st.rerun() 

is_admin = st.session_state.user_email in ADMIN_EMAILS

# Use tabs for navigation
tabs = st.tabs(["Submit Entry", "Admin Panel"])

with tabs[0]: # Submit Entry Tab
    st.header("Submit Training Data")
    
    # Form for training data submission
    with st.form("training_form", clear_on_submit=False):
        # Input fields (ensure unique keys for all widgets)
        date = st.date_input("Date", key="date_input")
        hpc_code = st.text_input("HPC Code", key="hpc_code_input")
        hpc_name = st.text_input("HPC Name", key="hpc_name_input")
        trainer = st.selectbox("Training conducted by", ["Guru", "Balaji"], key="trainer_select")
        topics = st.selectbox("Training Topic", [
            "Balanced Nutrition", "Fodder Enrichment", "EVM for Mastitis, Diarrhea, Repeat breeding"
        ], key="topics_select")
        volume = st.text_input("Volume (LPD)", key="volume_input")
        avg_fat = st.text_input("Average Fat (%)", key="avg_fat_input")
        avg_snf = st.text_input("Average SNF (%)", key="avg_snf_input")
        pourers_total = st.text_input("Pourers at HPC (Total)", key="pourers_total_input")
        pourers_attended = st.text_input("Pourers Attended Training", key="pourers_attended_input")
        heritage_users = st.text_input("Heritage Feed Using Farmers", key="heritage_users_input")
        non_heritage_users = st.text_input("Non-Heritage Feed Using Farmers", key="non_heritage_users_input")
        awareness_feed = st.selectbox("Feed Awareness (Yes/No)", ["Yes", "No"], key="awareness_feed_select")
        awareness_supplements = st.selectbox("Supplements Awareness (Yes/No)", ["Yes", "No"], key="awareness_supplements_select")
        awareness_vet = st.selectbox("Veterinary Services Awareness (Yes/No)", ["Yes", "No"], key="awareness_vet_select")
        awareness_ai = st.selectbox("AI Services Awareness (Yes/No)", ["Yes", "No"], key="awareness_ai_select")
        awareness_loans = st.selectbox("Loan Awareness (Yes/No)", ["Yes", "No"], key="awareness_loans_select")
        awareness_insurance = st.selectbox("Cattle Insurance Awareness (Yes/No)", ["Yes", "No"], key="awareness_insurance_select")
        awareness_gpa = st.selectbox("GPA Policy Awareness (Yes/No)", ["Yes", "No"], key="awareness_gpa_select")
        key_insights = st.text_area("Key Insights", key="key_insights_area")
        photo_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"], key="photo_uploader")
        
        # Submit button for the form (triggers review)
        submit_button_review = st.form_submit_button("Review Entry") # No need for key here, it's the only one in the form

    # Handle review submission
    if submit_button_review:
        # Store form data and photo in session state for review stage
        st.session_state.form_data = {
            "date": str(date), # Convert date object to string for consistency
            "hpc_code": hpc_code,
            "hpc_name": hpc_name,
            "trainer": trainer,
            "topic": topics,
            "volume": volume,
            "avg_fat": avg_fat,
            "avg_snf": avg_snf,
            "pourers_total": pourers_total,
            "pourers_attended": pourers_attended,
            "heritage_users": heritage_users,
            "non_heritage_users": non_heritage_users,
            "awareness_feed": awareness_feed,
            "awareness_supplements": awareness_supplements,
            "awareness_vet": awareness_vet,
            "awareness_ai": awareness_ai,
            "awareness_loans": awareness_loans,
            "awareness_insurance": awareness_insurance,
            "awareness_gpa": awareness_gpa,
            "key_insights": key_insights,
            "email": st.session_state.user_email
        }
        st.session_state.uploaded_photo = photo_file
        st.session_state.show_review = True # Set flag to show review section

    # --- Review and Final Submit Section (conditionally displayed) ---
    if st.session_state.show_review:
        st.subheader("Review Your Entry")
        st.info("Please review the details below. If everything is correct, click 'Confirm & Submit'.")

        # Display stored form data from session state
        for key, value in st.session_state.form_data.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        if st.session_state.uploaded_photo:
            st.image(st.session_state.uploaded_photo, caption="Uploaded Photo", use_column_width=True)
        
        # Confirmation checkbox
        confirm_checkbox = st.checkbox("I confirm that the above information is correct.", key="confirm_checkbox_final")
        
        # Final submission button (outside the initial st.form)
        if confirm_checkbox and st.button("Confirm & Submit Entry Now", key="final_submit_entry_button"):
            # Get data from session state
            data_to_save = st.session_state.form_data
            photo_to_save = st.session_state.uploaded_photo
            
            # Save the submission and get the photo filename
            saved_photo_filename = save_submission(data_to_save, photo_to_save)
            
            # Ensure the photo_filename is also added to the data_to_save before saving to CSV
            # This is critical if save_submission *doesn't* modify the passed data dict in place
            # or if it returns only the filename.
            # In our `save_submission` function, the `photo_filename` is added to the `df_new_entry`
            # so the CSV will contain it.
            
            st.success("Your training submission has been saved successfully!")
            st.balloons()
            
            # Reset session state variables to clear form and hide review
            st.session_state.show_review = False
            st.session_state.form_data = {}
            st.session_state.uploaded_photo = None
            st.experimental_rerun() # Re-run to refresh the app state and clear the form

with tabs[1]: # Admin Panel Tab
    st.header("Admin Panel")
    if is_admin:
        st.success("Admin Access Granted")

        # --- Data Table and CSV Download ---
        st.subheader("Submitted Training Data")
        df_submissions = get_all_data()
        if not df_submissions.empty:
            st.dataframe(df_submissions, use_container_width=True) # Display dataframe
            
            # Download button for all data
            csv_data = df_submissions.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download All Data (CSV)",
                data=csv_data,
                file_name="training_submissions.csv",
                mime="text/csv",
                key="download_all_csv_admin"
            )
        else:
            st.info("No training submissions recorded yet.")

        # --- Photo Viewing and Download ---
        st.subheader("Uploaded Photos")
        photo_paths = get_all_photos_paths()
        
        if photo_paths:
            # Download all photos as a single ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for photo_path in photo_paths:
                    # Add photo to zip, using only its filename within the zip
                    zf.write(photo_path, os.path.basename(photo_path))
            
            st.download_button(
                label="Download All Photos (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="training_photos.zip",
                mime="application/zip",
                key="download_all_photos_zip_admin"
            )

            st.write("#### Individual Photos:")
            # Display individual photos in a grid
            num_cols = 4 # Adjust as needed
            cols = st.columns(num_cols)
            for i, photo_path in enumerate(photo_paths):
                with cols[i % num_cols]:
                    st.image(photo_path, caption=os.path.basename(photo_path), use_column_width="always")
        else:
            st.info("No photos uploaded yet.")
    else:
        st.warning("Enter an admin email for access to the Admin Panel.")
