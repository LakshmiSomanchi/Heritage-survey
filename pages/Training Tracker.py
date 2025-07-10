import streamlit as st

st.title("Farmer Training Tracker")

# 🗓️ Basic Details
date = st.text_input("Date")
hpc_code = st.text_input("HPC Code")
hpc_name = st.text_input("HPC Name")

# 👨‍🏫 Training Details
trainer = st.selectbox("Farmer training conducted by", ["Guru", "Balaji"])
topics = st.selectbox(
    "Training Topics",
    ["Balanced Nutrition", "Fodder Enrichment", "EVM for Mastitis, Diarrhea, Repeat breeding"]
)

# 🥛 Dairy Metrics
volume = st.text_input("Volume (LPD)")
avg_fat = st.text_input("Average Fat (%)")
avg_snf = st.text_input("Average SNF (%)")

pourers_total = st.text_input("Number of Pourers at the HPC")
pourers_attended = st.text_input("Number of Pourers Attended Training")

heritage_users = st.text_input("Heritage Feed Using Farmers")
non_heritage_users = st.text_input("Non-Heritage Feed Using Farmers")

# 📣 Awareness Metrics
st.subheader("Farmer Awareness on HPC Benefits")
awareness_feed = st.text_input("Feed Awareness (Yes/No)")
awareness_supplements = st.text_input("Supplements Awareness (Yes/No)")
awareness_vet = st.text_input("Veterinary Services Awareness (Yes/No)")
awareness_ai = st.text_input("AI Services Awareness (Yes/No)")
awareness_loans = st.text_input("Loan Awareness (Yes/No)")
awareness_insurance = st.text_input("Cattle Insurance Awareness (Yes/No)")
awareness_gpa = st.text_input("GPA Policy Awareness (Yes/No)")

# 📝 Final Notes
key_insights = st.text_area("Key Insights")

if st.button("Submit"):
    st.success("Training Tracker Submitted Successfully!")
