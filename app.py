# app.py (Final Streamlit Dairy Survey)

import streamlit as st
import pandas as pd
import datetime
import os

# Ensure save folder exists
SAVE_DIR = 'survey_responses'
os.makedirs(SAVE_DIR, exist_ok=True)

# Updated Constants
VLCC_OPTIONS = ["VLCC 1", "VLCC 2", "VLCC 3"]
GREEN_FODDER_TYPES = ["Napier", "Maize", "Sorghum"]
DRY_FODDER_TYPES = ["Paddy Straw", "Maize Straw", "Ragi Straw", "Ground Nut Crop Residues"]
PELLET_FEED_BRANDS = [
    "Heritage Milk Rich", "Heritage Milk Joy", "Heritage Power Plus",
    "Kamadhenu", "Godrej", "Sreeja", "Vallabha-Panchamruth", "Vallabha-Subham Pusti"
]
MINERAL_MIXTURES = ["Herita Vit", "Herita Min", "Others"]
WATER_SOURCES = ["Panchayat", "Borewell", "Water Streams"]
SURVEYOR_NAMES = [
    "Shiva Shankaraiah", "Reddisekhar", "Balakrishna",
    "Somasekhar", "Mahesh Kumar", "Dr Swaran Raj Nayak",
    "Ram Prasad", "K Balaji"
]

# Multilingual Translations Placeholder
from translations_full import dict_translations

# Streamlit App Setup
st.set_page_config(page_title="Dairy Survey", page_icon="🐄", layout="centered")
lang = st.selectbox("Language / भाषा / భాష / भाषा / ಭాಷೆ / ভাষা / ભાષા", tuple(dict_translations.keys()))
labels = dict_translations.get(lang, dict_translations['English'])

st.title(labels['Farmer Profile'])

with st.form("survey_form"):
    st.header(labels['Farmer Profile'])
    vlcc = st.selectbox(labels['VLCC'], VLCC_OPTIONS)
    hpc_name = st.text_input(labels['HPC/MCC Name'])
    hpc_code = st.text_input(labels['HPC/MCC Code'])
    types = st.selectbox(labels['Types'], (labels['HPC'], labels['MCC']))
    farmer_name = st.text_input(labels['Farmer Name'])
    farmer_code = st.text_input(labels['Farmer Code'])
    gender = st.selectbox(labels['Gender'], (labels['Male'], labels['Female']))

    st.header(labels['Farm Details'])
    cows = st.number_input(labels['Number of Cows'], min_value=0)
    cattle_in_milk = st.number_input(labels['No. of Cattle in Milk'], min_value=0)
    calves = st.number_input(labels['No. of Calves/Heifers'], min_value=0)
    desi_cows = st.number_input(labels['No. of Desi cows'], min_value=0)
    crossbreed_cows = st.number_input(labels['No. of Cross breed cows'], min_value=0)
    buffalo = st.number_input(labels['No. of Buffalo'], min_value=0)
    milk_production = st.number_input(labels['Milk Production'], min_value=0.0)

    st.header(labels['Specific Questions'])
    green_fodder = st.selectbox(labels['Green Fodder'], (labels['Yes'], labels['No']))
    green_fodder_type = st.multiselect(labels['Type of Green Fodder'], GREEN_FODDER_TYPES)
    green_fodder_qty = st.number_input(labels['Quantity of Green Fodder'], min_value=0.0)

    dry_fodder = st.selectbox(labels['Dry Fodder'], (labels['Yes'], labels['No']))
    dry_fodder_type = st.multiselect(labels['Type of Dry Fodder'], DRY_FODDER_TYPES)
    dry_fodder_qty = st.number_input(labels['Quantity of Dry Fodder'], min_value=0.0)

    concentrate_feed = st.selectbox(labels['Concentrate Feed'], (labels['Yes'], labels['No']))
    concentrate_brand = st.multiselect(labels['Pellet Feed Brand'], PELLET_FEED_BRANDS)
    concentrate_qty = st.number_input(labels['Quantity of Concentrate Feed'], min_value=0.0)

    mineral_mixture = st.selectbox(labels['Mineral Mixture'], (labels['Yes'], labels['No']))
    mineral_brand = st.selectbox(labels['Mineral Mixture Brand'], MINERAL_MIXTURES)
    mineral_qty = st.number_input(labels['Quantity of Mineral Mixture'], min_value=0.0)

    silage = st.selectbox(labels['Silage'], (labels['Yes'], labels['No']))
    silage_source = st.text_input(labels['Source and Price of Silage'])
    silage_qty = st.number_input(labels['Quantity of Silage'], min_value=0.0)

    water_source = st.multiselect(labels['Source of Water'], WATER_SOURCES)
    surveyor_name = st.selectbox(labels['Name of Surveyor'], SURVEYOR_NAMES)
    visit_date = st.date_input(labels['Date of Visit'])

    submit = st.form_submit_button(labels['Submit'])

