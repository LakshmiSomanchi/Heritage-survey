import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

def save_submission(data, photo_file):
    # Save form data
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    # Save photo
    if photo_file is not None:
        photo_path = os.path.join(PHOTO_DIR, data['timestamp'] + "_" + photo_file.name)
        with open(photo_path, "wb") as f:
            f.write(photo_file.getbuffer())
        return photo_path
    return None

def get_all_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame()

def get_all_photos():
    if os.path.exists(PHOTO_DIR):
        return [os.path.join(PHOTO_DIR, f) for f in os.listdir(PHOTO_DIR)]
    else:
        return []

# ---- MAIN APP ---- #
st.title("Training Tracker")

# Authentication: email input
user_email = st.text_input("Enter your email:", key="user_email").strip()
is_admin = user_email in ADMIN_EMAILS

tabs = st.tabs(["Submit Entry", "Admin Panel"])

with tabs[0]:
    st.header("Submit Training Data")
    with st.form("training_form", clear_on_submit=False):
        date = st.date_input("Date")
        hpc_code = st.text_input("HPC Code")
        hpc_name = st.text_input("HPC Name")
        trainer = st.selectbox("Training conducted by", ["Guru", "Balaji"])
        topics = st.selectbox("Training Topic", [
            "Balanced Nutrition", "Fodder Enrichment", "EVM for Mastitis, Diarrhea, Repeat breeding"
        ])
        volume = st.text_input("Volume (LPD)")
        avg_fat = st.text_input("Average Fat (%)")
        avg_snf = st.text_input("Average SNF (%)")
        pourers_total = st.text_input("Pourers at HPC (Total)")
        pourers_attended = st.text_input("Pourers Attended Training")
        heritage_users = st.text_input("Heritage Feed Using Farmers")
        non_heritage_users = st.text_input("Non-Heritage Feed Using Farmers")
        awareness_feed = st.text_input("Feed Awareness (Yes/No)")
        awareness_supplements = st.text_input("Supplements Awareness (Yes/No)")
        awareness_vet = st.text_input("Veterinary Services Awareness (Yes/No)")
        awareness_ai = st.text_input("AI Services Awareness (Yes/No)")
        awareness_loans = st.text_input("Loan Awareness (Yes/No)")
        awareness_insurance = st.text_input("Cattle Insurance Awareness (Yes/No)")
        awareness_gpa = st.text_input("GPA Policy Awareness (Yes/No)")
        key_insights = st.text_area("Key Insights")
        photo_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("Review Entry")
    
    # Review and Submit
    if submit_button:
        st.subheader("Review Your Entry")
        st.write(f"**Date:** {date}")
        st.write(f"**HPC Code:** {hpc_code}")
        st.write(f"**HPC Name:** {hpc_name}")
        st.write(f"**Trainer:** {trainer}")
        st.write(f"**Topic:** {topics}")
        st.write(f"**Volume:** {volume}")
        st.write(f"**Fat:** {avg_fat}")
        st.write(f"**SNF:** {avg_snf}")
        st.write(f"**Pourers Total:** {pourers_total}")
        st.write(f"**Attended:** {pourers_attended}")
        st.write(f"**Heritage Users:** {heritage_users}")
        st.write(f"**Non-Heritage Users:** {non_heritage_users}")
        st.write(f"**Feed Awareness:** {awareness_feed}")
        st.write(f"**Supplements Awareness:** {awareness_supplements}")
        st.write(f"**Veterinary Awareness:** {awareness_vet}")
        st.write(f"**AI Awareness:** {awareness_ai}")
        st.write(f"**Loan Awareness:** {awareness_loans}")
        st.write(f"**Insurance Awareness:** {awareness_insurance}")
        st.write(f"**GPA Awareness:** {awareness_gpa}")
        st.write(f"**Key Insights:** {key_insights}")
        if photo_file:
            st.image(photo_file, caption="Uploaded Photo", use_column_width=True)
        if st.button("Submit Entry Now"):
            # Save data
            data = {
                "timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
                "date": date,
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
                "email": user_email
            }
            saved_photo = save_submission(data, photo_file)
            st.success("Your submission has been saved successfully!")

with tabs[1]:
    st.header("Admin Panel")
    if is_admin:
        st.success("Admin Access Granted")
        # Data Table
        df = get_all_data()
        if not df.empty:
            st.dataframe(df)
            st.download_button("Download All Data (CSV)", df.to_csv(index=False), file_name="submissions.csv")
        else:
            st.info("No submissions yet.")

        # Photo Download
        st.subheader("Download Photos")
        photo_files = get_all_photos()
        if photo_files:
            for photo_path in photo_files:
                with open(photo_path, "rb") as f:
                    st.image(f, caption=os.path.basename(photo_path), width=200)
                    st.download_button(
                        label=f"Download {os.path.basename(photo_path)}",
                        data=f,
                        file_name=os.path.basename(photo_path)
                    )
        else:
            st.info("No photos uploaded yet.")
    else:
        st.warning("Enter an admin email for access.")
