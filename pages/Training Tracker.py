import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile
from io import BytesIO

# ---- SETUP ---- #
# Configure the Streamlit page settings
st.set_page_config(page_title="Training Tracker", layout="wide")

# Define authorized admin email addresses
ADMIN_EMAILS = [
    "mkaushal@tns.org",
    "rsomanchi@tns.org",
    "gmreddy@tns.org",
    "kbalaji@tns.org"
]

# Define file paths for data storage
DATA_FILE = "submissions.csv"  # CSV file to store training submissions
PHOTO_DIR = "photos"           # Directory to store uploaded photos

# Ensure the photo directory exists; create it if it doesn't
os.makedirs(PHOTO_DIR, exist_ok=True)

# Initialize Streamlit's session state variables
# These variables help maintain state across app reruns, crucial for multi-step forms and user authentication
if 'show_review' not in st.session_state:
    st.session_state.show_review = False  # Controls visibility of the review section
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}       # Stores data from the form before final submission
if 'uploaded_photo' not in st.session_state:
    st.session_state.uploaded_photo = None # Stores the uploaded photo object temporarily
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""       # Stores the current user's email for admin checks

# Helper function to save submission data and associated photo
def save_submission(data, photo_file):
    """
    Saves the training submission data to a CSV file and the uploaded photo to a directory.
    Ensures all expected columns are present in the DataFrame.
    """
    # Define all expected columns to ensure consistency in the CSV
    all_columns = [
        "timestamp", "date", "hpc_code", "hpc_name", "trainer", "topic", # 'topic' will now store a string of joined topics
        "volume", "avg_fat", "avg_snf", "pourers_total", "pourers_attended",
        "heritage_users", "non_heritage_users", "awareness_feed",
        "awareness_supplements", "awareness_vet", "awareness_ai",
        "awareness_loans", "awareness_insurance", "awareness_gpa",
        "key_insights", "email", "photo_filename" # Added photo_filename column
    ]
    
    # Create a dictionary with default None values for all columns
    # Then update it with the actual data received
    row_data = {col: None for col in all_columns}
    row_data.update(data)

    # Create a new DataFrame for the current entry
    df_new_entry = pd.DataFrame([row_data])

    # Check if the data file already exists
    if os.path.exists(DATA_FILE):
        # If it exists, read it and concatenate the new entry
        df_existing = pd.read_csv(DATA_FILE)
        df = pd.concat([df_existing, df_new_entry], ignore_index=True)
    else:
        # If not, the new entry becomes the DataFrame
        df = df_new_entry

    # Save the (updated) DataFrame to CSV
    df.to_csv(DATA_FILE, index=False)

    # Handle photo saving
    photo_filename_in_csv = "" # Initialize variable to store photo filename
    if photo_file is not None:
        # Generate a unique filename using timestamp and a relevant identifier
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use HPC code, HPC name, or a generic timestamp as part of the filename
        identifier = data.get('hpc_code', '').replace(' ', '_') or \
                     data.get('hpc_name', '').replace(' ', '_') or \
                     f"submission_{timestamp_str}"
        file_extension = os.path.splitext(photo_file.name)[1] # Get original file extension
        photo_filename = f"{identifier}_{timestamp_str}{file_extension}"
        photo_path = os.path.join(PHOTO_DIR, photo_filename)
        
        # Write the photo's bytes to the file
        with open(photo_path, "wb") as f:
            f.write(photo_file.getbuffer()) # st.file_uploader provides a BytesIO object
        
        photo_filename_in_csv = photo_filename # Store only the filename to be saved in CSV

    return photo_filename_in_csv # Return the filename saved (or empty string if no photo)

# Helper function to get all submission data from the CSV
@st.cache_data # Cache data loading for performance
def get_all_data():
    """Reads and returns all submission data from the CSV file."""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame() # Return empty DataFrame if file doesn't exist

# Helper function to get paths of all uploaded photos
def get_all_photos_paths():
    """Returns a list of full paths to all image files in the photo directory."""
    if os.path.exists(PHOTO_DIR):
        # Filter for common image file extensions
        image_files = [f for f in os.listdir(PHOTO_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))]
        return [os.path.join(PHOTO_DIR, f) for f in image_files]
    else:
        return [] # Return empty list if directory doesn't exist

# ---- MAIN APP CONTENT ---- #
st.title("Training Tracker")

# Authentication: User email input
# The user's email is stored in session state to persist across reruns
user_email_input = st.text_input("Enter your email:", value=st.session_state.user_email, key="user_email_input").strip()

# If the entered email changes, update session state and rerun the app
if user_email_input != st.session_state.user_email:
    st.session_state.user_email = user_email_input
    st.rerun() # Rerun to update admin status and content visibility

is_admin = st.session_state.user_email in ADMIN_EMAILS # Check if the current user is an admin

# Create tabs for navigation between "Submit Entry" and "Admin Panel"
tabs = st.tabs(["Submit Entry", "Admin Panel"])

