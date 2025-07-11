import streamlit as st
import pandas as pd
import os
from io import BytesIO # Needed for creating zip files in memory
import plotly.express as px # For more interactive charts
import plotly.graph_objects as go # Included as it was in previous code, though px is often sufficient

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Heritage Dairy Management System",
    page_icon="🐄",
    layout="wide" # Use wide layout for better dashboard presentation
)

# --- Title and Introduction ---
st.title("Welcome to Heritage Dairy Management System 🐄")
st.markdown("""
    This application helps manage various aspects of dairy farming operations, including:

    * **SNF Follow-up Survey**: Record and review detailed farmer and farm data related to SNF.
    * **Training Tracker**: Log and monitor farmer training sessions and awareness levels.

    If you've set up a multi-page app in Streamlit, you can use the navigation menu on the left. Otherwise, this main page provides a dashboard overview.
""")

# --- Sidebar Content ---
st.sidebar.markdown("---")
st.sidebar.header("About the App")
st.sidebar.write("Developed for Heritage Dairy operations to streamline data collection and progress tracking.")
st.sidebar.write("Version: 1.0.0")

# --- Progress Overview Section ---
st.header("📊 Progress Overview")
st.markdown("Here you can see real-time insights into your survey and training activities.")

# --- Corrected File Paths for Data Sources ---
# These paths should match where your SNF and Training Tracker apps save their data.
SNF_RESPONSES_FILE = "responses.csv"      # Data from SNF Follow-up app
TRAINING_SUBMISSIONS_FILE = "submissions.csv" # Data from Training Tracker app

# --- Data Loading Function ---
@st.cache_data # Cache data to improve performance for larger datasets
def load_data(file_path):
    """
    Loads data from a CSV file. Handles cases where the file
    doesn't exist or is empty. Includes basic column cleaning.
    """
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Basic cleaning: strip whitespace from column names for consistent access
            df.columns = df.columns.str.strip()
            return df
        except pd.errors.EmptyDataError:
            st.warning(f"The file {os.path.basename(file_path)} is empty. No data to display.")
            return pd.DataFrame() # Return empty DataFrame if file is empty
        except Exception as e:
            st.error(f"Error loading {os.path.basename(file_path)}: {e}")
            return pd.DataFrame()
    return pd.DataFrame() # Return empty DataFrame if file does not exist

progress_data = {} # Dictionary to store loaded DataFrames for easy access

# --- Create Columns for Side-by-Side Progress Display ---
col1, col2 = st.columns(2)

with col1:
    # --- SNF Follow Up Survey Progress ---
    st.subheader("SNF Follow-up Survey Progress")
    snf_df = load_data(SNF_RESPONSES_FILE)

    if not snf_df.empty:
        snf_total = len(snf_df)
        progress_data['SNF'] = snf_df # Store for combined summary
        
        st.write(f"**Total Surveys Completed:** `{snf_total}`")

        # Breakdown by Surveyor
        if 'Surveyor Name' in snf_df.columns:
            snf_by_surveyor = snf_df['Surveyor Name'].value_counts()
            st.markdown("##### Surveys by Surveyor")
            fig_surveyor_snf = px.bar(
                snf_by_surveyor, 
                x=snf_by_surveyor.index, 
                y=snf_by_surveyor.values, 
                labels={'x': 'Surveyor', 'y': 'Number of Surveys'},
                title="Number of SNF Surveys per Surveyor",
                color=snf_by_surveyor.index, # Color bars by surveyor
                template="streamlit" # Use Streamlit's default theme
            )
            st.plotly_chart(fig_surveyor_snf, use_container_width=True)
            st.dataframe(snf_by_surveyor.rename_axis('Surveyor').reset_index(name='Surveys Completed'), use_container_width=True)

        # Distribution of SNF in the list
        # Ensure column name exact match and robust numeric conversion
        if 'SNF in the list' in snf_df.columns:
            # Convert to string first to handle potential mixed types, then replace '%' and convert to numeric
            snf_values = pd.to_numeric(snf_df['SNF in the list'].astype(str).str.replace('%', ''), errors='coerce').dropna()
            
            if not snf_values.empty:
                st.markdown("##### SNF Distribution (in List)")
                fig_snf_dist = px.histogram(
                    snf_values, 
                    nbins=15, # Adjust number of bins for desired granularity
                    title="Distribution of SNF in Farmer List",
                    labels={'value': 'SNF Value (%)', 'count': 'Number of Entries'},
                    template="streamlit"
                )
                st.plotly_chart(fig_snf_dist, use_container_width=True)
            else:
                 st.info("No valid numeric SNF values found for distribution.")
        
        # Download button for SNF data
        st.download_button(
            label="Download SNF Survey Data (CSV)",
            data=snf_df.to_csv(index=False).encode('utf-8'),
            file_name="snf_follow_up_data.csv",
            mime="text/csv",
            key="download_snf_csv" # Unique key for this button
        )
    else:
        st.info(f"SNF Follow-up survey data not found or is empty ({SNF_RESPONSES_FILE}).")

