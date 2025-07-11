import streamlit as st
import pandas as pd
import os
import zipfile
from io import BytesIO
import datetime # Import datetime for accurate timestamping

st.title("SNF Follow-up Survey")

# --- File/Directory settings
PHOTOS_DIR = "photos"
RESPONSES_CSV = "responses.csv"

# Ensure the photos directory exists
os.makedirs(PHOTOS_DIR, exist_ok=True)

# --- Admin email list
ADMIN_EMAILS = [
    "mkaushal@tns.org",
    "rsomanchi@tns.org",
    "kbalaji@tns.org",
    "gmreddy@tns.org"
]

# --- Main Survey Form
with st.form("survey_form", clear_on_submit=False):
    st.header("Farmer Survey Details")
    surveyor_name = st.selectbox("Surveyor Name", ["Guru", "Balaji"])
    date_of_visit = st.text_input("Date of Visit (e.g., DD-MM-YYYY)") # Added example format
    hpc_code = st.text_input("HPC Code")
    hpc_name = st.text_input("HPC Name")
    farmer_name = st.text_input("Farmer Name")
    farmer_code = st.text_input("Farmer Code")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"]) # Changed to selectbox for consistency
    fat_list = st.text_input("Fat in the list (%)") # Added unit hint
    snf_list = st.text_input("SNF in the list (%)") # Added unit hint
    vol_list = st.text_input("Vol in the list (LPD)") # Added unit hint

    st.subheader("Farmer Slip Details (As on date)")
    as_on_date_fat = st.text_input("Fat in the farmer slip (%)")
    as_on_date_snf = st.text_input("SNF in the farmer slip (%)")
    as_on_date_vol = st.text_input("Vol in the farmer slip (LPD)")

    st.subheader("Cattle Details")
    number_of_cows = st.text_input("Total Number of Cows")
    jersey_cross = st.text_input("Jersey /Cross (Count)")
    hf_cross = st.text_input("HF/Cross (Count)")

    st.write("---") # Separator
    st.markdown("##### Jersey Cows (In Milk)")
    jersey_milk = st.text_input("No. of Jersey cows in milk")
    jersey_vol_lpd = st.text_input("Vol-LPD (Jersey Cows)")
    jersey_fat = st.text_input("Fat (Jersey Cows) (%)")
    jersey_snf = st.text_input("SNF (Jersey Cows) (%)")

    st.markdown("##### HF Cows (In Milk)")
    hf_milk = st.text_input("No. of HF cows in milk")
    hf_vol_lpd = st.text_input("Vol-LPD (HF Cows)")
    hf_fat = st.text_input("Fat (HF Cows) (%)")
    hf_snf = st.text_input("SNF (HF Cows) (%)")

    st.markdown("##### Desi Cows (In Milk)")
    desi_milk = st.text_input("No. of Desi cows in milk")
    desi_vol_lpd = st.text_input("Vol-LPD (Desi Cows)")
    desi_fat = st.text_input("Fat (Desi Cows) (%)")
    desi_snf = st.text_input("SNF (Desi Cows) (%)")

    st.markdown("##### Buffalo (In Milk)")
    buffalo_milk = st.text_input("No. of Buffalo in milk")
    buffalo_vol_lpd = st.text_input("Vol-LPD (Buffalo)")

    st.subheader("Fodder & Feed Details")
    green_fodder = st.selectbox("Green Fodder Available?", ["Yes", "No"]) # Changed to selectbox
    green_fodder_type = st.text_input("Type of Green Fodder (if Yes)")
    green_fodder_qty = st.text_input("Quantity of Green Fodder (Kg/day)")

    dry_fodder = st.selectbox("Dry Fodder Available?", ["Yes", "No"]) # Changed to selectbox
    dry_fodder_type = st.text_input("Type of Dry Fodder (if Yes)")
    dry_fodder_qty = st.text_input("Quantity of Dry Fodder (Kg/day)")

    pellet_feed = st.selectbox("Pellet Feed Used?", ["Yes", "No"]) # Changed to selectbox
    heritage_feed = st.text_input("If Yes, Heritage Feed (Yes/No)")
    feed_variant = st.text_input("If Yes, Mention the Feed Variant")
    feed_brand = st.text_input("If No, Mention the Feed Brand")
    pellet_qty = st.text_input("Quantity of Pellet Feed (Kg/day)")

    mineral_mix = st.selectbox("Mineral Mixture Used?", ["Yes", "No"]) # Changed to selectbox
    mineral_mix_brand = st.text_input("Mineral Mixture Brand (if Yes)")
    mineral_mix_qty = st.text_input("Quantity of Mineral Mixture (gm/day)")

    key_insights = st.text_area("Key Insights/Observations")

    photo = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Review & Submit")

