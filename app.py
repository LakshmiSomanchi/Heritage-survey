# app.py (Heritage Specific Streamlit Dairy Survey)

import streamlit as st
import pandas as pd
import datetime
import os
import json # To save/load session state as JSON

# Ensure save folder exists
SAVE_DIR = 'survey_responses'
os.makedirs(SAVE_DIR, exist_ok=True)

# Define a directory for auto-saved drafts
DRAFT_DIR = os.path.join(SAVE_DIR, 'drafts')
os.makedirs(DRAFT_DIR, exist_ok=True)

# Streamlit Page Config - THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Heritage Dairy Survey", page_icon="🐄", layout="centered")


# Multilingual Translations
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
        'Name': 'Name', 'Date of Visit': 'Date of Visit', # Changed 'Name of Surveyor' to 'Name' in English
        'Submit': 'Submit', 'Yes': 'Yes', 'No': 'No', 'Download CSV': 'Download CSV',
        'Auto-saved!': 'Auto-saved! You can resume filling the form even if you refresh or lose internet temporarily.',
        'Others': 'Others', # Added for "Others" option
        'Specify Farmer Name': 'Specify Farmer Name (if Others selected)', # Added for specifying "Others"
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
        'Name': 'सर्वेक्षक का नाम', 'Date of Visit': 'दौरे की तिथि', # Changed 'Name of Surveyor' to 'Name' in Hindi
        'Submit': 'जमा करें', 'Yes': 'हाँ', 'No': 'नहीं', 'Download CSV': 'CSV डाउनलोड करें',
        'Auto-saved!': 'स्वतः सहेजा गया! आप फ़ॉर्म भरना जारी रख सकते हैं, भले ही आप ताज़ा करें या अस्थायी रूप से इंटरनेट खो दें!',
        'Others': 'अन्य', # Added for "Others" option
        'Specify Farmer Name': 'किसान का नाम निर्दिष्ट करें (यदि अन्य चुना गया हो)', # Added for specifying "Others"
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
        "Type of Farm": "शेताचा प्रकार",
        "Other Type of Farm (if selected above)": "इतर शेताचा प्रकार (वर निवडल्यास)",
        "Source of Water": "पाण्याचा स्त्रोत (अनेक निवडा)",
        "Name": "सर्वेक्षकाचे नाव", # Changed 'Name of Surveyor' to 'Name' in Marathi
        "Date of Visit": "भेटीची तारीख",
        "Submit": "सादर करा",
        "Yes": "होय",
        "No": "नाही",
        "Download CSV": "CSV डाउनलोड करा",
        "Auto-saved!": "स्वयं-जतन केले! आपण रिफ्रेश केले किंवा तात्पुरते इंटरनेट गमावले तरीही आपण फॉर्म भरणे सुरू ठेवू शकता.",
        'Others': 'इतर', # Added for "Others" option
        'Specify Farmer Name': 'शेतकऱ्याचे नाव नमूद करा (इतर निवडल्यास)', # Added for specifying "Others"
    }
}