if submit:
    now = datetime.datetime.now()
    data = {
        'Timestamp': [now.isoformat()],
        'Language': [lang],
        'VLCC': [vlcc],
        'HPC/MCC Name': [hpc_name],
        'HPC/MCC Code': [hpc_code],
        'Types': [types],
        'Farmer Name': [farmer_name],
        'Farmer Code': [farmer_code],
        'Gender': [gender],
        'Number of Cows': [cows],
        'No. of Cattle in Milk': [cattle_in_milk],
        'No. of Calves/Heifers': [calves],
        'No. of Desi cows': [desi_cows],
        'No. of Cross breed cows': [crossbreed_cows],
        'No. of Buffalo': [buffalo],
        'Milk Production (liters/day)': [milk_production],
        'Green Fodder': [green_fodder],
        'Type of Green Fodder': ["; ".join(green_fodder_type)],
        'Quantity of Green Fodder (Kg/day)': [green_fodder_qty],
        'Dry Fodder': [dry_fodder],
        'Type of Dry Fodder': ["; ".join(dry_fodder_type)],
        'Quantity of Dry Fodder (Kg/day)': [dry_fodder_qty],
        'Pellet Feed': [concentrate_feed],
        'Pellet Feed Brand': ["; ".join(concentrate_brand)],
        'Quantity of Concentrate Feed (Kg/day)': [concentrate_qty],
        'Mineral Mixture': [mineral_mixture],
        'Mineral Mixture Brand': [mineral_brand],
        'Quantity of Mineral Mixture (gm/day)': [mineral_qty],
        'Silage': [silage],
        'Source and Price of Silage': [silage_source],
        'Quantity of Silage (Kg/day)': [silage_qty],
        'Source of Water': ["; ".join(water_source)],
        'Surveyor Name': [surveyor_name],
        'Date of Visit': [visit_date]
    }
    df = pd.DataFrame(data)
    filename = f"survey_{now.strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(os.path.join(SAVE_DIR, filename), index=False, encoding='utf-8')
    st.success("✅ Survey Submitted and Saved!")

st.divider()
st.header("🔐 Admin Real-Time Access")

ALLOWED_EMAILS = ["shifalis@tns.org", "rmukherjee@tns.org", "rsomanchi@tns.org", "mkaushal@tns.org"]
admin_email = st.text_input("Enter your Admin Email to unlock extra features:")

if admin_email in ALLOWED_EMAILS:
    st.success("✅ Admin access granted! Real-time view enabled.")
else:
    if admin_email:
        st.error("❌ Not an authorized admin.")

if st.checkbox("📄 View Past Submissions"):
    files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.csv')]
    if files:
        all_data = pd.concat([pd.read_csv(os.path.join(SAVE_DIR, f)) for f in files], ignore_index=True)
        st.dataframe(all_data)

        csv = all_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download All Responses",
            data=csv,
            file_name='all_survey_responses.csv',
            mime='text/csv',
            key='public_csv_download'
        )
    else:
        st.warning("⚠️ No submissions found yet.")