if submitted:
    # Review Section
    st.header("Review your submission:")
    st.write(f"**Surveyor Name:** {surveyor_name}")
    st.write(f"**Date of Visit:** {date_of_visit}")
    st.write(f"**HPC Code:** {hpc_code}")
    st.write(f"**HPC Name:** {hpc_name}")
    st.write(f"**Farmer Name:** {farmer_name}")
    st.write(f"**Farmer Code:** {farmer_code}")
    st.write(f"**Gender:** {gender}")
    st.write(f"**Fat in the list:** {fat_list}")
    st.write(f"**SNF in the list:** {snf_list}")
    st.write(f"**Vol in the list:** {vol_list}")
    st.write(f"**As on date Fat in the farmer slip:** {as_on_date_fat}")
    st.write(f"**As on date SNF in the farmer slip:** {as_on_date_snf}")
    st.write(f"**As on date Vol in the farmer slip:** {as_on_date_vol}")
    st.write(f"**Number of Cows:** {number_of_cows}")
    st.write(f"**Jersey /Cross:** {jersey_cross}")
    st.write(f"**HF/Cross:** {hf_cross}")
    st.write(f"**No of jersey cows in milk:** {jersey_milk}")
    st.write(f"**Vol-LPD (Jersey):** {jersey_vol_lpd}")
    st.write(f"**Fat (Jersey):** {jersey_fat}")
    st.write(f"**SNF (Jersey):** {jersey_snf}")
    st.write(f"**No of HF cows in milk:** {hf_milk}")
    st.write(f"**Vol-LPD (HF):** {hf_vol_lpd}")
    st.write(f"**Fat (HF):** {hf_fat}")
    st.write(f"**SNF (HF):** {hf_snf}")
    st.write(f"**No of Desi cows in milk:** {desi_milk}")
    st.write(f"**Vol-LPD (Desi):** {desi_vol_lpd}")
    st.write(f"**Fat (Desi):** {desi_fat}")
    st.write(f"**SNF (Desi):** {desi_snf}")
    st.write(f"**No of Buffalo:** {buffalo_milk}")
    st.write(f"**Vol-LPD (Buffalo):** {buffalo_vol_lpd}")
    st.write(f"**Green Fodder Yes/No:** {green_fodder}")
    st.write(f"**Type of Green Fodder:** {green_fodder_type}")
    st.write(f"**Quantity of Green Fodder (Kg/day):** {green_fodder_qty}")
    st.write(f"**Dry Fodder Yes/No:** {dry_fodder}")
    st.write(f"**Type of Dry Fodder:** {dry_fodder_type}")
    st.write(f"**Quantity of Dry Fodder (Kg/day):** {dry_fodder_qty}")
    st.write(f"**Pellet Feed Yes/No:** {pellet_feed}")
    st.write(f"**If Yes, Heritage Feed Yes/No:** {heritage_feed}")
    st.write(f"**If Yes, Mention the Feed Variant:** {feed_variant}")
    st.write(f"**If No, Mention the Feed Brand:** {feed_brand}")
    st.write(f"**Quantity of Pellet Feed (Kg/day):** {pellet_qty}")
    st.write(f"**Mineral Mixture Yes/No:** {mineral_mix}")
    st.write(f"**Mineral Mixture Brand:** {mineral_mix_brand}")
    st.write(f"**Quantity of Mineral Mixture (gm/day):** {mineral_mix_qty}")
    st.write(f"**Key Insights:** {key_insights}")
    if photo:
        st.write("---") # Separator
        st.write("**Uploaded Photo:**")
        st.image(photo, caption=photo.name, width=300) # Added caption

    confirm = st.checkbox("I confirm that the above information is correct.")
    if confirm and st.button("Confirm & Submit"):
        # Save photo
        photo_filename = ""
        if photo:
            # Create a unique filename for the photo using farmer code/name and a timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Use original filename extension
            file_extension = os.path.splitext(photo.name)[1]
            photo_filename = f"{farmer_code or farmer_name}_{timestamp}{file_extension}"
            photo_path = os.path.join(PHOTOS_DIR, photo_filename)
            with open(photo_path, "wb") as f:
                f.write(photo.getbuffer())

        # Prepare DataFrame row
        row = [
            surveyor_name, date_of_visit, hpc_code, hpc_name, farmer_name, farmer_code, gender, fat_list, snf_list, vol_list,
            as_on_date_fat, as_on_date_snf, as_on_date_vol, number_of_cows, jersey_cross, hf_cross,
            jersey_milk, jersey_vol_lpd, jersey_fat, jersey_snf, hf_milk, hf_vol_lpd, hf_fat, hf_snf,
            desi_milk, desi_vol_lpd, desi_fat, desi_snf, buffalo_milk, buffalo_vol_lpd,
            green_fodder, green_fodder_type, green_fodder_qty, dry_fodder, dry_fodder_type, dry_fodder_qty,
            pellet_feed, heritage_feed, feed_variant, feed_brand, pellet_qty, mineral_mix, mineral_mix_brand,
            mineral_mix_qty, key_insights, photo_filename
        ]
        columns = [
            "Surveyor Name", "Date of Visit", "HPC Code", "HPC Name", "Farmer Name", "Farmer Code", "Gender", "Fat in the list", "SNF in the list", "Vol in the list",
            "As on date Fat in the farmer slip", "As on date SNF in the farmer slip", "As on date Vol in the farmer slip", "Number of Cows", "Jersey /Cross", "HF/Cross",
            "No of jersey cows in milk", "Vol-LPD (Jersey)", "Fat (Jersey)", "SNF (Jersey)", "No of HF cows in milk", "Vol-LPD (HF)", "Fat (HF)", "SNF (HF)",
            "No of Desi cows in milk", "Vol-LPD (Desi)", "Fat (Desi)", "SNF (Desi)", "No of Buffalo", "Vol-LPD (Buffalo)",
            "Green Fodder Yes/No", "Type of Green Fodder", "Quantity of Green Fodder (Kg/day)", "Dry Fodder Yes/No", "Type of Dry Fodder", "Quantity of Dry Fodder (Kg/day)",
            "Pellet Feed Yes/No", "If Yes, Heritage Feed Yes/No", "If Yes, Mention the Feed Variant", "If No, Mention the Feed Brand", "Quantity of Pellet Feed (Kg/day)", "Mineral Mixture Yes/No",
            "Mineral Mixture Brand", "Quantity of Mineral Mixture (gm/day)", "Key Insights", "Photo Filename"
        ]
        df = pd.DataFrame([row], columns=columns)

        # Append to CSV
        if os.path.exists(RESPONSES_CSV):
            df.to_csv(RESPONSES_CSV, mode="a", header=False, index=False)
        else:
            df.to_csv(RESPONSES_CSV, index=False)
        st.success("Your response has been submitted!")
        # Clear form by rerunning
        st.experimental_rerun()

