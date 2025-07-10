import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64  # Import base64 for image handling
import shutil  # Import shutil for moving files
import zipfile # Import zipfile for creating zip archives
import io # Import io for in-memory file operations

# Ensure save folder exists
SAVE_DIR = 'survey_responses'
os.makedirs(SAVE_DIR, exist_ok=True)

# Define a directory for auto-saved drafts
DRAFT_DIR = os.path.join(SAVE_DIR, 'drafts')
os.makedirs(DRAFT_DIR, exist_ok=True)

# Define a temporary directory for uploaded images before final submission
TEMP_IMAGE_DIR = os.path.join(SAVE_DIR, 'temp_images')
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

# Define a directory for final submitted images
FINAL_IMAGE_DIR = os.path.join(SAVE_DIR, 'final_images')
os.makedirs(FINAL_IMAGE_DIR, exist_ok=True)

# Streamlit Page Config - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Heritage Dairy Survey", page_icon="🐄", layout="centered")

# Multilingual Translations (kept same)
dict_translations = {
    'English': {
        'Language': 'Language', 'Farmer Profile': 'Farmer Profile', 'VLCC Name': 'VLCC Name',
        'HPC/MCC Code': 'HPC/MCC Code', 'Types': 'Type', 'HPC': 'HPC', 'MCC': 'MCC',
        'Farmer Name': 'Farmer Name', 'Farmer Code': 'Farmer Code / Pourer ID', 'Gender': 'Gender',
        'Male': 'Male', 'Female': 'Female', 'Farm Details': 'Farm Details',
        'Number of Cows': 'Number of Cows', 'No. of Cattle in Milk': 'No. of Cattle in Milk',
        'No. of Calves/Heifers': 'No. of Calves/Heifers', 'No. of Desi cows': 'No. of Desi cows',
        'No. of Cross breed cows': 'No. of Cross breed cows', 'No. of Buffalo': 'No. of Buffalo',
        'Milk Production': 'Milk Production (liters/day)', 'Specific Questions': 'Specific Questions',
        'Green Fodder': 'Green Fodder', 'Type of Green Fodder': 'Type of Green Fodder (Multiple Select)',
        'Quantity of Green Fodder': 'Quantity of Green Fodder (Kg/day)',
        'Dry Fodder': 'Dry Fodder', 'Type of Dry Fodder': 'Type of Dry Fodder (Multiple Select)',
        'Quantity of Dry Fodder': 'Quantity of Dry Fodder (Kg/day)',
        'Pellet Feed': 'Pellet Feed', 'Pellet Feed Brand': 'Pellet Feed Brand (Multiple Select)',
        'Quantity of Pellet Feed': 'Quantity of Pellet Feed (Kg/day)',
        'Mineral Mixture': 'Mineral Mixture',
        'Mineral Mixture Brand': 'Mineral Mixture Brand',
        'Quantity of Mineral Mixture': 'Quantity of Mineral Mixture (gm/day)',
        'Silage': 'Silage', 'Source and Price of Silage': 'Source and Price of Silage',
        'Quantity of Silage': 'Quantity of Silage (Kg/day)', 'Source of Water': 'Source of Water (Multiple Select)',
        'Name': 'Name', 'Date of Visit': 'Date of Visit',
        'Submit': 'Submit', 'Yes': 'Yes', 'No': 'No', 'Download CSV': 'Download CSV',
        'Auto-saved!': 'Auto-saved! You can resume filling the form even if you refresh or lose internet temporarily.',
        'Others': 'Others',
        'Specify Farmer Name': 'Specify Farmer Name (if Others selected)',
        'Upload Photos': 'Upload Photos (Max 3)',
        'Photo uploaded successfully!': 'Photo uploaded successfully!',
        'No photo uploaded.': 'No photo uploaded.',
        'Error uploading photo:': 'Error uploading photo:',
        'Please upload up to 3 photos.': 'Please upload up to 3 photos.',
        'Review and Confirm': 'Review and Confirm',
        'Confirm and Submit': 'Confirm and Submit',
        'Edit Form': 'Edit Form',
        'Successfully Submitted!': 'Form Successfully Submitted!',
        'Review Your Submission': 'Review Your Submission',
        'Fill Another Form': 'Fill Another Form',
        'Download All Responses (CSV)': 'Download All Responses (CSV)',
        'Download All Responses (Excel)': 'Download All Responses (Excel)',
        'Download All Photos (ZIP)': 'Download All Photos (ZIP)'
    },
    'Hindi': {
        'Language': 'भाषा', 'Farmer Profile': 'किसान प्रोफ़ाइल', 'VLCC Name': 'वीएलसीसी नाम',
        'HPC/MCC Code': 'एचपीसी/एमसीसी कोड', 'Types': 'प्रकार', 'HPC': 'एचपीसी', 'MCC': 'एमसीसी',
        'Farmer Name': 'किसान का नाम', 'Farmer Code': 'किसान कोड/दूधदाता आईडी', 'Gender': 'लिंग',
        'Male': 'पुरुष', 'Female': 'महिला', 'Farm Details': 'फार्म विवरण',
        'Number of Cows': 'गायों की संख्या', 'No. of Cattle in Milk': 'दूध देने वाले मवेशी',
        'No. of Calves/Heifers': 'बछड़े/बछड़ियां', 'No. of Desi cows': 'देसी गायों की संख्या',
        'No. of Cross breed cows': 'क्रॉसब्रीड गायों की संख्या', 'No. of Buffalo': 'भैंसों की संख्या',
        'Milk Production': 'दूध उत्पादन (लीटर/दिन)', 'Specific Questions': 'विशिष्ट प्रश्न',
        'Green Fodder': 'हरा चारा', 'Type of Green Fodder': 'हरे चारे का प्रकार (एकाधिक चयन)',
        'Quantity of Green Fodder': 'हरे चारे की मात्रा (किलो/दिन)',
        'Dry Fodder': 'सूखा चारा', 'Type of Dry Fodder': 'सूखे चारे का प्रकार (एकाधिक चयन)',
        'Quantity of Dry Fodder': 'सूखे चारे की मात्रा (किलो/दिन)',
        'Pellet Feed': 'पेलेट फ़ीड', 'Pellet Feed Brand': 'पेलेट फ़ीड ब्रांड (एकाधिक चयन)',
        'Quantity of Pellet Feed': 'पेलेट फ़ीड मात्रा (किलो/दिन)',
        'Mineral Mixture': 'खनिज मिश्रण',
        'Mineral Mixture Brand': 'खनिज मिश्रण ब्रांड',
        'Quantity of Mineral Mixture': 'खनिज मिश्रण मात्रा (ग्राम/दिन)',
        'Silage': 'सायलेज', 'Source and Price of Silage': 'सायलेज स्रोत और मूल्य',
        'Quantity of Silage': 'सायलेज मात्रा (किलो/दिन)', 'Source of Water': 'पानी का स्रोत (एकाधिक चयन)',
        'Name': 'सर्वेक्षक का नाम', 'Date of Visit': 'दौरे की तिथि',
        'Submit': 'जमा करें', 'Yes': 'हाँ', 'No': 'नहीं', 'Download CSV': 'CSV डाउनलोड करें',
        'Auto-saved!': 'स्वतः सहेजा गया! आप फ़ॉर्म भरना जारी रख सकते हैं, भले ही आप ताज़ा करें या अस्थायी रूप से इंटरनेट खो दें!',
        'Others': 'अन्य',
        'Specify Farmer Name': 'किसान का नाम निर्दिष्ट करें (यदि अन्य चुना गया हो)',
        'Upload Photos': 'फ़ोटो अपलोड करें (अधिकतम 3)',
        'Photo uploaded successfully!': 'फ़ोटो सफलतापूर्वक अपलोड हुई!',
        'No photo uploaded.': 'कोई फ़ोटो अपलोड नहीं हुई।',
        'Error uploading photo:': 'फ़ोटो अपलोड करने में त्रुटि:',
        'Please upload up to 3 photos.': 'कृपया अधिकतम 3 फ़ोटो अपलोड करें!',
        'Review and Confirm': 'समीक्षा करें और पुष्टि करें',
        'Confirm and Submit': 'पुष्टि करें और जमा करें',
        'Edit Form': 'फ़ॉर्म संपादित करें',
        'Successfully Submitted!': 'फॉर्म सफलतापूर्वक जमा किया गया!',
        'Review Your Submission': 'अपनी सबमिशन की समीक्षा करें',
        'Fill Another Form': 'एक और फॉर्म भरें',
        'Download All Responses (CSV)': 'सभी प्रतिक्रियाएँ डाउनलोड करें (CSV)',
        'Download All Responses (Excel)': 'सभी प्रतिक्रियाएँ डाउनलोड करें (Excel)',
        'Download All Photos (ZIP)': 'सभी फ़ोटो डाउनलोड करें (ZIP)'
    },
    'Marathi': {
        "Language": "भाषा",
        "Farmer Profile": "शेतकरी प्रोफाइल",
        "VLCC Name": "वीएलसीसी नाव",
        "HPC/MCC Code": "एचपीसी/एमसीसी कोड",
        "Types": "प्रकार",
        "HPC": "एचपीसी",
        "MCC": "एमसीसी",
        "Farmer Name": "शेतकऱ्याचे नाव",
        "Farmer Code": "शेतकरी कोड/दूध देणारा आयडी",
        "Gender": "लिंग",
        "Male": "पुरुष",
        "Female": "महिला",
        "Farm Details": "फार्म तपशील",
        "Number of Cows": "गायींची संख्या",
        "No. of Cattle in Milk": "दूध देणाऱ्या जनावरांची संख्या",
        "No. of Calves/Heifers": "वासरे/वषाडांची संख्या",
        "No. of Desi cows": "देशी गायींची संख्या",
        "No. of Cross breed cows": "संकरित गायींची संख्या",
        "No. of Buffalo": "म्हशींची संख्या",
        "Milk Production": "दूध उत्पादन (लिटर/दिवस)",
        "Specific Questions": "विशिष्ट प्रश्न",
        "Green Fodder": "हिरवा चारा",
        "Type of Green Fodder": "हिरव्या चाऱ्याचा प्रकार (अनेक निवडा)",
        "Quantity of Green Fodder": "हिरव्या चाऱ्याचे प्रमाण (किलो/दिवस)",
        "Dry Fodder": "कोरडा चारा",
        "Type of Dry Fodder": "कोरड्या चाऱ्याचा प्रकार (अनेक निवडा)",
        "Quantity of Dry Fodder": "कोरड्या चाऱ्याचे प्रमाण (किलो/दिवस)",
        "Pellet Feed": "गोळी खाद्य",
        "Pellet Feed Brand": "गोळी खाद्य ब्रँड (अनेक निवडा)",
        "Quantity of Pellet Feed": "गोळी खाद्यचे प्रमाण (किलो/दिवस)",
        "Mineral Mixture": "खनिज मिश्रण",
        "Mineral Mixture Brand": "खनिज मिश्रण ब्रँड",
        "Quantity of Mineral Mixture": "खनिज मिश्रणाचे प्रमाण (ग्राम/दिवस)",
        "Silage": "सायलेज",
        "Source and Price of Silage": "सायलेजचा स्त्रोत आणि किंमत",
        "Quantity of Silage": "सायलेजचे प्रमाण (किलो/दिवस)",
        "Source of Water": "पाण्याचा स्त्रोत (अनेक निवडा)",
        "Name": "सर्वेक्षकाचे नाव",
        "Date of Visit": "भेटीची तारीख",
        "Submit": "सादर करा",
        "Yes": "होय",
        "No": "नाही",
        "Download CSV": "CSV डाउनलोड करा",
        "Auto-saved!": "स्वयं-जतन केले! आपण रिफ्रेश केले किंवा तात्पुरते इंटरनेट गमावले तरीही आपण फॉर्म भरणे सुरू ठेवू शकता.",
        'Others': 'इतर',
        'Specify Farmer Name': 'शेतकऱ्याचे नाव नमूद करा (इतर निवडल्यास)',
        'Upload Photos': 'फोटो अपलोड करा (जास्तीत जास्त 3)',
        'Photo uploaded successfully!': 'फोटो यशस्वीरित्या अपलोड झाला!',
        'No photo uploaded.': 'कोणताही फोटो अपलोड केला नाही.',
        'Error uploading photo:': 'फोटो अपलोड करताना त्रुटी:',
        'Please upload up to 3 photos.': 'कृपया 3 पर्यंत फोटो अपलोड करा!',
        'Review and Confirm': 'पुनरावलोकन करा आणि पुष्टी करा',
        'Confirm and Submit': 'पुष्टी करा आणि सबमिट करा',
        'Edit Form': 'फॉर्म संपादित करा',
        'Successfully Submitted!': 'फॉर्म यशस्वीरित्या सबमिट केला!',
        'Review Your Submission': 'आपल्या सबमिशनचे पुनरावलोकन करा',
        'Fill Another Form': 'दुसरा फॉर्म भरें',
        'Download All Responses (CSV)': 'सर्व प्रतिसाद डाउनलोड करा (CSV)',
        'Download All Responses (Excel)': 'सर्व प्रतिसाद डाउनलोड करा (Excel)',
        'Download All Photos (ZIP)': 'सर्व फोटो डाउनलोड करा (ZIP)'
    },
    'Telugu': {
        'Language': 'భాష',
        'Farmer Profile': 'రైతు ప్రొఫైల్',
        'VLCC Name': 'VLCC పేరు',
        'HPC/MCC Code': 'HPC/MCC కోడ్',
        'Types': 'రకం',
        'HPC': 'HPC',
        'MCC': 'MCC',
        'Farmer Name': 'రైతు పేరు',
        'Farmer Code': 'రైతు కోడ్ / పోరర్ ఐడి',
        'Gender': 'లింగం',
        'Male': 'పురుషుడు',
        'Female': 'స్త్రీ',
        'Farm Details': 'ఫారం వివరాలు',
        'Number of Cows': 'ఆవుల సంఖ్య',
        'No. of Cattle in Milk': 'పాలు ఇచ్చే పశువుల సంఖ్య',
        'No. of Calves/Heifers': 'దూడలు/పెయ్యల సంఖ్య',
        'No. of Desi cows': 'దేశీ ఆవుల సంఖ్య',
        'No. of Cross breed cows': 'క్రాస్‌బ్రీడ్ ఆవుల సంఖ్య',
        'No. of Buffalo': 'గేదెల సంఖ్య',
        'Milk Production': 'పాల ఉత్పత్తి (లీటర్లు/రోజు)',
        'Specific Questions': 'నిర్దిష్ట ప్రశ్నలు',
        'Green Fodder': 'పచ్చి మేత',
        'Type of Green Fodder': 'పచ్చి మేత రకం (బహుళ ఎంపిక)',
        'Quantity of Green Fodder': 'పచ్చి మేత పరిమాణం (కిలోలు/రోజు)',
        'Dry Fodder': 'ఎండు మేత',
        'Type of Dry Fodder': 'ఎండు మేత రకం (బహుళ ఎంపిక)',
        'Quantity of Dry Fodder': 'ఎండు మేత పరిమాణం (కిలోలు/రోజు)',
        'Pellet Feed': 'పెల్లెట్ ఫీడ్',
        'Pellet Feed Brand': 'పెల్లెట్ ఫీడ్ బ్రాండ్ (బహుళ ఎంపిక)',
        'Quantity of Pellet Feed': 'పెల్లెట్ ఫీడ్ పరిమాణం (కిలోలు/రోజు)',
        'Mineral Mixture': 'మినరల్ మిశ్రమం',
        'Mineral Mixture Brand': 'మినరల్ మిశ్రమం బ్రాండ్',
        'Quantity of Mineral Mixture': 'మినరల్ మిశ్రమం పరిమాణం (గ్రాములు/రోజు)',
        'Silage': 'సైలేజ్',
        'Source and Price of Silage': 'సైలేజ్ మూలం మరియు ధర',
        'Quantity of Silage': 'సైలేజ్ పరిమాణం (కిలోలు/రోజు)',
        'Source of Water': 'నీటి మూలం (బహుళ ఎంపిక)',
        'Name': 'సర్వేయర్ పేరు',
        'Date of Visit': 'సందర్శన తేదీ',
        'Submit': 'సమర్పించు',
        'Yes': 'అవును',
        'No': 'కాదు',
        'Download CSV': 'CSV డౌన్‌లోడ్ చేయండి',
        'Auto-saved!': 'ఆటో-సేవ్ చేయబడింది! మీరు రీఫ్రెష్ చేసినా లేదా తాత్కాలికంగా ఇంటర్నెట్ కోల్పోయినా ఫారమ్‌ను పూరించడం కొనసాగించవచ్చు.',
        'Others': 'ఇతరులు',
        'Specify Farmer Name': 'రైతు పేరును పేర్కొనండి (ఇతరులు ఎంచుకుంటే)',
        'Upload Photos': 'ఫోటోలను అప్‌లోడ్ చేయండి (గరిష్టంగా 3)',
        'Photo uploaded successfully!': 'ఫోటో విజయవంతంగా అప్‌లోడ్ చేయబడింది!',
        'No photo uploaded.': 'ఏ ఫోటో అప్‌లోడ్ చేయబడలేదు.',
        'Error uploading photo:': 'ఫోటో అప్‌లోడ్ చేయడంలో లోపం:',
        'Please upload up to 3 photos.': 'దయచేసి గరిష్టంగా 3 ఫోటోలను అప్‌లోడ్ చేయండి.',
        'Review and Confirm': 'సమీక్షించి నిర్ధారించండి',
        'Confirm and Submit': 'నిర్ధారించి సమర్పించు',
        'Edit Form': 'ఫారమ్‌ను సవరించండి',
        'Successfully Submitted!': 'ఫారమ్ విజయవంతంగా సమర్పించబడింది!',
        'Review Your Submission': 'మీ సమర్పణను సమీక్షించండి',
        'Fill Another Form': 'మరొక ఫారమ్ పూరించండి',
        'Download All Responses (CSV)': 'అన్ని ప్రతిస్పందనలను డౌన్‌లోడ్ చేయండి (CSV)',
        'Download All Responses (Excel)': 'అన్ని ప్రతిస్పందనలను డౌన్‌లోడ్ చేయండి (Excel)',
        'Download All Photos (ZIP)': 'అన్ని ఫోటోలను డౌన్‌లోడ్ చేయండి (ZIP)'
    }
}