# --- Heritage Specific Data
VLCC_NAMES = ["3025-K.V.PALLE","3026-KOTHA PALLE","3028-BONAMVARIPALLE","3029-BOMMAICHERUVUPALLI","3030-BADDALAVARIPALLI","3033-CHINNAGOTTIGALLU","3034-VODDIPALLE","3036-MUDUPULAVEMULA","3037-BAYYAREDDYGARIPALLE","3038-DODDIPALLE","3040-MARAMREDDYGARIPALLE","3041-GUTTAPALEM","3042-CHERUVUMUNDARAPALLI","3044-VARAMPATIVARIPALLE",
"3045-ROMPICHERLA","3046-BANDAKINDAPALLE","3047-MARASANIVARIPALLI",
"3024-DEVALAVARIPALLE","3002-KHAMBAMMITTAPALLE","3004-MARRIMAKULAPALLE","3005-NAGARIMADUGUVARIPALLE","3006-KOORAPARTHIVARIPALLE","3008-IRRIVANDLAPALLE","3009-PATHEGADA (U.I)","3011-PULICHERLA","3013-GUDAREVUPALLE","3014-ENUMALAVARIPALLE","3015-MUNTHAVANDLAPALLE","3016-REGALLU",
"3018-REDDIVARIPALLE","3019-MAJJIGAVANDLAPALLE","3020-VENKATADASARAPALLE","3021-BURRAVANDLAPALLE","3022-KODEKAMBAMVARIPALLI","3023-SEENAPPAGARIPALLE","3071-KOTAKADAPALLE","3072-KOTAKADAPALLE","3074-PODALAKUNTALAPALLE","3075-SOMALA","3076-SOMALA","3077-SOMALA","3078-CHINNAGOTTIGALLU","3079-MATLOLLPALLAI",
"3080-POLIKIMAKULAPALLE","3081-K.GOLLAPALLE","3082-CHERUKUVARIPALLE","3083-SODUM","3084-PILER","3085-CHERUKUVARIPALLE","3086-SOMALA","3087-SODUM","3088-YERRAVARIPALEM",
"3089-GUDAREVUPALLE","3090-SOMALA","3091-PUTTAVARIPALLE","3092-VAGALLA","3048-R.KUMMARA PALLE","3049-HANUMANTHARAYUNIPETA","3050-CHENCHAMAREDDIGARIPALLE","3051-BODUMALLUVARIPALLE","3052-BANDAKINDAPALLE","3055-NAKKALADINNEVODDIPALLE","3057-KUKKALODDU",
"3059-GUNDLAKADAPALLI","3070-PEDDAPANJANI","3069-PEDDAPALLI","3068-KADIRAKUNTA","3067-KOTALA","3066-VLLIGATLA(U.I)","3060-BALIREDDIGARIPALLE","3061-SODUM","3062-GONGIVARIPALLE","3064-SRINADHAPURAM","3063-GANGUVARIPALLE","1664-DEVALAMPETA","1651-YERRAGUNTLAVARIPALLE","1740-KALIKIRI","1718-KOTHA PALLE",
"1542-HARIJANAWADA","1937-KAMMAPALLE","1993-T.SANDRAVARIPALLE","1959-MANCHOORIVARIPALLE","1812-GANGIREDDIGARIPALLE","1781-ROMPICHERLA","1773-SREERAMULAVADDIPALLE","1770-THATIGUNTAPALEM","1868-ROMPICHERLA","1824-YERRAGUNTLAVARIPALLE","0884-KOTHAPALLE","0881-ROMPICHERLA","0880-MUREVANDLAPALLE","0878-KALIKIRI","0876-DIGUVAJUPALLI",
"0874-KONDAREDDIGARIPALLE","0871-ROMPICHERLA","0868-NAGARIMADUGUVARIPALLE","0863-KHAMBAMMITTAPALLE","0906-REDDIVARIPALLE","0900-GOLLAPALLE","0895-PEDDAMALLELA","0893-PEDDIREDDIGARIPALLE","0888-BANDARALAVARIPALLE","0887-ELLAMPALLE","0830-REGALLU","0826-MUNIREDDIGARIPALLE","0824-PILER",
"0859-KRIHSNAREDDIGARIPALLE","0851-GYARAMPALLE","0848-ELLAREDDIGARIPALLE","0846-KURAVAPALLE","0842-PEDDAMALLELA","0839-BANDAMVARIPALLE","1058-CHERUKUVARIPALLE","1057-CHERUKUVARIPALLE","1052-NANJAMPETA","1017-KHAMBAMVARIPALLE","1003-PUTTAVANDLAPALLE THANDA","1272-USTIKAYALAPENTA",
"1240-MITTAPALLE","0916-AGRAHARAM","0915-CHALLAVARIPALLE","0982-KUCHAMVARIPALLE","2388-SAGGAMVARI ENDLU","2380-PILER",
"2374-PILER","2437-MARRIMAKULAPALLE","2421-MATLOLLPALLAI","2314-KUMMARAPALLE","2338-SETTIPALLEVANDLAPALLE","2500-KAMMAPALLE","2530-AVULAPEDDIREDDIGARIPALL","2528-MARAMREDDIGARIPALLE","2526-AVULAPEDDIREDDIGARIPALL","2463-BOMMAIAHGARIPALLE","2444-ROMPICHERLA","2440-BASIREDDIGARIPALLE",
"2013-THOTIMALAPALLE","2083-RAJUVARIPALLI H/W","2045-RAJUVARIPALLI","2288-RAJUVARIPALLI","2272-THATIGUNTAPALEM","2186-KANTAMVARIPALLE","2183-REGALLU","2178-SANKENIGUTTAPALLE","2173-MUNELLAPALLE","2160-V.K.THURPUPALLE","2228-GAJULAVARIPALLI","0296-BESTAPALLE",
"0335-MATLOLLPALLAI","0326-LOKAVARIPALLE","0256-VOOTUPALLE","0245-BETAPALLE","0237-BATTUVARIPALLE","0417-ROMPICHERLA","0414-BODIPATIVARIPALLE","0441-BODIPATIVARIPALLE","0440-VARANASIVARIPALLE",
"0360-CHICHILIVARIPALLE",
"0357-AKKISANIVARIPALLE", "0394-SETTIPALLEVANDLAPALLE", "0072-VAGALLA",
"0056-LEMATIVARIPALLE", "0108-KONDAREDDIGARIPALLE","0016-ROMPICHERLA",
"0030-MELLAVARIPALLE", "0197-BASIREDDIGARIPALLE", "0173-MORAVAPALLE",
"0221-KURABAPALLE", "0130-PATHAKURVAPALLE", "0165-AGRAHARAM",
"0151-BONAMVARIPALLE", "0649-PILER", "0645-NADIMPALLE",
"0643-SAVVALAVARIPALLE", "0636-KURAPATHIVARIPALLE", "0689-VANKAVODDIPALLE",
"0688-BADDALAVARIPALLI H.W.","0685-NAGARIMADUGUVARIPALLE", "0668-KANDUR",
"0663-DEVALAVARIPALLE", "0585-SRIVARAMPURAM", "0575-RAMREDDIGARIPALLE",
"0572-LOKAVARIPALLE", "0613-NAGAVANDLAPALLI", "0611-BODIPATIVARIPALLE",
"0610-ROMPICHERLA", "0604-NAGAVANDLAPALLI", "0782-CHICHILIVARIPALLE",
"0770-DEVALAVARIPALLE", "0767-PEDDAGOTTIGALLU", "0764-K.V.PALLE",
"0762-JAGADAMVARIPALLE", "0753-BOLLINANIVARIPALLI", "0813-ROMPICHERLA",
"0811-ALAKAMVARIPALLE", "0809-KOTAKADAPALLE", "0794-PEDDAGOTTIGALLU",
"0793-DIGUVAJUPALLI", "0789-SODUM", "0788-BURUJUPALLE",
"0786-PEDDAGOTTIGALLU CROSS", "0719-NADIMPALLE", "0718-PEDDAGOTTIGALLU",
"0714-BODIPATIVARIPALLE", "0709-REDDIVARIPALLE", "0700-RAMIREDDIGARIPALLE",
"0721-SODUM", "0747-KURAVAPALLE", "0745-ETUKURIVARIPALLE",
"0743-ROMPICHERLA", "0736-VOOTUPALLE", "0732-ROMPICHERLA",
"0727-DUSSAVANDLA PALLI", "0726-SAVVALAVARIPALLE", "0508-MUREVANDLAPALLE",
"0490-MATAMPALLE", "0551-TALUPULA", "0512-BONAMVARIPALLE",
"0473-KURAVAPALLE", "0477-VARANASIVARIPALLE"
]