---

# Admin Access Section (Download and View Data)

# Fix: Changed 'With' to 'with' here
with st.expander("Admin Access (Download & View Data)"):
    admin_email = st.text_input("Enter admin email")
    if st.button("Login as Admin"):
        if admin_email in ADMIN_EMAILS:
            st.success("Admin access granted.")

            # --- Download Options ---
            st.subheader("Download Options")
            # Download responses
            if os.path.exists(RESPONSES_CSV):
                with open(RESPONSES_CSV, "rb") as f:
                    st.download_button(
                        label="Download All Survey Responses (CSV)",
                        data=f,
                        file_name="responses.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No survey responses recorded yet.")

            # Download all photos as a zip file
            if os.path.exists(PHOTOS_DIR) and os.listdir(PHOTOS_DIR):
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for photo_file in os.listdir(PHOTOS_DIR):
                        # Ensure we write the full path to the file inside the zip, but only the filename in the zip itself
                        zf.write(os.path.join(PHOTOS_DIR, photo_file), photo_file)
                st.download_button(
                    label="Download All Photos (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="photos.zip",
                    mime="application/zip"
                )
            else:
                st.info("No photos uploaded yet.")

            # --- View Real-time Data ---
            st.subheader("View Real-time Data")

            # View CSV Responses
            if os.path.exists(RESPONSES_CSV):
                st.write("#### Survey Responses Table")
                df_responses = pd.read_csv(RESPONSES_CSV)
                st.dataframe(df_responses)
            else:
                st.info("No survey responses to display.")

            # View Uploaded Photos
            st.write("#### Uploaded Photos")
            photo_files = [f for f in os.listdir(PHOTOS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if photo_files:
                # Use st.columns for a nicer grid layout for photos
                cols = st.columns(3) # Display up to 3 photos per row
                for i, photo_file in enumerate(photo_files):
                    with cols[i % 3]: # Cycle through the columns
                        st.image(os.path.join(PHOTOS_DIR, photo_file), caption=photo_file, width=200) # Smaller width for grid
            else:
                st.info("No photos to display.")

        else:
            st.error("Access denied. You are not an admin.")