# Load the raw data into a DataFrame
df_farmer_data = pd.read_csv(io.StringIO(farmer_data_raw_csv), sep='\t')

# Clean up column names by stripping whitespace
df_farmer_data.columns = df_farmer_data.columns.str.strip()

# Create a master lookup dictionary for farmer details based on Member Code
FARMER_LOOKUP = {}
for index, row in df_farmer_data.iterrows():
    farmer_code = str(row['Member Code']).strip()
    FARMER_LOOKUP[farmer_code] = {
        'HPC Name': row['HPC Name'].strip(),
        'Farmer Name': row['Farmer Name'].strip(),
        'Rep ID': str(row['Rep ID']).strip(), # Phone number
        'HPC Code': str(row['HPC Code']).strip()
    }

# Create initial lists for ALL VLCC Names, Farmer Codes, and Farmer Names
VLCC_NAMES = sorted(df_farmer_data['HPC Name'].unique().tolist())
FARMER_CODES_ALL = sorted(list(FARMER_LOOKUP.keys()))
FARMER_NAMES_ALL = sorted(list(set(data['Farmer Name'] for data in FARMER_LOOKUP.values()))) # Unique farmer names

GREEN_FODDER_OPTIONS = ["Napier", "Maize", "Sorghum"]
DRY_FODDER_OPTIONS = ["Paddy Straw", "Maize Straw", "Ragi Straw", "Ground Nut Crop Residues"]
PELLET_FEED_BRANDS = ["Heritage Milk Rich", "Heritage Milk Joy", "Heritage Power Plus", "Kamadhenu", "Godrej", "Sreeja", "Vallabha-Panchamruth", "Vallabha-Subham Pusti"]
MINERAL_MIXTURE_BRANDS = ["Herita Vit", "Herita Min", "Other (Specify)"]
WATER_SOURCE_OPTIONS = ["Panchayat", "Borewell", "Water Streams"]
SURVEYOR_NAMES = ["Shiva Shankaraiah", "Reddisekhar", "Balakrishna", "Somasekhar", "Mahesh Kumar", "Dr Swaran Raj Nayak", "Ram Prasad", "K Balaji"]