# Create a dictionary for farmer data
FARMER_DATA = {
    "0005": "KATTARI VASANTA KUMARI",
    "0006": "GUDISI NARAYANAMMA",
    "0007": "P SUREKHA",
    "0008": "VAGUMALLU SUDHAKARREDDY",
    "0015": "VANGUNALLI REDDY SEKHAR REDDY",
    "0017": "Y REDDEMMA",
    "0003": "INDIRAVATHI MARRIPATTI",
    "0008": "CHIKATIPALLI VASANTHA",
    "0011": "BIRE LAKSHMI DEVI",
    "0013": "B SAMPURNA",
    "0016": "R PADMA",
    "0017": "KRISHTNAMMA KOTAKONDA",
    "0018": "A LAKSHMAIAH",
    "0021": "CANDRAKALA GURRAMKONDA",
    "0025": "P JYOTHI",
    "0030": "M KANTHAMMA",
    "0033": "M CHANDRA",
    "0036": "C SURYA PRAKASH",
    "0001": "P SHANKARAMMA",
    "0012": "V PRAMEELA",
    "0003": "RAJINI KUMAR REDDY M",
    "0002": "D GOPAL NAIDU",
    "0003": "D PRASAD REDDY",
    "0006": "G RATHNAMMA",
    "0009": "M NARAYANAMMA",
    "0012": "V DEVAKI",
    "0026": "P HARSHA VARDHAN REDDY",
    "0019": "B REDDEMMA",
    "0002": "J RAMADEVI",
    "0003": "N SIDDAMA",
    "0005": "J ESWARAMMA",
    "0006": "M SIDDAMMA",
    "0008": "Y DEVAKI DEVI",
    "0003": "C RAMANAIAH",
    "0014": "P REDDY PRASAD",
    "0002": "B VARA LAKSHMI",
    "0003": "D NAGARJUNA",
    "0001": "C USHARANI",
    "0006": "S SHAHEEDA BEGUM",
    "0007": "S SHAMSHAD",
    "0008": "S USHA RANI",
    "0010": "V REDDY RANI",
    "0012": "A KALAVATHI",
    "0014": "S YASHODA",
    "0015": "N RESHMA",
    "0016": "D RAMADEVI",
    "0017": "S SHARMILA",
    "0018": "B RANI",
    "0027": "DESIREDDY PALLAVI",
    "0028": "C SREERAMI REDDY",
    "0005": "M JYOSHNA",
    "0013": "M VENKTRAMAIAH",
    "0002": "M BHARGAVI",
    "0006": "N GANGAIAH",
    "0009": "N PURUSHOTHAM",
    "0011": "N RAMADEVI",
    "0017": "Y LAKSHMI",
    "0026": "N SRINIVASULU",
    "0027": "N LAVANYA",
    "0002": "B MURALI",
    "0014": "S MUBARAK ALI",
    "0015": "S SABEEN TAJ",
    "0019": "D NARASAMMA",
    "0020": "V RANI",
    "0001": "A RAJAMMA",
    "0006": "D SURENDRA REDDY",
    "0008": "M VISHNUVARDHAN REDDY",
    "0010": "K SAHADEVA",
    "0002": "D ASHOK KUMAR",
    "0014": "K VENKATRAMAIAH",
    "0006": "K RAJAMMA",
    "0008": "P ANASUYA",
    "0010": "P RAJAMMA",
    "0012": "P SAHADEVAREDDY",
    "0015": "P BHARATHAMMA",
    "0017": "S GOWRAMMA",
    "0008": "V PADMAJA",
    "0010": "V CHITTEMMA",
    "0017": "B GIRI BABU",
    "0019": "P MOHAN BABU",
    "0002": "SREENIVASULU",
    "0012": "C NARSAMMA",
    "0004": "A CHANDRAMMA",
    "0014": "G RAMNJULU",
    "0018": "P SYAMALAMMA",
    "0019": "K BHARGAVI",
    "0012": "M LAKSHMIDEVI",
    "0013": "K MALLESWARI",
    "0016": "M YERRAKKA",
    "0017": "V GANGADEVI",
    "0021": "M CHANDRAMMA"
}

