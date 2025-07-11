import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Heritage Dairy Management System",
    page_icon="🐄",
    layout="wide"
)

st.title("Welcome to Heritage Dairy Management System 🐄")
st.markdown("""
    This application helps manage various aspects of dairy farming operations, including:

    * **Heritage SNF Survey**: Record and review detailed farmer and farm data.
    * **SNF Follow-up**: Track follow-up actions related to SNF (Solids-Non-Fat) measurements.
    * **Training Tracker**: Log and monitor farmer training sessions.

    Please use the navigation menu on the left to access different modules.
""")
st.info("Select a module from the sidebar to begin.")

st.sidebar.markdown("---")
st.sidebar.header("About the App")
st.sidebar.write("Developed for Heritage Dairy operations.")
st.sidebar.write("Version: 1.0.0")

# --- Progress Overview Section ---
st.header("📊 Progress Overview")

# --- File paths (adjust if needed) ---
snf_file = "SNF-Follow-up.csv"
training_file = "Training_Tracker.csv"

progress_data = {}

# --- SNF Follow Up Survey Progress ---
if os.path.exists(snf_file):
    snf_df = pd.read_csv(snf_file)
    snf_total = len(snf_df)
    snf_by_surveyor = snf_df['Surveyor Name'].value_counts() if 'Surveyor Name' in snf_df else None
    progress_data['SNF'] = snf_df

    st.subheader("SNF Follow-up Survey Progress")
    st.write(f"**Total Surveys Completed:** {snf_total}")

    if snf_by_surveyor is not None and not snf_by_surveyor.empty:
        st.bar_chart(snf_by_surveyor)
        st.write("Breakdown by Surveyor:")
        st.dataframe(snf_by_surveyor.rename_axis('Surveyor').reset_index(name='Surveys Completed'))
    st.download_button("Download SNF Survey Data (CSV)", snf_df.to_csv(index=False), file_name="SNF-Follow-up.csv")
else:
    st.info("SNF Follow-up survey data not found (SNF-Follow-up.csv).")

# --- Training Tracker Progress ---
if os.path.exists(training_file):
    training_df = pd.read_csv(training_file)
    training_total = len(training_df)
    trainer_col = "Training conducted by" if "Training conducted by" in training_df else None
    training_by_trainer = training_df[trainer_col].value_counts() if trainer_col else None
    progress_data['Training'] = training_df

    st.subheader("Training Tracker Progress")
    st.write(f"**Total Trainings Logged:** {training_total}")

    if training_by_trainer is not None and not training_by_trainer.empty:
        st.bar_chart(training_by_trainer)
        st.write("Breakdown by Trainer:")
        st.dataframe(training_by_trainer.rename_axis('Trainer').reset_index(name='Trainings Conducted'))
    st.download_button("Download Training Tracker Data (CSV)", training_df.to_csv(index=False), file_name="Training_Tracker.csv")
else:
    st.info("Training tracker data not found (Training_Tracker.csv).")

# --- Combined Progress Overview ---
if 'SNF' in progress_data or 'Training' in progress_data:
    st.subheader("Combined Progress Summary")
    combined_counts = {
        'SNF Surveys': len(progress_data['SNF']) if 'SNF' in progress_data else 0,
        'Trainings': len(progress_data['Training']) if 'Training' in progress_data else 0
    }
    st.write("Summary Table:")
    summary_df = pd.DataFrame([combined_counts])
    st.dataframe(summary_df)

    # Download combined summary as CSV
    st.download_button(
        "Download Combined Progress Summary (CSV)",
        summary_df.to_csv(index=False),
        file_name="Combined_Progress_Summary.csv"
    )

    # Optional: Simple progress bar (if you have a target, e.g. 100 for each)
    total_completed = combined_counts['SNF Surveys'] + combined_counts['Trainings']
    target = 100  # Change to your real target if known
    percent = total_completed / max(target, 1)
    st.progress(min(percent, 1.0), text=f"Progress: {total_completed}/{target*2 if target else total_completed}")