# Define initial_values_defaults at the global scope, using logical keys
initial_values_defaults = {
    'lang_select': "English",
    'vlcc_name': VLCC_NAMES[0] if VLCC_NAMES else None,
    'hpc_code': '',
    'types': "HPC",
    'farmer_name_selected': 'Others',
    'farmer_name_other': '',
    'farmer_code': None,
    'rep_id': '',
    'gender': "Male",
    'cows': 0,
    'cattle_in_milk': 0,
    'calves': 0,
    'desi_cows': 0,
    'crossbreed_cows': 0,
    'buffalo': 0,
    'milk_production': 0.0,
    'green_fodder': "Yes",
    'green_fodder_types': [],
    'green_fodder_qty': 0.0,
    'dry_fodder': "Yes",
    'dry_fodder_types': [],
    'dry_fodder_qty': 0.0,
    'pellet_feed': "Yes",
    'pellet_feed_brands': [],
    'pellet_feed_qty': 0.0,
    'mineral_mixture': "Yes",
    'mineral_brand': MINERAL_MIXTURE_BRANDS[0] if MINERAL_MIXTURE_BRANDS else None,
    'mineral_qty': 0.0,
    'silage': "Yes",
    'silage_source': '',
    'silage_qty': 0.0,
    'water_sources': [],
    'surveyor_name': SURVEYOR_NAMES[0] if SURVEYOR_NAMES else None,
    'visit_date': datetime.date.today(),
    'uploaded_temp_photo_paths': [],
    'final_submitted_data': None,
    'current_step': 'form_entry',
}

# Helper functions for dynamic options
def get_filtered_farmer_names(selected_vlcc):
    if selected_vlcc and selected_vlcc in VLCC_NAMES:
        filtered_df = df_farmer_data[df_farmer_data['HPC Name'] == selected_vlcc]
        return sorted(filtered_df['Farmer Name'].unique().tolist())
    return []

def get_filtered_farmer_codes(selected_vlcc):
    if selected_vlcc and selected_vlcc in VLCC_NAMES:
        filtered_df = df_farmer_data[df_farmer_data['HPC Name'] == selected_vlcc]
        return sorted(filtered_df['Member Code'].astype(str).unique().tolist())
    return []

# Function to save current form data to a draft file
def save_draft():
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    draft_data = {}
    
    # Map original_key to the session state key used for the widget
    key_mapping = {
        'vlcc_name': 'vlcc_name_select',
        'farmer_name_selected': 'farmer_name_selected_select',
        'farmer_name_other': 'farmer_name_other_input',
        'farmer_code': 'farmer_code_select',
        'hpc_code': 'hpc_code_display',
        'rep_id': 'rep_id_display',
        'types': 'types_selectbox',
        'gender': 'gender_selectbox',
        'green_fodder': 'green_fodder_radio',
        'dry_fodder': 'dry_fodder_radio',
        'pellet_feed': 'pellet_feed_radio',
        'mineral_mixture': 'mineral_mixture_radio',
        'silage': 'silage_radio',
        'mineral_brand': 'mineral_brand_select',
        'surveyor_name': 'surveyor_name_select',
        'visit_date': 'visit_date_input',
        'uploaded_temp_photo_paths': 'uploaded_temp_photo_paths',
        'lang_select': 'lang_select',
        'current_step': 'current_step',
        # Other form fields
        'cows': 'cows_input',
        'cattle_in_milk': 'cattle_in_milk_input',
        'calves': 'calves_input',
        'desi_cows': 'desi_cows_input',
        'crossbreed_cows': 'crossbreed_cows_input',
        'buffalo': 'buffalo_input',
        'milk_production': 'milk_production_input',
        'green_fodder_types': 'green_fodder_types_multi',
        'green_fodder_qty': 'green_fodder_qty_input',
        'dry_fodder_types': 'dry_fodder_types_multi',
        'dry_fodder_qty': 'dry_fodder_qty_input',
        'pellet_feed_brands': 'pellet_feed_brands_multi',
        'pellet_feed_qty': 'pellet_feed_qty_input',
        'mineral_qty': 'mineral_qty_input',
        'silage_source': 'silage_source_input',
        'silage_qty': 'silage_qty_input',
        'water_sources': 'water_sources_multi',
        'final_submitted_data': 'final_submitted_data',
    }

    # Iterate through initial_values_defaults to ensure all expected fields are saved
    for original_key, default_value in initial_values_defaults.items():
        session_key = key_mapping.get(original_key, original_key) # Use direct key if not in map

        value_to_save = st.session_state.get(session_key, default_value)

        # Special handling for datetime.date
        if original_key == 'visit_date' and isinstance(value_to_save, datetime.date):
            value_to_save = value_to_save.isoformat()
        
        # Ensure list types are saved as lists
        if original_key in ['green_fodder_types', 'dry_fodder_types', 'pellet_feed_brands', 'water_sources', 'uploaded_temp_photo_paths']:
            if not isinstance(value_to_save, list):
                value_to_save = [] # Default to empty list if not a list
            
        draft_data[original_key] = value_to_save
    
    try:
        with open(draft_filename, 'w') as f:
            json.dump(draft_data, f, indent=4)
        st.session_state.last_saved_time_persistent = datetime.datetime.now().strftime("%H:%M:%S")
    except Exception as e:
        st.error(f"Error saving draft: {e}")

