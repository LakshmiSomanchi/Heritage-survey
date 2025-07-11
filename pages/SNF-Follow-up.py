import streamlit as st
import pandas as pd
import os
st.title("Survey Data Entry Form")

# 1. Surveyor Name Dropdown
surveyor_name = st.selectbox("Surveyor Name", ["Guru", "Balaji"])

# 2–45. Text Inputs
date_of_visit = st.text_input("Date of Visit")
hpc_code = st.text_input("HPC Code")
hpc_name = st.text_input("HPC Name")
farmer_name = st.text_input("Farmer Name")
farmer_code = st.text_input("Farmer Code")
gender = st.text_input("Gender")
fat_list = st.text_input("Fat in the list")
snf_list = st.text_input("SNF in the list")
vol_list = st.text_input("Vol in the list")

# Repeating groups
as_on_date_fat = st.text_input("As on date Fat in the farmer slip")
as_on_date_snf = st.text_input("As on date SNF in the farmer slip")
as_on_date_vol = st.text_input("As on date Vol in the farmer slip")

number_of_cows = st.text_input("Number of Cows")
jersey_cross = st.text_input("Jersey /Cross")
hf_cross = st.text_input("HF/Cross")

jersey_milk = st.text_input("No of jersey cows in milk")
jersey_vol_lpd = st.text_input("Vol-LPD (Jersey)")
jersey_fat = st.text_input("Fat (Jersey)")
jersey_snf = st.text_input("SNF (Jersey)")

hf_milk = st.text_input("No of HF cows in milk")
hf_vol_lpd = st.text_input("Vol-LPD (HF)")
hf_fat = st.text_input("Fat (HF)")
hf_snf = st.text_input("SNF (HF)")

desi_milk = st.text_input("No of Desi cows in milk")
desi_vol_lpd = st.text_input("Vol-LPD (Desi)")
desi_fat = st.text_input("Fat (Desi)")
desi_snf = st.text_input("SNF (Desi)")

buffalo_milk = st.text_input("No of Buffalo")
buffalo_vol_lpd = st.text_input("Vol-LPD (Buffalo)")

green_fodder = st.text_input("Green Fodder Yes/No")
green_fodder_type = st.text_input("Type of Green Fodder")
green_fodder_qty = st.text_input("Quantity of Green Fodder (Kg/day)")

dry_fodder = st.text_input("Dry Fodder Yes/No")
dry_fodder_type = st.text_input("Type of Dry Fodder")
dry_fodder_qty = st.text_input("Quantity of Dry Fodder (Kg/day)")

pellet_feed = st.text_input("Pellet Feed Yes/No")
heritage_feed = st.text_input("If Yes, Heritage Feed Yes/No")
feed_variant = st.text_input("If Yes, Mention the Feed Variant")
feed_brand = st.text_input("If No, Mention the Feed Brand")
pellet_qty = st.text_input("Quantity of Pellet Feed (Kg/day)")

mineral_mix = st.text_input("Mineral Mixture Yes/No")
mineral_mix_brand = st.text_input("Mineral Mixture Brand")
mineral_mix_qty = st.text_input("Quantity of Mineral Mixture (gm/day)")
key_insights = st.text_area("Key Insights")

# --- File paths (you should adjust to your storage logic)
PHOTOS_DIR = "photos/"
RESPONSES_CSV = "responses.csv"

st.title("SNF Follow-up Survey")

# --- Normal survey form
with st.form("survey_form", clear_on_submit=False):
    # Example fields; add your own fields as needed
    name = st.text_input("Name")
    response = st.text_area("Survey Response")
    photo = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
    
    # Review section
    if st.form_submitted():
        if name and response:
            st.write("**Review your submission:**")
            st.write(f"Name: {name}")
            st.write(f"Response: {response}")
            if photo:
                st.image(photo)
            confirm = st.checkbox("I confirm that the above information is correct.")
            if confirm:
                # Save the response (implement as per your storage logic)
                # Save the uploaded photo
                if photo:
                    photo_path = os.path.join(PHOTOS_DIR, photo.name)
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())
                # Save to CSV
                df = pd.DataFrame([[name, response, photo.name if photo else ""]], columns=["Name", "Response", "Photo"])
                if os.path.exists(RESPONSES_CSV):
                    df.to_csv(RESPONSES_CSV, mode="a", header=False, index=False)
                else:
                    df.to_csv(RESPONSES_CSV, index=False)
                st.success("Your response has been submitted!")
        else:
            st.error("Please fill all required fields.")

# --- Admin email list
ADMIN_EMAILS = [
    "mkaushal@tns.org",
    "rsomanchi@tns.org",
    "kbalaji@tns.org",
    "gmreddy@tns.org"
]

# --- Admin Access Section
with st.expander("Admin Access (Download Data)"):
    admin_email = st.text_input("Enter admin email")
    if st.button("Login as Admin"):
        if admin_email in ADMIN_EMAILS:
            st.success("Admin access granted.")
            # Download responses
            if os.path.exists(RESPONSES_CSV):
                with open(RESPONSES_CSV, "rb") as f:
                    st.download_button(
                        label="Download Survey Responses (CSV)",
                        data=f,
                        file_name="responses.csv",
                        mime="text/csv"
                    )
            # Download all photos as a zip file
            import zipfile
            from io import BytesIO
            if os.path.exists(PHOTOS_DIR) and os.listdir(PHOTOS_DIR):
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for photo_file in os.listdir(PHOTOS_DIR):
                        zf.write(os.path.join(PHOTOS_DIR, photo_file), photo_file)
                st.download_button(
                    label="Download All Photos (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="photos.zip",
                    mime="application/zip"
                )
        else:
            st.error("Access denied. You are not an admin.")


if st.button("Submit"):
    st.success("Form Submitted Successfully!")