# Create lists for dropdowns
FARMER_CODES = sorted(list(FARMER_DATA.keys())) if FARMER_DATA else []
FARMER_NAMES_ORIGINAL = sorted(list(FARMER_DATA.values())) if FARMER_DATA else [] # Keep original names

GREEN_FODDER_OPTIONS = ["Napier", "Maize", "Sorghum"]
DRY_FODDER_OPTIONS = ["Paddy Straw", "Maize Straw", "Ragi Straw", "Ground Nut Crop Residues"]
PELLET_FEED_BRANDS = ["Heritage Milk Rich", "Heritage Milk Joy", "Heritage Power Plus", "Kamadhenu", "Godrej", "Sreeja", "Vallabha-Panchamruth", "Vallabha-Subham Pusti"]
MINERAL_MIXTURE_BRANDS = ["Herita Vit", "Herita Min", "Other (Specify)"]
WATER_SOURCE_OPTIONS = ["Panchayat", "Borewell", "Water Streams"]
SURVEYOR_NAMES = ["Shiva Shankaraiah", "Reddisekhar", "Balakrishna", "Somasekhar", "Mahesh Kumar", "Dr Swaran Raj Nayak", "Ram Prasad", "K Balaji"]
# -----------------------------

# Define initial_values_defaults at the global scope, before any functions use it
initial_values_defaults = {
    'lang_select': "English",
    'vlcc_name': VLCC_NAMES[0] if VLCC_NAMES else None, # Handle empty list
    'hpc_code': '',
    'types': "HPC",
    'farmer_name_selected': FARMER_NAMES_ORIGINAL[0] if FARMER_NAMES_ORIGINAL else None, # Use a new key for the selected dropdown value
    'farmer_name_other': '', # New field for "Others" farmer name
    'farmer_code': FARMER_CODES[0] if FARMER_CODES else None, # Handle empty list
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
    'mineral_brand': MINERAL_MIXTURE_BRANDS[0] if MINERAL_MIXTURE_BRANDS else None, # Handle empty list
    'mineral_qty': 0.0,
    'silage': "Yes",
    'silage_source': '',
    'silage_qty': 0.0,
    'water_sources': [],
    'surveyor_name': SURVEYOR_NAMES[0] if SURVEYOR_NAMES else None, # Handle empty list
    'visit_date': datetime.date.today()
}