# Function to load draft data into session state
def load_draft():
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    if os.path.exists(draft_filename):
        try:
            with open(draft_filename, 'r') as f:
                loaded_data = json.load(f)

            # Map loaded data keys to session state widget keys
            key_mapping = {
                'vlcc_name': 'vlcc_name_select',
                'farmer_name_selected': 'farmer_name_selected_select',
                'farmer_name_other': 'farmer_name_other_input',
                'farmer_code': 'farmer_code_select',
                'hpc_code': 'hpc_code_display',
                'rep_id': 'rep_id_display',
                'types': 'types_selectbox',
                'gender': 'gender_selectbox',
                'green_fodder': 'green_fodder_radio',
                'dry_fodder': 'dry_fodder_radio',
                'pellet_feed': 'pellet_feed_radio',
                'mineral_mixture': 'mineral_mixture_radio',
                'silage': 'silage_radio',
                'mineral_brand': 'mineral_brand_select',
                'surveyor_name': 'surveyor_name_select',
                'visit_date': 'visit_date_input',
                'uploaded_temp_photo_paths': 'uploaded_temp_photo_paths', # This one maps directly
                'lang_select': 'lang_select', # This one maps directly
                'current_step': 'current_step', # This one maps directly
                # Other form fields that are directly mapped or managed by the form
                'cows': 'cows_input',
                'cattle_in_milk': 'cattle_in_milk_input',
                'calves': 'calves_input',
                'desi_cows': 'desi_cows_input',
                'crossbreed_cows': 'crossbreed_cows_input',
                'buffalo': 'buffalo_input',
                'milk_production': 'milk_production_input',
                'green_fodder_types': 'green_fodder_types_multi',
                'green_fodder_qty': 'green_fodder_qty_input',
                'dry_fodder_types': 'dry_fodder_types_multi',
                'dry_fodder_qty': 'dry_fodder_qty_input',
                'pellet_feed_brands': 'pellet_feed_brands_multi',
                'pellet_feed_qty': 'pellet_feed_qty_input',
                'mineral_qty': 'mineral_qty_input',
                'silage_source': 'silage_source_input',
                'silage_qty': 'silage_qty_input',
                'water_sources': 'water_sources_multi',
                'final_submitted_data': 'final_submitted_data', # For review step
            }

            for original_key, session_key in key_mapping.items():
                if original_key in loaded_data:
                    value = loaded_data[original_key]
                    if original_key == 'visit_date' and isinstance(value, str):
                        try:
                            st.session_state[session_key] = datetime.date.fromisoformat(value)
                        except ValueError:
                            st.session_state[session_key] = initial_values_defaults.get(original_key, datetime.date.today())
                    elif original_key in ['green_fodder_types', 'dry_fodder_types', 'pellet_feed_brands', 'water_sources', 'uploaded_temp_photo_paths'] and isinstance(value, list):
                        st.session_state[session_key] = list(value)
                    else:
                        st.session_state[session_key] = value
                # Ensure keys not in loaded_data are initialized to defaults for consistency
                elif session_key not in st.session_state:
                    st.session_state[session_key] = initial_values_defaults.get(original_key)

            # --- VALIDATE DROPDOWN SELECTIONS AFTER LOADING DRAFT ---
            temp_lang = st.session_state.get('lang_select', 'English') # Use session state for lang
            current_labels = dict_translations.get(temp_lang, dict_translations['English'])

            # VLCC Name
            if 'vlcc_name_select' in st.session_state and st.session_state['vlcc_name_select'] not in VLCC_NAMES:
                st.session_state['vlcc_name_select'] = VLCC_NAMES[0] if VLCC_NAMES else None
            
            # Farmer Name (validation against currently filtered names based on VLCC)
            current_vlcc_for_validation = st.session_state.get('vlcc_name_select')
            valid_farmer_names_for_vlcc = get_filtered_farmer_names(current_vlcc_for_validation) + [current_labels['Others']]

            if 'farmer_name_selected_select' in st.session_state and st.session_state['farmer_name_selected_select'] not in valid_farmer_names_for_vlcc:
                st.session_state['farmer_name_selected_select'] = current_labels['Others']
                st.session_state['farmer_name_other_input'] = '' # Clear other name if invalid

            # Farmer Code (validation against currently filtered codes based on VLCC)
            valid_farmer_codes_for_vlcc = get_filtered_farmer_codes(current_vlcc_for_validation)
            if 'farmer_code_select' in st.session_state and st.session_state['farmer_code_select'] not in valid_farmer_codes_for_vlcc:
                st.session_state['farmer_code_select'] = None
                st.session_state['hpc_code_display'] = ''
                st.session_state['rep_id_display'] = ''
                # Ensure farmer_name_selected_select is consistent if code becomes None
                if st.session_state.farmer_name_selected_select != current_labels['Others']:
                    st.session_state.farmer_name_selected_select = current_labels['Others']
                    st.session_state.farmer_name_other_input = ''


            # Types and Gender
            if 'types_selectbox' in st.session_state and st.session_state['types_selectbox'] not in (current_labels['HPC'], current_labels['MCC']):
                st.session_state['types_selectbox'] = current_labels['HPC']
            if 'gender_selectbox' in st.session_state and st.session_state['gender_selectbox'] not in (current_labels['Male'], current_labels['Female']):
                st.session_state['gender_selectbox'] = current_labels['Male']
            
            # Yes/No options (using new keys)
            if 'green_fodder_radio' in st.session_state and st.session_state['green_fodder_radio'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['green_fodder_radio'] = current_labels['Yes']
            if 'dry_fodder_radio' in st.session_state and st.session_state['dry_fodder_radio'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['dry_fodder_radio'] = current_labels['Yes']
            if 'pellet_feed_radio' in st.session_state and st.session_state['pellet_feed_radio'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['pellet_feed_radio'] = current_labels['Yes']
            if 'mineral_mixture_radio' in st.session_state and st.session_state['mineral_mixture_radio'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['mineral_mixture_radio'] = current_labels['Yes']
            if 'silage_radio' in st.session_state and st.session_state['silage_radio'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['silage_radio'] = current_labels['Yes']
            
            # Mineral Brand
            if 'mineral_brand_select' in st.session_state and st.session_state['mineral_brand_select'] not in MINERAL_MIXTURE_BRANDS:
                st.session_state['mineral_brand_select'] = MINERAL_MIXTURE_BRANDS[0] if MINERAL_MIXTURE_BRANDS else None
            
            # Surveyor Name
            if 'surveyor_name_select' in st.session_state and st.session_state['surveyor_name_select'] not in SURVEYOR_NAMES:
                st.session_state['surveyor_name_select'] = SURVEYOR_NAMES[0] if SURVEYOR_NAMES else None

            # Photo Paths
            if 'uploaded_temp_photo_paths' not in st.session_state or not isinstance(st.session_state.uploaded_temp_photo_paths, list):
                st.session_state.uploaded_temp_photo_paths = []

            st.toast("Draft loaded successfully!")
            return True
        except Exception as e:
            st.error(f"Error loading draft: {e}")
            return False
    return False


# Function to clear form fields (reset session state for form entry)
def clear_form_fields():
    persistent_keys = ['lang_select', 'app_initialized_flag', 'current_step'] # Keep these
    
    # Identify all keys that need to be cleared/reset
    all_current_session_keys = list(st.session_state.keys()) # Get a copy
    
    for key in all_current_session_keys:
        if key not in persistent_keys:
            if key in st.session_state: # Double-check existence before deleting
                del st.session_state[key]
    
    # Re-map initial_values_defaults to session state keys
    key_mapping = {
        'vlcc_name': 'vlcc_name_select',
        'farmer_name_selected': 'farmer_name_selected_select',
        'farmer_name_other': 'farmer_name_other_input',
        'farmer_code': 'farmer_code_select',
        'hpc_code': 'hpc_code_display',
        'rep_id': 'rep_id_display',
        'types': 'types_selectbox',
        'gender': 'gender_selectbox',
        'green_fodder': 'green_fodder_radio',
        'dry_fodder': 'dry_fodder_radio',
        'pellet_feed': 'pellet_feed_radio',
        'mineral_mixture': 'mineral_mixture_radio',
        'silage': 'silage_radio',
        'mineral_brand': 'mineral_brand_select',
        'surveyor_name': 'surveyor_name_select',
        'visit_date': 'visit_date_input',
        'uploaded_temp_photo_paths': 'uploaded_temp_photo_paths',
        # Other form fields
        'cows': 'cows_input',
        'cattle_in_milk': 'cattle_in_milk_input',
        'calves': 'calves_input',
        'desi_cows': 'desi_cows_input',
        'crossbreed_cows': 'crossbreed_cows_input',
        'buffalo': 'buffalo_input',
        'milk_production': 'milk_production_input',
        'green_fodder_types': 'green_fodder_types_multi',
        'green_fodder_qty': 'green_fodder_qty_input',
        'dry_fodder_types': 'dry_fodder_types_multi',
        'dry_fodder_qty': 'dry_fodder_qty_input',
        'pellet_feed_brands': 'pellet_feed_brands_multi',
        'pellet_feed_qty': 'pellet_feed_qty_input',
        'mineral_qty': 'mineral_qty_input',
        'silage_source': 'silage_source_input',
        'silage_qty': 'silage_qty_input',
        'water_sources': 'water_sources_multi',
        'final_submitted_data': 'final_submitted_data',
    }

    for original_key, default_value in initial_values_defaults.items():
        session_key = key_mapping.get(original_key, original_key)
        st.session_state[session_key] = default_value # Set to default

    # Re-apply the specific initial setup logic for farmer/VLCC
    if VLCC_NAMES:
        st.session_state.vlcc_name_select = VLCC_NAMES[0]
        filtered_farmers_for_init = get_filtered_farmer_names(st.session_state.vlcc_name_select)
        if filtered_farmers_for_init:
            initial_farmer_name = filtered_farmers_for_init[0]
            st.session_state.farmer_name_selected_select = initial_farmer_name
            initial_farmer_info = df_farmer_data[
                (df_farmer_data['Farmer Name'] == initial_farmer_name) &
                (df_farmer_data['HPC Name'] == st.session_state.vlcc_name_select)
            ]
            if not initial_farmer_info.empty:
                farmer_info_row = initial_farmer_info.iloc[0]
                st.session_state.farmer_code_select = str(farmer_info_row['Member Code']).strip()
                st.session_state.hpc_code_display = str(farmer_info_row['HPC Code']).strip()
                st.session_state.rep_id_display = str(farmer_info_row['Rep ID']).strip()
            else:
                st.session_state.farmer_name_selected_select = initial_values_defaults['farmer_name_selected'] # 'Others'
                st.session_state.farmer_code_select = None
        else:
            st.session_state.farmer_name_selected_select = initial_values_defaults['farmer_name_selected'] # 'Others'
            st.session_state.farmer_code_select = None
    else:
        st.session_state.vlcc_name_select = None
        st.session_state.farmer_name_selected_select = initial_values_defaults['farmer_name_selected']
        st.session_state.farmer_code_select = None

    st.session_state.current_step = 'form_entry'
    st.session_state.last_saved_time_persistent = None
    
    # Clear temporary image directory
    for f in os.listdir(TEMP_IMAGE_DIR):
        os.remove(os.path.join(TEMP_IMAGE_DIR, f))
    st.session_state.uploaded_temp_photo_paths = []

    # Remove draft file
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    if os.path.exists(draft_filename):
        os.remove(draft_filename)

    st.rerun()

# Function to create a ZIP file of all images (kept same)
def create_zip_file():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(FINAL_IMAGE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, FINAL_IMAGE_DIR))
    zip_buffer.seek(0)
    return zip_buffer

# Function to get all survey responses as a DataFrame (kept same)
def get_all_responses_df():
    all_files = [os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR) if f.endswith('.csv') and f.startswith('survey_response_')]
    
    if not all_files:
        return pd.DataFrame()

    df_list = []
    for file in all_files:
        try:
            df_list.append(pd.read_csv(file))
        except Exception as e:
            st.warning(f"Could not read {file}: {e}")
            continue
    
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    else:
        return pd.DataFrame()

# --- Callback functions for dynamic updates ---

# VLCC name change now updates other fields directly, no filtering of farmer lists based on VLCC.
def on_vlcc_change():
    selected_vlcc = st.session_state.vlcc_name_select # Use the key from the selectbox
    current_labels = dict_translations.get(st.session_state.lang_select, dict_translations['English'])

    # Get the filtered lists based on the new VLCC
    filtered_names = get_filtered_farmer_names(selected_vlcc)

    # Reset farmer name and code selections, then try to re-select a sensible default
    st.session_state.farmer_name_selected_select = current_labels['Others'] # Default to Others initially
    st.session_state.farmer_name_other_input = '' # Clear other name input
    st.session_state.farmer_code_select = None
    st.session_state.hpc_code_display = ''
    st.session_state.rep_id_display = ''

    # If the filtered list has farmers, pre-select the first one if not "Others"
    if filtered_names and current_labels['Others'] not in filtered_names:
        st.session_state.farmer_name_selected_select = filtered_names[0]
        # Auto-fill other fields based on this new default farmer
        on_farmer_name_change()

    save_draft()
    st.rerun() # Rerun to update the dropdown options

def on_farmer_name_change():
    selected_farmer_name = st.session_state.farmer_name_selected_select # Use the key
    current_labels = dict_translations.get(st.session_state.lang_select, dict_translations['English'])
    selected_vlcc = st.session_state.vlcc_name_select # Use the VLCC selected above

    if selected_farmer_name != current_labels['Others']:
        # Filter by both name AND selected VLCC for precision
        matching_farmers = df_farmer_data[
            (df_farmer_data['Farmer Name'] == selected_farmer_name) &
            (df_farmer_data['HPC Name'] == selected_vlcc) # Ensure consistency with VLCC
        ]

        if not matching_farmers.empty:
            farmer_info_row = matching_farmers.iloc[0]
            st.session_state.farmer_code_select = str(farmer_info_row['Member Code']).strip()
            st.session_state.hpc_code_display = str(farmer_info_row['HPC Code']).strip()
            st.session_state.rep_id_display = str(farmer_info_row['Rep ID']).strip()
            st.session_state.farmer_name_other_input = '' # Clear "other" if a known farmer is selected
        else:
            # If the selected farmer name is not found within the selected VLCC, revert to "Others"
            st.session_state.farmer_code_select = None
            st.session_state.hpc_code_display = ''
            st.session_state.rep_id_display = ''
            st.session_state.farmer_name_selected_select = current_labels['Others']
            st.session_state.farmer_name_other_input = ''
            st.warning(f"Selected farmer '{selected_farmer_name}' not found for VLCC '{selected_vlcc}'. Please select 'Others' or a valid farmer from the list.")
    else: # If "Others" is selected
        st.session_state.farmer_code_select = None
        st.session_state.hpc_code_display = ''
        st.session_state.rep_id_display = ''
        # farmer_name_other_input will be editable in the main UI section

    save_draft()
    # No rerun here, let the main UI flow handle it unless absolutely necessary.


def on_farmer_code_change():
    selected_farmer_code = st.session_state.farmer_code_select # Use the key
    current_labels = dict_translations.get(st.session_state.lang_select, dict_translations['English'])

    if selected_farmer_code in FARMER_LOOKUP:
        farmer_info = FARMER_LOOKUP[selected_farmer_code]
        st.session_state.hpc_code_display = farmer_info['HPC Code']
        st.session_state.rep_id_display = farmer_info['Rep ID']
        st.session_state.vlcc_name_select = farmer_info['HPC Name'] # Autofill VLCC too
        st.session_state.farmer_name_selected_select = farmer_info['Farmer Name']
        st.session_state.farmer_name_other_input = '' # Clear this if a specific code is chosen
    else:
        st.session_state.hpc_code_display = ''
        st.session_state.rep_id_display = ''
        st.session_state.vlcc_name_select = VLCC_NAMES[0] if VLCC_NAMES else None # Reset VLCC if not found
        st.session_state.farmer_name_selected_select = current_labels['Others']
        st.session_state.farmer_name_other_input = ''

    save_draft()
    # No rerun here, let the main UI flow handle it.

# Initialize session state (adjusted for ALL farmer data and new keys)
if 'app_initialized_flag' not in st.session_state:
    st.session_state.app_initialized_flag = True
    st.session_state.last_saved_time_persistent = None

    # Initialize all defaults first, using unique keys for widgets
    # This loop ensures all keys from initial_values_defaults exist in session_state,
    # mapping to their widget-specific keys.
    key_mapping_init = {
        'vlcc_name': 'vlcc_name_select',
        'farmer_name_selected': 'farmer_name_selected_select',
        'farmer_name_other': 'farmer_name_other_input',
        'farmer_code': 'farmer_code_select',
        'hpc_code': 'hpc_code_display',
        'rep_id': 'rep_id_display',
        'types': 'types_selectbox',
        'gender': 'gender_selectbox',
        'green_fodder': 'green_fodder_radio',
        'dry_fodder': 'dry_fodder_radio',
        'pellet_feed': 'pellet_feed_radio',
        'mineral_mixture': 'mineral_mixture_radio',
        'silage': 'silage_radio',
        'mineral_brand': 'mineral_brand_select',
        'surveyor_name': 'surveyor_name_select',
        'visit_date': 'visit_date_input',
        'uploaded_temp_photo_paths': 'uploaded_temp_photo_paths',
        'lang_select': 'lang_select',
        'current_step': 'current_step',
        'cows': 'cows_input',
        'cattle_in_milk': 'cattle_in_milk_input',
        'calves': 'calves_input',
        'desi_cows': 'desi_cows_input',
        'crossbreed_cows': 'crossbreed_cows_input',
        'buffalo': 'buffalo_input',
        'milk_production': 'milk_production_input',
        'green_fodder_types': 'green_fodder_types_multi',
        'green_fodder_qty': 'green_fodder_qty_input',
        'dry_fodder_types': 'dry_fodder_types_multi',
        'dry_fodder_qty': 'dry_fodder_qty_input',
        'pellet_feed_brands': 'pellet_feed_brands_multi',
        'pellet_feed_qty': 'pellet_feed_qty_input',
        'mineral_qty': 'mineral_qty_input',
        'silage_source': 'silage_source_input',
        'silage_qty': 'silage_qty_input',
        'water_sources': 'water_sources_multi',
        'final_submitted_data': 'final_submitted_data',
    }

    for original_key, default_value in initial_values_defaults.items():
        session_key = key_mapping_init.get(original_key, original_key)
        if session_key not in st.session_state:
            st.session_state[session_key] = default_value

    # Initial setup for farmer code/name selection to ensure consistency
    if VLCC_NAMES:
        st.session_state.vlcc_name_select = VLCC_NAMES[0]
        # Filter farmers based on this default VLCC
        filtered_farmers_for_init = get_filtered_farmer_names(st.session_state.vlcc_name_select)
        if filtered_farmers_for_init:
            initial_farmer_name = filtered_farmers_for_init[0]
            st.session_state.farmer_name_selected_select = initial_farmer_name
            # Attempt to find the full info for this initial farmer
            initial_farmer_info = df_farmer_data[
                (df_farmer_data['Farmer Name'] == initial_farmer_name) &
                (df_farmer_data['HPC Name'] == st.session_state.vlcc_name_select)
            ]
            if not initial_farmer_info.empty:
                farmer_info_row = initial_farmer_info.iloc[0]
                st.session_state.farmer_code_select = str(farmer_info_row['Member Code']).strip()
                st.session_state.hpc_code_display = str(farmer_info_row['HPC Code']).strip()
                st.session_state.rep_id_display = str(farmer_info_row['Rep ID']).strip()
            else:
                st.session_state.farmer_name_selected_select = initial_values_defaults['farmer_name_selected'] # 'Others'
                st.session_state.farmer_code_select = None
        else:
            # If no farmers for initial VLCC, default to 'Others'
            st.session_state.farmer_name_selected_select = initial_values_defaults['farmer_name_selected'] # 'Others'
            st.session_state.farmer_code_select = None
    else:
        st.session_state.vlcc_name_select = None
        st.session_state.farmer_name_selected_select = initial_values_defaults['farmer_name_selected']
        st.session_state.farmer_code_select = None

    # Then try to load draft, which will overwrite these defaults if successful and valid
    load_draft()

# Language Selection (kept same)
initial_lang_options = ("English", "Hindi", "Marathi", "Telugu")
if 'lang_select' not in st.session_state or st.session_state.lang_select not in initial_lang_options:
    st.session_state.lang_select = "English"

initial_lang_index = initial_lang_options.index(st.session_state.lang_select)

lang = st.sidebar.selectbox(
    "Language / भाषा / भाषा / భాష",
    initial_lang_options,
    index=initial_lang_index,
    key="lang_select",
    on_change=save_draft
)
labels = dict_translations.get(lang, dict_translations['English'])

# Display auto-save status (kept same)
if st.session_state.last_saved_time_persistent and st.session_state.current_step == 'form_entry':
    st.info(f"{labels['Auto-saved!']} Last saved: {st.session_state.last_saved_time_persistent}")
else:
    if st.session_state.current_step == 'form_entry':
        st.info("No auto-saved draft found, or draft cleared. Start filling the form!")

# --- Main Application Logic based on current_step ---
if st.session_state.current_step == 'form_entry':
    st.title(labels['Farmer Profile'])

    # --- Farmer Profile Inputs (Moved OUTSIDE the form for dynamic updates) ---
    st.subheader("Farmer Identification")

    # VLCC Name selectbox
    current_vlcc_name = st.session_state.get('vlcc_name_select')
    vlcc_name_default_idx = 0
    if current_vlcc_name in VLCC_NAMES:
        vlcc_name_default_idx = VLCC_NAMES.index(current_vlcc_name)
    st.selectbox(
        labels['VLCC Name'], VLCC_NAMES,
        index=vlcc_name_default_idx,
        key="vlcc_name_select", # Unique key
        disabled=(not VLCC_NAMES),
        on_change=on_vlcc_change
    )

    # Dynamically filtered farmer names and codes
    current_selected_vlcc_for_filtering = st.session_state.get('vlcc_name_select')
    filtered_farmer_names_for_display = get_filtered_farmer_names(current_selected_vlcc_for_filtering)
    
    # Add "Others" to the filtered farmer names for display
    farmer_names_options_display = filtered_farmer_names_for_display + [labels['Others']]

    # Determine the default index for Farmer Name
    current_farmer_name_selected_display = st.session_state.get('farmer_name_selected_select', labels['Others'])
    farmer_name_default_idx = 0
    if current_farmer_name_selected_display in farmer_names_options_display:
        farmer_name_default_idx = farmer_names_options_display.index(current_farmer_name_selected_display)
    # Ensure the index is valid for the current options, otherwise default to "Others"
    elif labels['Others'] in farmer_names_options_display:
        farmer_name_default_idx = farmer_names_options_display.index(labels['Others'])
    else:
        farmer_name_default_idx = 0 # Fallback if no options or Others not present

    st.selectbox(
        labels['Farmer Name'], options=farmer_names_options_display,
        index=farmer_name_default_idx,
        key="farmer_name_selected_select", # Unique key
        disabled=(not farmer_names_options_display),
        on_change=on_farmer_name_change
    )

    if st.session_state.farmer_name_selected_select == labels['Others']:
        st.text_input(
            labels['Specify Farmer Name'],
            value=st.session_state.get('farmer_name_other_input', ''),
            key="farmer_name_other_input",
            on_change=save_draft # Add save_draft here
        )
    # No else: block to clear farmer_name_other_input here, on_farmer_name_change handles it

    # Farmer Code dropdown
    filtered_farmer_codes_for_display = get_filtered_farmer_codes(current_selected_vlcc_for_filtering)
    current_farmer_code_display = st.session_state.get('farmer_code_select')
    farmer_code_default_idx = 0
    if current_farmer_code_display in filtered_farmer_codes_for_display:
        farmer_code_default_idx = filtered_farmer_codes_for_display.index(current_farmer_code_display)
    elif filtered_farmer_codes_for_display:
        farmer_code_default_idx = 0 # Default to first if None and options exist
    else:
        farmer_code_default_idx = 0 # Fallback if no options

    st.selectbox(
        labels['Farmer Code'], options=filtered_farmer_codes_for_display,
        index=farmer_code_default_idx,
        key="farmer_code_select", # Unique key
        disabled=(not filtered_farmer_codes_for_display),
        on_change=on_farmer_code_change
    )
    
    # Autofilled/displayed fields (HPC Code and Rep ID) - values are directly from session state
    st.text_input(
        labels['HPC/MCC Code'],
        value=st.session_state.get('hpc_code_display', ''),
        key="hpc_code_display",
        disabled=True
    )
    st.text_input(
        "Rep ID (Phone Number)",
        value=st.session_state.get('rep_id_display', ''),
        key="rep_id_display",
        disabled=True
    )

    # Types and Gender are simple selectboxes, can be outside or inside,
    # but since Farmer Identification section is already outside, keep them here for consistency.
    types_options = (labels['HPC'], labels['MCC'])
    current_types = st.session_state.get('types_selectbox', types_options[0])
    types_default_idx = 0
    if current_types in types_options:
        types_default_idx = types_options.index(current_types)
    st.selectbox(
        labels['Types'], types_options,
        index=types_default_idx,
        key="types_selectbox", # Unique key
        on_change=save_draft # Add save_draft for these too
    )
    
    gender_options = (labels['Male'], labels['Female'])
    current_gender = st.session_state.get('gender_selectbox', gender_options[0])
    gender_default_idx = 0
    if current_gender in gender_options:
        gender_default_idx = gender_options.index(current_gender)
    st.selectbox(
        labels['Gender'], gender_options,
        index=gender_default_idx,
        key="gender_selectbox", # Unique key
        on_change=save_draft # Add save_draft for these too
    )

    # --- PHOTO UPLOAD SECTION MOVED HERE ---
    st.header(labels['Upload Photos'])
    uploaded_files = st.file_uploader(
        labels['Upload Photos'],
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="image_uploader_outside_form" # New unique key for file_uploader outside the form
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_content = uploaded_file.getvalue()
            file_hash = base64.b64encode(file_content).decode()

            is_duplicate = False
            # Check for duplicates based on content hash and existing paths
            for existing_path in st.session_state.get('uploaded_temp_photo_paths', []):
                if os.path.exists(existing_path):
                    with open(existing_path, "rb") as f:
                        existing_hash = base64.b64encode(f.read()).decode()
                    if existing_hash == file_hash:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                if len(st.session_state.get('uploaded_temp_photo_paths', [])) < 3:
                    unique_filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{uploaded_file.name.replace(' ', '_')}"
                    temp_photo_path = os.path.join(TEMP_IMAGE_DIR, unique_filename)
                    try:
                        with open(temp_photo_path, "wb") as f:
                            f.write(file_content)
                        st.session_state.uploaded_temp_photo_paths.append(temp_photo_path)
                        st.success(f"{labels['Photo uploaded successfully!']} {uploaded_file.name}")
                        save_draft() # Save draft immediately after successful upload
                        st.rerun() # Rerun to update the displayed images and clear the uploader
                    except Exception as e:
                        st.error(f"{labels['Error uploading photo:']} {uploaded_file.name}. {e}")
                else:
                    st.warning(f"Could not upload {uploaded_file.name}: {labels['Please upload up to 3 photos.']}")
            else:
                st.info(f"Skipping duplicate photo: {uploaded_file.name}")
    
    if st.session_state.get('uploaded_temp_photo_paths'):
        st.subheader("Currently uploaded photos:")
        photos_to_display = list(st.session_state.uploaded_temp_photo_paths) # Create a copy to iterate
        
        # Clean up invalid paths first
        valid_photos = []
        rerun_needed_for_cleanup = False
        for photo_path in photos_to_display:
            if os.path.exists(photo_path):
                valid_photos.append(photo_path)
            else:
                rerun_needed_for_cleanup = True # Mark that a cleanup occurred

        if rerun_needed_for_cleanup:
            st.session_state.uploaded_temp_photo_paths = valid_photos
            st.warning("Some temporary photo paths were invalid and have been removed. Rerunning to update display.")
            st.rerun() # Trigger rerun to update UI after cleaning
        
        if valid_photos: # Only proceed if there are valid photos to display
            cols = st.columns(3)
            for i, photo_path in enumerate(valid_photos):
                try:
                    with open(photo_path, "rb") as f:
                        encoded_string = base64.b64encode(f.read()).decode()
                    
                    with cols[i % 3]:
                        st.image(f"data:image/png;base64,{encoded_string}", caption=os.path.basename(photo_path), use_column_width=True)
                        # The key for the remove button must be unique and stable across reruns
                        if st.button(f"Remove", key=f"remove_photo_{i}_{os.path.basename(photo_path).replace('.', '_')}"):
                            os.remove(photo_path)
                            st.session_state.uploaded_temp_photo_paths.remove(photo_path)
                            save_draft() # Save draft after removal
                            st.rerun() # Use this for immediate effect
                except Exception as e:
                    cols[i % 3].error(f"Could not load image {os.path.basename(photo_path)}: {e}")
                    # If an error occurs during loading, remove the path from session state
                    if photo_path in st.session_state.uploaded_temp_photo_paths:
                        st.session_state.uploaded_temp_photo_paths.remove(photo_path)
                        save_draft()
                        st.rerun() # Trigger rerun to update UI after cleaning
        else:
            st.info(labels['No photo uploaded.'])
    else:
        st.info(labels['No photo uploaded.'])
    # --- END PHOTO UPLOAD SECTION ---


    # --- Start of the actual Streamlit form for other fields ---
    with st.form("survey_form_details"):
        st.header(labels['Farm Details'])
        
        st.number_input(
            labels['Number of Cows'], min_value=0,
            value=int(st.session_state.get('cows_input', 0)),
            key="cows_input"
        )
        st.number_input(
            labels['No. of Cattle in Milk'], min_value=0,
            value=int(st.session_state.get('cattle_in_milk_input', 0)),
            key="cattle_in_milk_input"
        )
        st.number_input(
            labels['No. of Calves/Heifers'], min_value=0,
            value=int(st.session_state.get('calves_input', 0)),
            key="calves_input"
        )
        st.number_input(
            labels['No. of Desi cows'], min_value=0,
            value=int(st.session_state.get('desi_cows_input', 0)),
            key="desi_cows_input"
        )
        st.number_input(
            labels['No. of Cross breed cows'], min_value=0,
            value=int(st.session_state.get('crossbreed_cows_input', 0)),
            key="crossbreed_cows_input"
        )
        st.number_input(
            labels['No. of Buffalo'], min_value=0,
            value=int(st.session_state.get('buffalo_input', 0)),
            key="buffalo_input"
        )
        st.number_input(
            labels['Milk Production'], min_value=0.0, format="%.2f",
            value=float(st.session_state.get('milk_production_input', 0.0)),
            key="milk_production_input"
        )

        st.header(labels['Specific Questions'])
        green_fodder_options = (labels['Yes'], labels['No'])
        current_green_fodder = st.session_state.get('green_fodder_radio', green_fodder_options[0])
        green_fodder_default_idx = 0
        if current_green_fodder in green_fodder_options:
            green_fodder_default_idx = green_fodder_options.index(current_green_fodder)
        st.radio(
            labels['Green Fodder'], green_fodder_options,
            index=green_fodder_default_idx,
            key="green_fodder_radio"
        )
        
        if st.session_state.green_fodder_radio == labels['Yes']:
            st.multiselect(
                labels['Type of Green Fodder'], GREEN_FODDER_OPTIONS,
                default=st.session_state.get('green_fodder_types_multi', []),
                key="green_fodder_types_multi"
            )
            st.number_input(
                labels['Quantity of Green Fodder'], min_value=0.0, format="%.2f",
                value=float(st.session_state.get('green_fodder_qty_input', 0.0)),
                key="green_fodder_qty_input"
            )
        else:
            # When radio button is 'No', clear these values in session state
            st.session_state.green_fodder_types_multi = []
            st.session_state.green_fodder_qty_input = 0.0

        dry_fodder_options = (labels['Yes'], labels['No'])
        current_dry_fodder = st.session_state.get('dry_fodder_radio', dry_fodder_options[0])
        dry_fodder_default_idx = 0
        if current_dry_fodder in dry_fodder_options:
            dry_fodder_default_idx = dry_fodder_options.index(current_dry_fodder)
        st.radio(
            labels['Dry Fodder'], dry_fodder_options,
            index=dry_fodder_default_idx,
            key="dry_fodder_radio"
        )
        
        if st.session_state.dry_fodder_radio == labels['Yes']:
            st.multiselect(
                labels['Type of Dry Fodder'], DRY_FODDER_OPTIONS,
                default=st.session_state.get('dry_fodder_types_multi', []),
                key="dry_fodder_types_multi"
            )
            st.number_input(
                labels['Quantity of Dry Fodder'], min_value=0.0, format="%.2f",
                value=float(st.session_state.get('dry_fodder_qty_input', 0.0)),
                key="dry_fodder_qty_input"
            )
        else:
            st.session_state.dry_fodder_types_multi = []
            st.session_state.dry_fodder_qty_input = 0.0

        pellet_feed_options = (labels['Yes'], labels['No'])
        current_pellet_feed = st.session_state.get('pellet_feed_radio', pellet_feed_options[0])
        pellet_feed_default_idx = 0
        if current_pellet_feed in pellet_feed_options:
            pellet_feed_default_idx = pellet_feed_options.index(current_pellet_feed)
        st.radio(
            labels['Pellet Feed'], pellet_feed_options,
            index=pellet_feed_default_idx,
            key="pellet_feed_radio"
        )
        
        if st.session_state.pellet_feed_radio == labels['Yes']:
            st.multiselect(
                labels['Pellet Feed Brand'], PELLET_FEED_BRANDS,
                default=st.session_state.get('pellet_feed_brands_multi', []),
                key="pellet_feed_brands_multi"
            )
            st.number_input(
                labels['Quantity of Pellet Feed'], min_value=0.0, format="%.2f",
                value=float(st.session_state.get('pellet_feed_qty_input', 0.0)),
                key="pellet_feed_qty_input"
            )
        else:
            st.session_state.pellet_feed_brands_multi = []
            st.session_state.pellet_feed_qty_input = 0.0

        mineral_mixture_options = (labels['Yes'], labels['No'])
        current_mineral_mixture = st.session_state.get('mineral_mixture_radio', mineral_mixture_options[0])
        mineral_mixture_default_idx = 0
        if current_mineral_mixture in mineral_mixture_options:
            mineral_mixture_default_idx = mineral_mixture_options.index(current_mineral_mixture)
        st.radio(
            labels['Mineral Mixture'], mineral_mixture_options,
            index=mineral_mixture_default_idx,
            key="mineral_mixture_radio"
        )
        
        if st.session_state.mineral_mixture_radio == labels['Yes']:
            mineral_brand_default_idx = 0
            if st.session_state.get('mineral_brand_select') in MINERAL_MIXTURE_BRANDS:
                mineral_brand_default_idx = MINERAL_MIXTURE_BRANDS.index(st.session_state.get('mineral_brand_select'))
            st.selectbox(
                labels['Mineral Mixture Brand'], MINERAL_MIXTURE_BRANDS,
                index=mineral_brand_default_idx,
                key="mineral_brand_select"
            )
            st.number_input(
                labels['Quantity of Mineral Mixture'], min_value=0.0, format="%.2f",
                value=float(st.session_state.get('mineral_qty_input', 0.0)),
                key="mineral_qty_input"
            )
        else:
            st.session_state.mineral_brand_select = MINERAL_MIXTURE_BRANDS[0] if MINERAL_MIXTURE_BRANDS else None
            st.session_state.mineral_qty_input = 0.0

        silage_options = (labels['Yes'], labels['No'])
        current_silage = st.session_state.get('silage_radio', silage_options[0])
        silage_default_idx = 0
        if current_silage in silage_options:
            silage_default_idx = silage_options.index(current_silage)
        st.radio(
            labels['Silage'], silage_options,
            index=silage_default_idx,
            key="silage_radio"
        )
        
        if st.session_state.silage_radio == labels['Yes']:
            st.text_input(
                labels['Source and Price of Silage'],
                value=st.session_state.get('silage_source_input', ''),
                key="silage_source_input"
            )
            st.number_input(
                labels['Quantity of Silage'], min_value=0.0, format="%.2f",
                value=float(st.session_state.get('silage_qty_input', 0.0)),
                key="silage_qty_input"
            )
        else:
            st.session_state.silage_source_input = ""
            st.session_state.silage_qty_input = 0.0

        st.multiselect(
            labels['Source of Water'], WATER_SOURCE_OPTIONS,
            default=st.session_state.get('water_sources_multi', []),
            key="water_sources_multi"
        )

        st.header("Survey Details")
        current_surveyor_name = st.session_state.get('surveyor_name_select', SURVEYOR_NAMES[0] if SURVEYOR_NAMES else None)
        surveyor_name_default_idx = 0
        if current_surveyor_name in SURVEYOR_NAMES:
            surveyor_name_default_idx = SURVEYOR_NAMES.index(current_surveyor_name)
        st.selectbox(
            labels['Name'], SURVEYOR_NAMES,
            index=surveyor_name_default_idx,
            key="surveyor_name_select"
        )
        
        current_visit_date = st.session_state.get('visit_date_input', datetime.date.today())
        if not isinstance(current_visit_date, datetime.date):
            try:
                current_visit_date = datetime.date.fromisoformat(current_visit_date)
            except (TypeError, ValueError):
                current_visit_date = datetime.date.today()

        st.date_input(
            labels['Date of Visit'],
            value=current_visit_date,
            key="visit_date_input"
        )

        # --- Submit Button (MUST BE INSIDE THE FORM) ---
        submit_for_review = st.form_submit_button(labels['Submit'])

        if submit_for_review:
            # When the form submits, we gather values from session state for all fields,
            # both those outside the form (farmer ID, photos) and inside the form (farm details, etc.).
            final_farmer_name = st.session_state.farmer_name_other_input if st.session_state.farmer_name_selected_select == labels['Others'] else st.session_state.farmer_name_selected_select

            data_for_review = {
                "Language": st.session_state.lang_select,
                "VLCC Name": st.session_state.vlcc_name_select,
                "HPC/MCC Code": st.session_state.hpc_code_display,
                "Type": st.session_state.types_selectbox,
                "Farmer Name": final_farmer_name,
                "Farmer Code / Pourer ID": st.session_state.farmer_code_select if st.session_state.farmer_code_select else 'N/A',
                "Rep ID (Phone Number)": st.session_state.rep_id_display,
                "Gender": st.session_state.gender_selectbox,
                "Number of Cows": st.session_state.cows_input,
                "No. of Cattle in Milk": st.session_state.cattle_in_milk_input,
                "No. of Calves/Heifers": st.session_state.calves_input,
                "No. of Desi cows": st.session_state.desi_cows_input,
                "No. of Cross breed cows": st.session_state.crossbreed_cows_input,
                "No. of Buffalo": st.session_state.buffalo_input,
                "Milk Production (liters/day)": st.session_state.milk_production_input,
                "Green Fodder Provided": st.session_state.green_fodder_radio,
                "Type of Green Fodder": ", ".join(st.session_state.get('green_fodder_types_multi', [])) if st.session_state.get('green_fodder_radio') == labels['Yes'] else "N/A",
                "Quantity of Green Fodder (Kg/day)": st.session_state.get('green_fodder_qty_input', 0.0) if st.session_state.get('green_fodder_radio') == labels['Yes'] else 0.0,
                "Dry Fodder Provided": st.session_state.dry_fodder_radio,
                "Type of Dry Fodder": ", ".join(st.session_state.get('dry_fodder_types_multi', [])) if st.session_state.get('dry_fodder_radio') == labels['Yes'] else "N/A",
                "Quantity of Dry Fodder (Kg/day)": st.session_state.get('dry_fodder_qty_input', 0.0) if st.session_state.get('dry_fodder_radio') == labels['Yes'] else 0.0,
                "Pellet Feed Provided": st.session_state.pellet_feed_radio,
                "Pellet Feed Brand": ", ".join(st.session_state.get('pellet_feed_brands_multi', [])) if st.session_state.get('pellet_feed_radio') == labels['Yes'] else "N/A",
                "Quantity of Pellet Feed (Kg/day)": st.session_state.get('pellet_feed_qty_input', 0.0) if st.session_state.get('pellet_feed_radio') == labels['Yes'] else 0.0,
                "Mineral Mixture Provided": st.session_state.mineral_mixture_radio,
                "Mineral Mixture Brand": st.session_state.get('mineral_brand_select') if st.session_state.get('mineral_mixture_radio') == labels['Yes'] else "N/A",
                "Quantity of Mineral Mixture (gm/day)": st.session_state.get('mineral_qty_input', 0.0) if st.session_state.get('mineral_mixture_radio') == labels['Yes'] else 0.0,
                "Silage Provided": st.session_state.silage_radio,
                "Source and Price of Silage": st.session_state.get('silage_source_input', '') if st.session_state.get('silage_radio') == labels['Yes'] else "N/A",
                "Quantity of Silage (Kg/day)": st.session_state.get('silage_qty_input', 0.0) if st.session_state.get('silage_radio') == labels['Yes'] else 0.0,
                "Source of Water": ", ".join(st.session_state.get('water_sources_multi', [])) if st.session_state.get('water_sources_multi') else "N/A",
                "Name of Surveyor": st.session_state.surveyor_name_select,
                "Date of Visit": st.session_state.visit_date_input.isoformat(),
                "Photo Paths": st.session_state.uploaded_temp_photo_paths
            }
            st.session_state.final_submitted_data = data_for_review
            st.session_state.current_step = 'review'
            save_draft()
            st.rerun()

elif st.session_state.current_step == 'review':
    st.title(labels['Review Your Submission'])
    st.write("Please review the information below before final submission.")

    data_to_review = st.session_state.final_submitted_data

    if data_to_review:
        st.subheader("Farmer Profile")
        st.write(f"**{labels['Language']}:** {data_to_review['Language']}")
        st.write(f"**{labels['VLCC Name']}:** {data_to_review['VLCC Name']}")
        st.write(f"**{labels['HPC/MCC Code']}:** {data_to_review['HPC/MCC Code']}")
        st.write(f"**{labels['Types']}:** {data_to_review['Type']}")
        st.write(f"**{labels['Farmer Name']}:** {data_to_review['Farmer Name']}")
        st.write(f"**{labels['Farmer Code']}:** {data_to_review['Farmer Code / Pourer ID']}")
        st.write(f"**Rep ID (Phone Number):** {data_to_review['Rep ID (Phone Number)']}")
        st.write(f"**{labels['Gender']}:** {data_to_review['Gender']}")

        st.subheader("Farm Details")
        st.write(f"**{labels['Number of Cows']}:** {data_to_review['Number of Cows']}")
        st.write(f"**{labels['No. of Cattle in Milk']}:** {data_to_review['No. of Cattle in Milk']}")
        st.write(f"**{labels['No. of Calves/Heifers']}:** {data_to_review['No. of Calves/Heifers']}")
        st.write(f"**{labels['No. of Desi cows']}:** {data_to_review['No. of Desi cows']}")
        st.write(f"**{labels['No. of Cross breed cows']}:** {data_to_review['No. of Cross breed cows']}")
        st.write(f"**{labels['No. of Buffalo']}:** {data_to_review['No. of Buffalo']}")
        st.write(f"**{labels['Milk Production']}:** {data_to_review['Milk Production (liters/day)']}")

        st.subheader("Specific Questions")
        st.write(f"**{labels['Green Fodder']}:** {data_to_review['Green Fodder Provided']}")
        if data_to_review['Green Fodder Provided'] == labels['Yes']:
            st.write(f"**{labels['Type of Green Fodder']}:** {data_to_review['Type of Green Fodder']}")
            st.write(f"**{labels['Quantity of Green Fodder']}:** {data_to_review['Quantity of Green Fodder (Kg/day)']}")

        st.write(f"**{labels['Dry Fodder']}:** {data_to_review['Dry Fodder Provided']}")
        if data_to_review['Dry Fodder Provided'] == labels['Yes']:
            st.write(f"**{labels['Type of Dry Fodder']}:** {data_to_review['Type of Dry Fodder']}")
            st.write(f"**{labels['Quantity of Dry Fodder']}:** {data_to_review['Quantity of Dry Fodder (Kg/day)']}")

        st.write(f"**{labels['Pellet Feed']}:** {data_to_review['Pellet Feed Provided']}")
        if data_to_review['Pellet Feed Provided'] == labels['Yes']:
            st.write(f"**{labels['Pellet Feed Brand']}:** {data_to_review['Pellet Feed Brand']}")
            st.write(f"**{labels['Quantity of Pellet Feed']}:** {data_to_review['Quantity of Pellet Feed (Kg/day)']}")

        st.write(f"**{labels['Mineral Mixture']}:** {data_to_review['Mineral Mixture Provided']}")
        if data_to_review['Mineral Mixture Provided'] == labels['Yes']:
            st.write(f"**{labels['Mineral Mixture Brand']}:** {data_to_review['Mineral Mixture Brand']}")
            st.write(f"**{labels['Quantity of Mineral Mixture']}:** {data_to_review['Quantity of Mineral Mixture (gm/day)']}")

        st.write(f"**{labels['Silage']}:** {data_to_review['Silage Provided']}")
        if data_to_review['Silage Provided'] == labels['Yes']:
            st.write(f"**{labels['Source and Price of Silage']}:** {data_to_review['Source and Price of Silage']}")
            st.write(f"**{labels['Quantity of Silage']}:** {data_to_review['Quantity of Silage (Kg/day)']}")

        st.write(f"**{labels['Source of Water']}:** {data_to_review['Source of Water']}")
        
        st.subheader("Survey Details")
        st.write(f"**{labels['Name']}:** {data_to_review['Name of Surveyor']}")
        st.write(f"**{labels['Date of Visit']}:** {data_to_review['Date of Visit']}")

        st.subheader(labels['Upload Photos'])
        if data_to_review['Photo Paths']:
            cols = st.columns(3)
            for i, photo_path in enumerate(data_to_review['Photo Paths']):
                if os.path.exists(photo_path):
                    try:
                        with open(photo_path, "rb") as f:
                            encoded_string = base64.b64encode(f.read()).decode()
                        with cols[i % 3]:
                            st.image(f"data:image/png;base64,{encoded_string}", use_column_width=True)
                            st.caption(os.path.basename(photo_path))
                    except Exception as e:
                        cols[i % 3].error(f"Could not load image {os.path.basename(photo_path)}: {e}")
                else:
                    st.warning(f"Image not found for review: {os.path.basename(photo_path)}")
        else:
            st.info(labels['No photo uploaded.'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(labels['Confirm and Submit'], key="confirm_submit_button"):
                final_photo_paths = []
                for temp_path in st.session_state.uploaded_temp_photo_paths:
                    if os.path.exists(temp_path):
                        final_image_name = os.path.basename(temp_path)
                        final_path = os.path.join(FINAL_IMAGE_DIR, final_image_name)
                        try:
                            shutil.move(temp_path, final_path)
                            final_photo_paths.append(final_path)
                        except Exception as e:
                            st.error(f"Error moving photo {os.path.basename(temp_path)}: {e}")
                            final_photo_paths.append(temp_path)
                    else:
                        st.warning(f"Temporary photo {os.path.basename(temp_path)} not found during final submission. Skipping.")
                
                data_to_review["Photo Paths"] = ", ".join(final_photo_paths)

                df = pd.DataFrame([data_to_review])

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(SAVE_DIR, f"survey_response_{timestamp}.csv")

                try:
                    file_exists = os.path.exists(file_path)
                    df.to_csv(file_path, mode='a', header=not file_exists, index=False)
                    
                    st.session_state.current_step = 'submitted'
                    st.session_state.last_saved_time_persistent = None
                    
                    for f in os.listdir(TEMP_IMAGE_DIR):
                        os.remove(os.path.join(TEMP_IMAGE_DIR, f))
                    st.session_state.uploaded_temp_photo_paths = []

                    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
                    if os.path.exists(draft_filename):
                        os.remove(draft_filename)

                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving data: {e}")
        with col2:
            if st.button(labels['Edit Form'], key="edit_form_button"):
                st.session_state.current_step = 'form_entry'
                st.rerun()
    else:
        st.warning("No data found to review. Please go back and fill the form.")
        if st.button(labels['Edit Form']):
            st.session_state.current_step = 'form_entry'
            st.rerun()

elif st.session_state.current_step == 'submitted':
    st.balloons()
    st.success(labels['Successfully Submitted!'])
    st.write("Thank you for your submission!")
    if st.button(labels['Fill Another Form']):
        clear_form_fields()

# --- Sidebar for Download Options ---
st.sidebar.markdown("---")
st.sidebar.header("Download Options")

all_responses_df = get_all_responses_df()
if not all_responses_df.empty:
    csv_data = all_responses_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label=labels['Download All Responses (CSV)'],
        data=csv_data,
        file_name="all_survey_responses.csv",
        mime="text/csv",
        key="download_all_csv"
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        all_responses_df.to_excel(writer, index=False, sheet_name='SurveyResponses')
    excel_buffer.seek(0)
    st.sidebar.download_button(
        label=labels['Download All Responses (Excel)'],
        data=excel_buffer.getvalue(),
        file_name="all_survey_responses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_all_excel"
    )
else:
    st.sidebar.info("No survey responses available for download (CSV/Excel).")

if os.path.exists(FINAL_IMAGE_DIR) and os.listdir(FINAL_IMAGE_DIR):
    zip_buffer = create_zip_file()
    st.sidebar.download_button(
        label=labels['Download All Photos (ZIP)'],
        data=zip_buffer,
        file_name="all_survey_photos.zip",
        mime="application/zip",
        key="download_all_photos_zip"
    )
else:
    st.sidebar.info("No photos available for download (ZIP).")
