import streamlit as st

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

if st.button("Submit"):
    st.success("Form Submitted Successfully!")