with col2:
    # --- Training Tracker Progress ---
    st.subheader("Training Tracker Progress")
    training_df = load_data(TRAINING_SUBMISSIONS_FILE)

    if not training_df.empty:
        training_total = len(training_df)
        progress_data['Training'] = training_df # Store for combined summary
        
        st.write(f"**Total Trainings Logged:** `{training_total}`")

        # Breakdown by Trainer (column name is 'trainer' from the training app's data structure)
        if 'trainer' in training_df.columns:
            training_by_trainer = training_df['trainer'].value_counts()
            st.markdown("##### Trainings by Trainer")
            fig_trainer_training = px.bar(
                training_by_trainer, 
                x=training_by_trainer.index, 
                y=training_by_trainer.values, 
                labels={'x': 'Trainer', 'y': 'Number of Trainings'},
                title="Number of Trainings Conducted per Trainer",
                color=training_by_trainer.index, # Color bars by trainer
                template="streamlit"
            )
            st.plotly_chart(fig_trainer_training, use_container_width=True)
            st.dataframe(training_by_trainer.rename_axis('Trainer').reset_index(name='Trainings Conducted'), use_container_width=True)

        # Breakdown by Training Topic (Pie Chart, column name is 'topic')
        if 'topic' in training_df.columns:
            training_by_topic = training_df['topic'].value_counts()
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
        
        # Training Attendance Rate (columns are 'pourers_attended' and 'pourers_total')
        if 'pourers_attended' in training_df.columns and 'pourers_total' in training_df.columns:
            st.markdown("##### Training Attendance Rate")
            # Convert to numeric, coercing errors to NaN and dropping
            total_pourers = pd.to_numeric(training_df['pourers_total'], errors='coerce').sum()
            attended_pourers = pd.to_numeric(training_df['pourers_attended'], errors='coerce').sum()

            if total_pourers > 0:
                attendance_rate = (attended_pourers / total_pourers) * 100
                st.metric("Overall Attendance Rate", f"{attendance_rate:.2f}%")
            else:
                st.info("No valid 'Pourers Total' data to calculate attendance rate.")

        # Download button for Training data
        st.download_button(
            label="Download Training Tracker Data (CSV)",
            data=training_df.to_csv(index=False).encode('utf-8'),
            file_name="training_tracker_data.csv",
            mime="text/csv",
            key="download_training_csv" # Unique key for this button
        )
    else:
        st.info(f"Training tracker data not found or is empty ({TRAINING_SUBMISSIONS_FILE}).")


st.markdown("---") # Separator for combined summary

# --- Combined Progress Overview ---
st.subheader("Combined Progress Summary")
# Check if any data was loaded into progress_data before trying to summarize
if 'SNF' in progress_data or 'Training' in progress_data:
    combined_counts = {
        'SNF Surveys': len(progress_data.get('SNF', pd.DataFrame())), # Use .get() with default empty DataFrame
        'Trainings': len(progress_data.get('Training', pd.DataFrame()))
    }
    
    summary_df = pd.DataFrame([combined_counts])
    st.write("Summary Table:")
    st.dataframe(summary_df, use_container_width=True)

    # Combined Bar Chart for overall counts
    fig_combined = px.bar(
        summary_df.melt(var_name="Category", value_name="Count"), # Melt DataFrame for easy plotting by category
        x="Category",
        y="Count",
        title="Combined Activity Counts",
        color="Category",
        template="streamlit"
    )
    st.plotly_chart(fig_combined, use_container_width=True)

    # Download combined summary as CSV
    st.download_button(
        label="Download Combined Progress Summary (CSV)",
        data=summary_df.to_csv(index=False).encode('utf-8'),
        file_name="combined_progress_summary.csv",
        mime="text/csv",
        key="download_combined_csv" # Unique key
    )

    # Optional: Simple progress bar (if you have a target)
    total_completed = combined_counts['SNF Surveys'] + combined_counts['Trainings']
    overall_target = 100 # Adjust this to your desired overall target for both activities combined
    
    if overall_target > 0:
        percent = total_completed / overall_target
        # Ensure percentage doesn't exceed 1.0 for progress bar visualization
        st.progress(min(percent, 1.0), text=f"Overall Progress: {total_completed}/{overall_target} activities ({percent:.1%})")
    else:
        st.warning("Set an 'overall_target' variable (e.g., `overall_target = 100`) to see the combined progress bar.")
else:
    st.info("No survey or training data available to generate combined progress. Please submit some entries in the respective modules to see the dashboard come alive!")