# Function to save current form data to a draft file
def save_draft():
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")

    # Collect all current session state items related to the form
    # Exclude non-serializable objects and form-specific keys
    draft_data = {key: st.session_state[key] for key in initial_values_defaults.keys() if key in st.session_state}

    # Handle date objects for JSON serialization
    if 'visit_date' in draft_data and isinstance(draft_data['visit_date'], datetime.date):
        draft_data['visit_date'] = draft_data['visit_date'].isoformat()

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

            # Update st.session_state with loaded data
            for key, value in loaded_data.items():
                if key == 'visit_date' and isinstance(value, str):
                    try:
                        st.session_state[key] = datetime.date.fromisoformat(value)
                    except ValueError:
                        st.session_state[key] = initial_values_defaults.get(key, datetime.date.today()) # Fallback to default
                elif key in ['green_fodder_types', 'dry_fodder_types', 'pellet_feed_brands', 'water_sources']:
                    # Ensure multiselect defaults are lists, even if loaded as something else
                    st.session_state[key] = list(value) if isinstance(value, list) else []
                else:
                    st.session_state[key] = value

            # After loading, explicitly set language-dependent options based on the loaded language
            current_labels = dict_translations.get(st.session_state.get('lang_select', 'English'), dict_translations['English'])

            # Ensure dropdowns use current labels for their defaults if value is loaded
            # This handles cases where values like "Yes" might not match current labels directly
            # Also, handle cases where the loaded value might not be in the current options list (e.g., if options change)
            if 'types' in st.session_state and st.session_state['types'] not in (current_labels['HPC'], current_labels['MCC']):
                st.session_state['types'] = current_labels['HPC']
            if 'gender' in st.session_state and st.session_state['gender'] not in (current_labels['Male'], current_labels['Female']):
                st.session_state['gender'] = current_labels['Male']
            if 'green_fodder' in st.session_state and st.session_state['green_fodder'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['green_fodder'] = current_labels['Yes']
            if 'dry_fodder' in st.session_state and st.session_state['dry_fodder'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['dry_fodder'] = current_labels['Yes']
            if 'pellet_feed' in st.session_state and st.session_state['pellet_feed'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['pellet_feed'] = current_labels['Yes']
            if 'mineral_mixture' in st.session_state and st.session_state['mineral_mixture'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['mineral_mixture'] = current_labels['Yes']
            if 'silage' in st.session_state and st.session_state['silage'] not in (current_labels['Yes'], current_labels['No']):
                st.session_state['silage'] = current_labels['Yes']

            st.toast("Draft loaded successfully!")
            return True
        except Exception as e:
            st.error(f"Error loading draft: {e}. Please try clearing local storage or starting a new draft.")
            return False
    return False

# Initialize session state with default values, or load from draft
if st.session_state.get('app_initialized_flag', False) is False:
    st.session_state.app_initialized_flag = True

    # Initialize last_saved_time_persistent here to prevent AttributeError
    st.session_state.last_saved_time_persistent = None # Initialize as None or empty string

    loaded_a_draft = load_draft()

    if not loaded_a_draft:
        for key, default_value in initial_values_defaults.items():
            if key not in st.session_state: # Only set if not already loaded by draft
                st.session_state[key] = default_value

# Language Selection
initial_lang_options = ("English", "Hindi", "Marathi") # Restricted language options
initial_lang_index = initial_lang_options.index(st.session_state.lang_select) if st.session_state.lang_select in initial_lang_options else 0
lang = st.selectbox(
    "Language / भाषा / भाषा",
    initial_lang_options,
    index=initial_lang_index,
    key="lang_select",
)
labels = dict_translations.get(lang, dict_translations['English'])

# Title
st.title(labels['Farmer Profile'])

# Display auto-save status.
if st.session_state.last_saved_time_persistent:
    st.info(f"{labels['Auto-saved!']} Last saved: {st.session_state.last_saved_time_persistent}")
else:
    st.info("No auto-saved draft found, or draft cleared. Start filling the form!")


# Form Start
with st.form("survey_form"):
    st.header(labels['Farmer Profile'])

    # All widgets explicitly reference st.session_state for their initial value.
    # Streamlit automatically updates st.session_state[key] on rerun when a widget value changes.

    # VLCC Name
    vlcc_name_default_idx = 0
    if st.session_state.vlcc_name in VLCC_NAMES:
        vlcc_name_default_idx = VLCC_NAMES.index(st.session_state.vlcc_name)
    elif VLCC_NAMES: # If VLCC_NAMES is not empty, default to first
        st.session_state.vlcc_name = VLCC_NAMES[0] # Ensure session state has a valid default
    else: # If VLCC_NAMES is empty, set to None
        st.session_state.vlcc_name = None

    vlcc_name = st.selectbox(
        labels['VLCC Name'], VLCC_NAMES,
        index=vlcc_name_default_idx,
        key="vlcc_name",
        disabled=(not VLCC_NAMES) # Disable if no options
    )

    # HPC/MCC Code
    hpc_code = st.text_input(
        labels['HPC/MCC Code'],
        value=st.session_state.hpc_code,
        key="hpc_code"
    )

    # Types
    types_options = (labels['HPC'], labels['MCC'])
    types_default_idx = types_options.index(st.session_state.types) if st.session_state.types in types_options else 0
    types = st.selectbox(
        labels['Types'], types_options,
        index=types_default_idx,
        key="types"
    )

    # Add 'Others' to FARMER_NAMES options
    farmer_names_with_others = FARMER_NAMES_ORIGINAL + [labels['Others']]

    # Dropdown for Farmer Name
    farmer_name_default_idx = 0
    if st.session_state.farmer_name_selected in farmer_names_with_others:
        farmer_name_default_idx = farmer_names_with_others.index(st.session_state.farmer_name_selected)
    elif farmer_names_with_others:
        st.session_state.farmer_name_selected = farmer_names_with_others[0]
    else:
        st.session_state.farmer_name_selected = None

    farmer_name_selected = st.selectbox(
        labels['Farmer Name'], options=farmer_names_with_others,
        index=farmer_name_default_idx,
        key="farmer_name_selected",
        disabled=(not farmer_names_with_others)
    )

    # Conditional text input for "Others" farmer name
    if farmer_name_selected == labels['Others']:
        farmer_name_other = st.text_input(
            labels['Specify Farmer Name'],
            value=st.session_state.farmer_name_other,
            key="farmer_name_other"
        )
    else:
        st.session_state.farmer_name_other = "" # Clear if "Others" is not selected
        farmer_name_other = "" # This will be empty for data collection

    # Dropdown for Farmer Code
    farmer_code_default_idx = 0
    if st.session_state.farmer_code in FARMER_CODES:
        farmer_code_default_idx = FARMER_CODES.index(st.session_state.farmer_code)
    elif FARMER_CODES:
        st.session_state.farmer_code = FARMER_CODES[0]
    else:
        st.session_state.farmer_code = None

    farmer_code = st.selectbox(
        labels['Farmer Code'], options=FARMER_CODES,
        index=farmer_code_default_idx,
        key="farmer_code",
        disabled=(not FARMER_CODES)
    )

    # Gender
    gender_options = (labels['Male'], labels['Female'])
    gender_default_idx = gender_options.index(st.session_state.gender) if st.session_state.gender in gender_options else 0
    gender = st.selectbox(
        labels['Gender'], gender_options,
        index=gender_default_idx,
        key="gender"
    )

    st.header(labels['Farm Details'])
    # Number of Cows
    cows = st.number_input(
        labels['Number of Cows'], min_value=0,
        value=int(st.session_state.cows), # Cast to int for number_input
        key="cows"
    )
