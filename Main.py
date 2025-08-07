import streamlit as st
import pandas as pd
import os
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Heritage Dairy Management System",
    page_icon="🐄",
    layout="wide"
)

st.title("Welcome to Heritage Dairy Management System 🐄")
st.markdown("""
    This application helps manage various aspects of dairy farming operations, including:

    * **SNF Follow-up Survey**: Record and review detailed farmer and farm data related to SNF.
    * **Training Tracker**: Log and monitor farmer training sessions and awareness levels.

    If you've set up a multi-page app in Streamlit, you can use the navigation menu on the left. Otherwise, this main page provides a dashboard overview.
""")

st.sidebar.markdown("---")
st.sidebar.header("About the App")
st.sidebar.write("Developed for Heritage Dairy operations to streamline data collection and progress tracking.")
st.sidebar.write("Version: 1.0.0")

st.header("📊 Progress Overview")
st.markdown("Here you can see real-time insights into your survey and training activities.")

SNF_RESPONSES_FILE = "responses.csv"
TRAINING_SUBMISSIONS_FILE = "submissions.csv"

@st.cache_data
def load_data(file_path):
    """
    Loads data from a CSV file. Handles cases where the file
    doesn't exist or is empty. Includes basic column cleaning.
    """
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Clean column names by stripping whitespace
            df.columns = df.columns.str.strip()
            return df
        except pd.errors.EmptyDataError:
            st.warning(f"The file {os.path.basename(file_path)} is empty. No data to display.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading {os.path.basename(file_path)}: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

progress_data = {}

col1, col2 = st.columns(2)

with col1:
    st.subheader("SNF Follow-up Survey Progress")
    snf_df = load_data(SNF_RESPONSES_FILE)

    if not snf_df.empty:
        snf_total = len(snf_df)
        progress_data['SNF'] = snf_df
        
        st.write(f"**Total Surveys Completed:** `{snf_total}`")

        if 'Surveyor Name' in snf_df.columns:
            snf_by_surveyor = snf_df['Surveyor Name'].value_counts()
            st.markdown("##### Surveys by Surveyor")
            fig_surveyor_snf = px.bar(
                snf_by_surveyor,
                x=snf_by_surveyor.index,
                y=snf_by_surveyor.values,
                labels={'x': 'Surveyor', 'y': 'Number of Surveys'},
                title="Number of SNF Surveys per Surveyor",
                color=snf_by_surveyor.index,
                template="streamlit"
            )
            st.plotly_chart(fig_surveyor_snf, use_container_width=True)
            st.dataframe(snf_by_surveyor.rename_axis('Surveyor').reset_index(name='Surveys Completed'), use_container_width=True)
        
        # Check for both "SNF in the list" and "SNF in the list (%)"
        snf_col = None
        if 'SNF in the list' in snf_df.columns:
            snf_col = 'SNF in the list'
        elif 'SNF in the list (%)' in snf_df.columns:
            snf_col = 'SNF in the list (%)'
            
        if snf_col:
            snf_values = pd.to_numeric(snf_df[snf_col].astype(str).str.replace('%', ''), errors='coerce').dropna()
            
            if not snf_values.empty:
                st.markdown("##### SNF Distribution (in List)")
                fig_snf_dist = px.histogram(
                    snf_values,
                    nbins=15,
                    title="Distribution of SNF in Farmer List",
                    labels={'value': 'SNF Value (%)', 'count': 'Number of Entries'},
                    template="streamlit"
                )
                st.plotly_chart(fig_snf_dist, use_container_width=True)
            else:
                st.info("No valid numeric SNF values found for distribution.")
        
        st.download_button(
            label="Download SNF Survey Data (CSV)",
            data=snf_df.to_csv(index=False).encode('utf-8'),
            file_name="snf_follow_up_data.csv",
            mime="text/csv",
            key="download_snf_csv"
        )
    else:
        st.info(f"SNF Follow-up survey data not found or is empty ({SNF_RESPONSES_FILE}).")

with col2:
    st.subheader("Training Tracker Progress")
    training_df = load_data(TRAINING_SUBMISSIONS_FILE)

    if not training_df.empty:
        training_total = len(training_df)
        progress_data['Training'] = training_df
        
        st.write(f"**Total Trainings Logged:** `{training_total}`")

        if 'trainer' in training_df.columns:
            training_by_trainer = training_df['trainer'].value_counts()
            st.markdown("##### Trainings by Trainer")
            fig_trainer_training = px.bar(
                training_by_trainer,
                x=training_by_trainer.index,
                y=training_by_trainer.values,
                labels={'x': 'Trainer', 'y': 'Number of Trainings'},
                title="Number of Trainings Conducted per Trainer",
                color=training_by_trainer.index,
                template="streamlit"
            )
            st.plotly_chart(fig_trainer_training, use_container_width=True)
            st.dataframe(training_by_trainer.rename_axis('Trainer').reset_index(name='Trainings Conducted'), use_container_width=True)

        if 'topic' in training_df.columns:
            topics_list = training_df['topic'].str.split(', ').explode()
            training_by_topic = topics_list.value_counts()
            if not training_by_topic.empty:
                st.markdown("##### Trainings by Topic")
                fig_topic_pie = px.pie(
                    training_by_topic,
                    values=training_by_topic.values,
                    names=training_by_topic.index,
                    title="Distribution of Training Topics",
                    template="streamlit"
                )
                st.plotly_chart(fig_topic_pie, use_container_width=True)
            else:
                st.info("No training topics found for distribution.")

        if 'pourers_attended' in training_df.columns and 'pourers_total' in training_df.columns:
            st.markdown("##### Training Attendance Rate")
            
            total_pourers = pd.to_numeric(training_df['pourers_total'], errors='coerce').sum()
            attended_pourers = pd.to_numeric(training_df['pourers_attended'], errors='coerce').sum()

            if total_pourers > 0:
                attendance_rate = (attended_pourers / total_pourers) * 100
                st.metric("Overall Attendance Rate", f"{attendance_rate:.2f}%")
            else:
                st.info("No valid 'Pourers Total' data to calculate attendance rate.")

        st.download_button(
            label="Download Training Tracker Data (CSV)",
            data=training_df.to_csv(index=False).encode('utf-8'),
            file_name="training_tracker_data.csv",
            mime="text/csv",
            key="download_training_csv"
        )
    else:
        st.info(f"Training tracker data not found or is empty ({TRAINING_SUBMISSIONS_FILE}).")

st.markdown("---")

st.subheader("Combined Progress Summary")

if 'SNF' in progress_data or 'Training' in progress_data:
    combined_counts = {
        'SNF Surveys': len(progress_data.get('SNF', pd.DataFrame())),
        'Trainings': len(progress_data.get('Training', pd.DataFrame()))
    }
    
    summary_df = pd.DataFrame([combined_counts])
    st.write("Summary Table:")
    st.dataframe(summary_df, use_container_width=True)

    fig_combined = px.bar(
        summary_df.melt(var_name="Category", value_name="Count"),
        x="Category",
        y="Count",
        title="Combined Activity Counts",
        color="Category",
        template="streamlit"
    )
    st.plotly_chart(fig_combined, use_container_width=True)

    st.download_button(
        label="Download Combined Progress Summary (CSV)",
        data=summary_df.to_csv(index=False).encode('utf-8'),
        file_name="combined_progress_summary.csv",
        mime="text/csv",
        key="download_combined_csv"
    )

    total_completed = combined_counts['SNF Surveys'] + combined_counts['Trainings']
    overall_target = 100
    
    if overall_target > 0:
        percent = total_completed / overall_target
        st.markdown("##### Overall Progress")
        st.progress(min(percent, 1.0), text=f"Overall Progress: {total_completed}/{overall_target} activities ({percent:.1%})")
    else:
        st.warning("Set an 'overall_target' variable (e.g., `overall_target = 100`) to see the combined progress bar.")
else:
    st.info("No survey or training data available to generate combined progress. Please submit some entries in the respective modules to see the dashboard come alive!")