with tabs[0]: # "Submit Entry" Tab Content
    st.header("Submit Training Data")
    
    # Training data submission form
    # clear_on_submit=False allows retaining values until explicitly cleared by rerun
    with st.form("training_form", clear_on_submit=False):
        # Input fields for training data
        date = st.date_input("Date", key="date_input")
        hpc_code = st.text_input("HPC Code", key="hpc_code_input")
        hpc_name = st.text_input("HPC Name", key="hpc_name_input")
        trainer = st.selectbox("Training conducted by", ["Guru", "Balaji"], key="trainer_select")
        
        # --- MULTIPLE SELECT FOR TRAINING TOPIC ---
        available_topics = [
            "Balanced Nutrition", 
            "Fodder Enrichment", 
            "EVM for Mastitis", 
            "Diarrhea",         
            "Repeat breeding"   
        ]
        # Using st.multiselect allows choosing multiple options
        topics = st.multiselect("Training Topic (Select all that apply)", available_topics, key="topics_select")
        # --- END MULTIPLE SELECT ---

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
        
        # The first submit button triggers the review phase
        submit_button_review = st.form_submit_button("Review Entry")

    # Handle the review submission (this block runs if 'Review Entry' was clicked)
    if submit_button_review:
        # Convert the list of selected topics into a comma-separated string for storage
        topics_for_storage = ", ".join(topics) if topics else "" 

        # Store all form data and the uploaded photo in session state
        # This allows the data to persist and be available for the final submission step
        st.session_state.form_data = {
            "date": str(date), # Convert date object to string for CSV compatibility
            "hpc_code": hpc_code,
            "hpc_name": hpc_name,
            "trainer": trainer,
            "topic": topics_for_storage, # Store the joined string here
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
        st.session_state.show_review = True # Set flag to display the review section

    # --- Review and Final Submit Section (conditionally displayed) ---
    # This section appears only if 'show_review' is True in session state
    if st.session_state.show_review:
        st.subheader("Review Your Entry")
        st.info("Please review the details below. If everything is correct, click 'Confirm & Submit'.")

        # Display all stored form data for the user to review
        for key, value in st.session_state.form_data.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Display the uploaded photo if one exists
        if st.session_state.uploaded_photo:
            st.image(st.session_state.uploaded_photo, caption="Uploaded Photo", use_column_width=True)
        
        # Confirmation checkbox before final submission
        confirm_checkbox = st.checkbox("I confirm that the above information is correct.", key="confirm_checkbox_final")
        
        # Final submission button (this is a regular st.button, not part of the initial st.form)
        if confirm_checkbox and st.button("Confirm & Submit Entry Now", key="final_submit_entry_button"):
            # Retrieve data from session state for saving
            data_to_save = st.session_state.form_data
            photo_to_save = st.session_state.uploaded_photo
            
            # Call the helper function to save data and photo
            save_submission(data_to_save, photo_to_save)
            
            # Display success message and visual feedback
            st.success("Your training submission has been saved successfully!")
            st.balloons()
            
            # Reset session state variables to clear the form and hide the review section
            st.session_state.show_review = False
            st.session_state.form_data = {}
            st.session_state.uploaded_photo = None
            
            # Rerun the app to refresh the state and clear the displayed form fields
            st.rerun()

with tabs[1]: # "Admin Panel" Tab Content
    st.header("Admin Panel")
    # Check if the current user's email is in the ADMIN_EMAILS list
    if is_admin:
        st.success("Admin Access Granted")

        # --- Data Table and CSV Download ---
        st.subheader("Submitted Training Data")
        df_submissions = get_all_data() # Load all submission data
        if not df_submissions.empty:
            # Display the data in an interactive DataFrame
            st.dataframe(df_submissions, use_container_width=True)
            
            # Download button for the entire CSV data
            csv_data = df_submissions.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download All Data (CSV)",
                data=csv_data,
                file_name="training_submissions.csv",
                mime="text/csv",
                key="download_all_csv_admin" # Unique key for this button
            )
        else:
            st.info("No training submissions recorded yet.")

        # --- Photo Viewing and Download ---
        st.subheader("Uploaded Photos")
        photo_paths = get_all_photos_paths() # Get paths of all photos
        
        if photo_paths:
            # Prepare all photos for download as a single ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for photo_path in photo_paths:
                    # Add each photo to the zip file using its base filename
                    zf.write(photo_path, os.path.basename(photo_path))
            
            # Download button for the ZIP archive of photos
            st.download_button(
                label="Download All Photos (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="training_photos.zip",
                mime="application/zip",
                key="download_all_photos_zip_admin" # Unique key
            )

            st.write("#### Individual Photos:")
            # Display individual photos in a grid layout
            num_cols = 4 # Define how many columns for photos (e.g., 4 photos per row)
            cols = st.columns(num_cols)
            for i, photo_path in enumerate(photo_paths):
                with cols[i % num_cols]: # Cycle through the columns
                    st.image(photo_path, caption=os.path.basename(photo_path), use_column_width="always")
        else:
            st.info("No photos uploaded yet.")
    else:
        # Message shown if the user is not an admin
        st.warning("Enter an admin email for access to the Admin Panel.")
