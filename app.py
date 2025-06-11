import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64 # Import base64 for image handling

# Ensure save folder exists
SAVE_DIR = 'survey_responses'
os.makedirs(SAVE_DIR, exist_ok=True)

# Define a directory for auto-saved drafts
DRAFT_DIR = os.path.join(SAVE_DIR, 'drafts')
os.makedirs(DRAFT_DIR, exist_ok=True)

# Define a directory for uploaded images
IMAGE_DIR = os.path.join(SAVE_DIR, 'images')
os.makedirs(IMAGE_DIR, exist_ok=True)

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
        'Name': 'Name', 'Date of Visit': 'Date of Visit',
        'Submit': 'Submit', 'Yes': 'Yes', 'No': 'No', 'Download CSV': 'Download CSV',
        'Auto-saved!': 'Auto-saved! You can resume filling the form even if you refresh or lose internet temporarily.',
        'Others': 'Others',
        'Specify Farmer Name': 'Specify Farmer Name (if Others selected)',
        'Upload Photos': 'Upload Photos (Max 3)',
        'Photo uploaded successfully!': 'Photo uploaded successfully!',
        'No photo uploaded.': 'No photo uploaded.',
        'Error uploading photo:': 'Error uploading photo:',
        'Please upload up to 3 photos.': 'Please upload up to 3 photos.'
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
        'Please upload up to 3 photos.': 'कृपया अधिकतम 3 फ़ोटो अपलोड करें।'
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
        'Please upload up to 3 photos.': 'कृपया 3 पर्यंत फोटो अपलोड करा.'
    }
}

# --- Heritage Specific Data
VLCC_NAMES = [
    "3025-K.V.PALLE", "3026-KOTHA PALLE", "3028-BONAMVARIPALLE", "3029-BOMMAICHERUVUPALLI",
    "3030-BADDALAVARIPALLI", "3033-CHINNAGOTTIGALLU", "3034-VODDIPALLE", "3036-MUDUPULAVEMULA",
    "3037-BAYYAREDDYGARIPALLE", "3038-DODDIPALLE", "3040-MARAMREDDYGARIPALLE", "3041-GUTTAPALEM",
    "3042-CHERUVUMUNDARAPALLI", "3044-VARAMPATIVARIPALLE", "3045-ROMPICHERLA", "3046-BANDAKINDAPALLE",
    "3047-MARASANIVARIPALLI", "3024-DEVALAVARIPALLE", "3002-KHAMBAMMITTAPALLE", "3004-MARRIMAKULAPALLE",
    "3005-NAGARIMADUGUVARIPALLE", "3006-KOORAPARTHIVARIPALLE", "3008-IRRIVANDLAPALLE", "3009-PATHEGADA (U.I)",
    "3011-PULICHERLA", "3013-GUDAREVUPALLE", "3014-ENUMALAVARIPALLE", "3015-MUNTHAVANDLAPALLE", "3016-REGALLU",
    "3018-REDDIVARIPALLE", "3019-MAJJIGAVANDLAPALLE", "3020-VENKATADASARAPALLE", "3021-BURRAVANDLAPALLE",
    "3022-KODEKAMBAMVARIPALLI", "3023-SEENAPPAGARIPALLE", "3071-KOTAKADAPALLE", "3072-KOTAKADAPALLE",
    "3074-PODALAKUNTALAPALLE", "3075-SOMALA", "3076-SOMALA", "3077-SOMALA", "3078-CHINNAGOTTIGALLU",
    "3079-MATLOLLPALLAI", "3080-POLIKIMAKULAPALLE", "3081-K.GOLLAPALLE", "3082-CHERUKUVARIPALLE",
    "3083-SODUM", "3084-PILER", "3085-CHERUKUVARIPALLE", "3086-SOMALA", "3087-SODUM", "3088-YERRAVARIPALEM",
    "3089-GUDAREVUPALLE", "3090-SOMALA", "3091-PUTTAVARIPALLE", "3092-VAGALLA", "3048-R.KUMMARA PALLE",
    "3049-HANUMANTHARAYUNIPETA", "3050-CHENCHAMAREDDIGARIPALLE", "3051-BODUMALLUVARIPALLE", "3052-BANDAKINDAPALLE",
    "3055-NAKKALADINNEVODDIPALLE", "3057-KUKKALODDU", "3059-GUNDLAKADAPALLI", "3070-PEDDAPANJANI",
    "3069-PEDDAPALLI", "3068-KADIRAKUNTA", "3067-KOTALA", "3066-VLLIGATLA(U.I)", "3060-BALIREDDIGARIPALLE",
    "3061-SODUM", "3062-GONGIVARIPALLE", "3064-SRINADHAPURAM", "3063-GANGUVARIPALLE", "1664-DEVALAMPETA",
    "1651-YERRAGUNTLAVARIPALLE", "1740-KALIKIRI", "1718-KOTHA PALLE", "1542-HARIJANAWADA", "1937-KAMMAPALLE",
    "1993-T.SANDRAVARIPALLE", "1959-MANCHOORIVARIPALLE", "1812-GANGIREDDIGARIPALLE", "1781-ROMPICHERLA",
    "1773-SREERAMULAVADDIPALLE", "1770-THATIGUNTAPALEM", "1868-ROMPICHERLA", "1824-YERRAGUNTLAVARIPALLE",
    "0884-KOTHAPALLE", "0881-ROMPICHERLA", "0880-MUREVANDLAPALLE", "0878-KALIKIRI", "0876-DIGUVAJUPALLI",
    "0874-KONDAREDDIGARIPALLE", "0871-ROMPICHERLA", "0868-NAGARIMADUGUVARIPALLE", "0863-KHAMBAMMITTAPALLE",
    "0906-REDDIVARIPALLE", "0900-GOLLAPALLE", "0895-PEDDAMALLELA", "0893-PEDDIREDDIGARIPALLE",
    "0888-BANDARALAVARIPALLE", "0887-ELLAMPALLE", "0830-REGALLU", "0826-MUNIREDDIGARIPALLE", "0824-PILER",
    "0859-KRIHSNAREDDIGARIPALLE", "0851-GYARAMPALLE", "0848-ELLAREDDIGARIPALLE", "0846-KURAVAPALLE",
    "0842-PEDDAMALLELA", "0839-BANDAMVARIPALLE", "1058-CHERUKUVARIPALLE", "1057-CHERUKUVARIPALLE",
    "1052-NANJAMPETA", "1017-KHAMBAMVARIPALLE", "1003-PUTTAVANDLAPALLE THANDA", "1272-USTIKAYALAPENTA",
    "1240-MITTAPALLE", "0916-AGRAHARAM", "0915-CHALLAVARIPALLE", "0982-KUCHAMVARIPALLE", "2388-SAGGAMVARI ENDLU",
    "2380-PILER", "2374-PILER", "2437-MARRIMAKULAPALLE", "2421-MATLOLLPALLAI", "2314-KUMMARAPALLE",
    "2338-SETTIPALLEVANDLAPALLE", "2500-KAMMAPALLE", "2530-AVULAPEDDIREDDIGARIPALL", "2528-MARAMREDDIGARIPALLE",
    "2526-AVULAPEDDIREDDIGARIPALL", "2463-BOMMAIAHGARIPALLE", "2444-ROMPICHERLA", "2440-BASIREDDIGARIPALLE",
    "2013-THOTIMALAPALLE", "2083-RAJUVARIPALLI H/W", "2045-RAJUVARIPALLI", "2288-RAJUVARIPALLI",
    "2272-THATIGUNTAPALEM", "2186-KANTAMVARIPALLE", "2183-REGALLU", "2178-SANKENIGUTTAPALLE",
    "2173-MUNELLAPALLE", "2160-V.K.THURPUPALLE", "2228-GAJULAVARIPALLI", "0296-BESTAPALLE",
    "0335-MATLOLLPALLAI", "0326-LOKAVARIPALLE", "0256-VOOTUPALLE", "0245-BETAPALLE", "0237-BATTUVARIPALLE",
    "0417-ROMPICHERLA", "0414-BODIPATIVARIPALLE", "0441-BODIPATIVARIPALLE", "0440-VARANASIVARIPALLE",
    "0360-CHICHILIVARIPALLE", "0357-AKKISANIVARIPALLE", "0394-SETTIPALLEVANDLAPALLE", "0072-VAGALLA",
    "0056-LEMATIVARIPALLE", "0108-KONDAREDDIGARIPALLE", "0016-ROMPICHERLA", "0030-MELLAVARIPALLE",
    "0197-BASIREDDIGARIPALLE", "0173-MORAVAPALLE", "0221-KURABAPALLE", "0130-PATHAKURVAPALLE",
    "0165-AGRAHARAM", "0151-BONAMVARIPALLE", "0649-PILER", "0645-NADIMPALLE", "0643-SAVVALAVARIPALLE",
    "0636-KURAPATHIVARIPALLE", "0689-VANKAVODDIPALLE", "0688-BADDALAVARIPALLI H.W.", "0685-NAGARIMADUGUVARIPALLE",
    "0668-KANDUR", "0663-DEVALAVARIPALLE", "0585-SRIVARAMPURAM", "0575-RAMREDDIGARIPALLE", "0572-LOKAVARIPALLE",
    "0613-NAGAVANDLAPALLI", "0611-BODIPATIVARIPALLE", "0610-ROMPICHERLA", "0604-NAGAVANDLAPALLI",
    "0782-CHICHILIVARIPALLE", "0770-DEVALAVARIPALLE", "0767-PEDDAGOTTIGALLU", "0764-K.V.PALLE",
    "0762-JAGADAMVARIPALLE", "0753-BOLLINANIVARIPALLI", "0813-ROMPICHERLA", "0811-ALAKAMVARIPALLE",
    "0809-KOTAKADAPALLE", "0794-PEDDAGOTTIGALLU", "0793-DIGUVAJUPALLI", "0789-SODUM", "0788-BURUJUPALLE",
    "0786-PEDDAGOTTIGALLU CROSS", "0719-NADIMPALLE", "0718-PEDDAGOTTIGALLU", "0714-BODIPATIVARIPALLE",
    "0709-REDDIVARIPALLE", "0700-RAMIREDDIGARIPALLE", "0721-SODUM", "0747-KURAVAPALLE", "0745-ETUKURIVARIPALLE",
    "0743-ROMPICHERLA", "0736-VOOTUPALLE", "0732-ROMPICHERLA", "0727-DUSSAVANDLA PALLI", "0726-SAVVALAVARIPALLE",
    "0508-MUREVANDLAPALLE", "0490-MATAMPALLE", "0551-TALUPULA", "0512-BONAMVARIPALLE", "0473-KURAVAPALLE",
    "0477-VARANASIVARIPALLE"
]

# Create a dictionary for farmer data (ensure unique keys if possible in real data)
FARMER_DATA = {
    "0005": "KATTARI VASANTA KUMARI",
    "0006": "GUDISI NARAYANAMMA",
    "0007": "P SUREKHA",
    "0008_a": "VAGUMALLU SUDHAKARREDDY", # Renamed to ensure uniqueness if codes are non-unique
    "0015": "VANGUNALLI REDDY SEKHAR REDDY",
    "0017_a": "Y REDDEMMA",
    "0003_a": "INDIRAVATHI MARRIPATTI",
    "0008_b": "CHIKATIPALLI VASANTHA", # Renamed
    "0011": "BIRE LAKSHMI DEVI",
    "0013": "B SAMPURNA",
    "0016": "R PADMA",
    "0017_b": "KRISHTNAMMA KOTAKONDA", # Renamed
    "0018": "A LAKSHMAIAH",
    "0021": "CANDRAKALA GURRAMKONDA",
    "0025": "P JYOTHI",
    "0030": "M KANTHAMMA",
    "0033": "M CHANDRA",
    "0036": "C SURYA PRAKASH",
    "0001": "P SHANKARAMMA",
    "0012_a": "V PRAMEELA",
    "0003_b": "RAJINI KUMAR REDDY M", # Renamed
    "0002_a": "D GOPAL NAIDU",
    "0003_c": "D PRASAD REDDY", # Renamed
    "0006_a": "G RATHNAMMA",
    "0009": "M NARAYANAMMA",
    "0012_b": "V DEVAKI",
    "0026_a": "P HARSHA VARDHAN REDDY",
    "0019_a": "B REDDEMMA",
    "0002_b": "J RAMADEVI",
    "0003_d": "N SIDDAMA",
    "0005_b": "J ESWARAMMA",
    "0006_b": "M SIDDAMMA",
    "0008_c": "Y DEVAKI DEVI",
    "0003_e": "C RAMANAIAH",
    "0014_a": "P REDDY PRASAD",
    "0002_c": "B VARA LAKSHMI",
    "0003_f": "D NAGARJUNA",
    "0001_b": "C USHARANI",
    "0006_c": "S SHAHEEDA BEGUM",
    "0007_b": "S SHAMSHAD",
    "0008_d": "S USHA RANI",
    "0010_a": "V REDDY RANI",
    "0012_c": "A KALAVATHI",
    "0014_b": "S YASHODA",
    "0015_b": "N RESHMA",
    "0016_b": "D RAMADEVI",
    "0017_c": "S SHARMILA",
    "0018_b": "B RANI",
    "0027": "DESIREDDY PALLAVI",
    "0028": "C SREERAMI REDDY",
    "0005_c": "M JYOSHNA",
    "0013_b": "M VENKTRAMAIAH",
    "0002_d": "M BHARGAVI",
    "0006_d": "N GANGAIAH",
    "0009_b": "N PURUSHOTHAM",
    "0011_b": "N RAMADEVI",
    "0017_d": "Y LAKSHMI",
    "0026_b": "N SRINIVASULU",
    "0027_b": "N LAVANYA",
    "0002_e": "B MURALI",
    "0014_c": "S MUBARAK ALI",
    "0015_c": "S SABEEN TAJ",
    "0019_b": "D NARASAMMA",
    "0020": "V RANI",
    "0001_c": "A RAJAMMA",
    "0006_e": "D SURENDRA REDDY",
    "0008_e": "M VISHNUVARDHAN REDDY",
    "0010_b": "K SAHADEVA",
    "0002_f": "D ASHOK KUMAR",
    "0014_d": "K VENKATRAMAIAH",
    "0006_f": "K RAJAMMA",
    "0008_f": "P ANASUYA",
    "0010_c": "P RAJAMMA",
    "0012_d": "P SAHADEVAREDDY",
    "0015_d": "P BHARATHAMMA",
    "0017_e": "S GOWRAMMA",
    "0008_g": "V PADMAJA",
    "0010_d": "V CHITTEMMA",
    "0017_f": "B GIRI BABU",
    "0019_c": "P MOHAN BABU",
    "0002_g": "SREENIVASULU",
    "0012_e": "C NARSAMMA",
    "0004": "A CHANDRAMMA",
    "0014_e": "G RAMNJULU",
    "0018_c": "P SYAMALAMMA",
    "0019_d": "K BHARGAVI",
    "0012_f": "M LAKSHMIDEVI",
    "0013_c": "K MALLESWARI",
    "0016_c": "M YERRAKKA",
    "0017_g": "V GANGADEVI",
    "0021_b": "M CHANDRAMMA"
}

# Create lists for dropdowns
FARMER_CODES = sorted(list(FARMER_DATA.keys())) if FARMER_DATA else []
FARMER_NAMES_ORIGINAL = sorted(list(FARMER_DATA.values())) if FARMER_DATA else []

GREEN_FODDER_OPTIONS = ["Napier", "Maize", "Sorghum"]
DRY_FODDER_OPTIONS = ["Paddy Straw", "Maize Straw", "Ragi Straw", "Ground Nut Crop Residues"]
PELLET_FEED_BRANDS = ["Heritage Milk Rich", "Heritage Milk Joy", "Heritage Power Plus", "Kamadhenu", "Godrej", "Sreeja", "Vallabha-Panchamruth", "Vallabha-Subham Pusti"]
MINERAL_MIXTURE_BRANDS = ["Herita Vit", "Herita Min", "Other (Specify)"]
WATER_SOURCE_OPTIONS = ["Panchayat", "Borewell", "Water Streams"]
SURVEYOR_NAMES = ["Shiva Shankaraiah", "Reddisekhar", "Balakrishna", "Somasekhar", "Mahesh Kumar", "Dr Swaran Raj Nayak", "Ram Prasad", "K Balaji"]

# Define initial_values_defaults at the global scope
initial_values_defaults = {
    'lang_select': "English",
    'vlcc_name': VLCC_NAMES[0] if VLCC_NAMES else None,
    'hpc_code': '',
    'types': "HPC",
    'farmer_name_selected': FARMER_NAMES_ORIGINAL[0] if FARMER_NAMES_ORIGINAL else 'Others',
    'farmer_name_other': '',
    'farmer_code': FARMER_CODES[0] if FARMER_CODES else None,
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
    'uploaded_photo_paths': [] # To store paths of uploaded photos
}

# Function to save current form data to a draft file
def save_draft():
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    draft_data = {key: st.session_state.get(key, initial_values_defaults.get(key)) for key in initial_values_defaults.keys()}
    
    # Convert datetime.date objects to string for JSON serialization
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

            for key, value in loaded_data.items():
                if key == 'visit_date' and isinstance(value, str):
                    try:
                        st.session_state[key] = datetime.date.fromisoformat(value)
                    except ValueError:
                        st.session_state[key] = initial_values_defaults.get(key, datetime.date.today())
                elif key in ['green_fodder_types', 'dry_fodder_types', 'pellet_feed_brands', 'water_sources', 'uploaded_photo_paths']:
                    st.session_state[key] = list(value) if isinstance(value, list) else []
                else:
                    st.session_state[key] = value
            
            # --- VALIDATE VLCC_NAME AFTER LOADING DRAFT ---
            if 'vlcc_name' in st.session_state and st.session_state['vlcc_name'] not in VLCC_NAMES:
                st.session_state['vlcc_name'] = VLCC_NAMES[0] if VLCC_NAMES else None
            
            # Re-validate other dropdown selections based on current language
            current_labels = dict_translations.get(st.session_state.get('lang_select', 'English'), dict_translations['English'])
            
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
            st.error(f"Error loading draft: {e}")
            return False
    return False

# Initialize session state for the first time or load draft
if 'app_initialized_flag' not in st.session_state:
    st.session_state.app_initialized_flag = True
    st.session_state.last_saved_time_persistent = None
    
    # Initialize all defaults first
    for key, default_value in initial_values_defaults.items():
        if key not in st.session_state: # Only set if not already present from a previous, possibly invalid, run
            st.session_state[key] = default_value
    
    # Then try to load draft, which will overwrite defaults if successful and valid
    load_draft()

# Language Selection
initial_lang_options = ("English", "Hindi", "Marathi")
# Ensure the selected language is always one of the valid options
if st.session_state.lang_select not in initial_lang_options:
    st.session_state.lang_select = "English" # Default to English if invalid
initial_lang_index = initial_lang_options.index(st.session_state.lang_select)

lang = st.selectbox(
    "Language / भाषा / भाषा",
    initial_lang_options,
    index=initial_lang_index,
    key="lang_select",
)
labels = dict_translations.get(lang, dict_translations['English'])

# Title
st.title(labels['Farmer Profile'])

# Display auto-save status
if st.session_state.last_saved_time_persistent:
    st.info(f"{labels['Auto-saved!']} Last saved: {st.session_state.last_saved_time_persistent}")
else:
    st.info("No auto-saved draft found, or draft cleared. Start filling the form!")

# Form Start
with st.form("survey_form"):
    st.header(labels['Farmer Profile'])

    # VLCC Name - No direct modification to st.session_state.vlcc_name here
    # The validation is done in load_draft() or initial setup
    vlcc_name_default_idx = 0
    if st.session_state.vlcc_name in VLCC_NAMES:
        vlcc_name_default_idx = VLCC_NAMES.index(st.session_state.vlcc_name)
    elif VLCC_NAMES: # Fallback if session state is still somehow invalid, but not modifying session_state directly
        vlcc_name_default_idx = 0 # Default to first valid option for display purposes

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
    types_default_idx = 0
    if st.session_state.types in types_options:
        types_default_idx = types_options.index(st.session_state.types)
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
    elif farmer_names_with_others: # Fallback for display
        farmer_name_default_idx = 0
    else:
        # If no farmer names, set to None for display but don't modify session state
        pass # st.session_state.farmer_name_selected should be handled in initial setup

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
    elif FARMER_CODES: # Fallback for display
        farmer_code_default_idx = 0
    else:
        pass # st.session_state.farmer_code should be handled in initial setup

    farmer_code = st.selectbox(
        labels['Farmer Code'], options=FARMER_CODES,
        index=farmer_code_default_idx,
        key="farmer_code",
        disabled=(not FARMER_CODES)
    )

    # Gender
    gender_options = (labels['Male'], labels['Female'])
    gender_default_idx = 0
    if st.session_state.gender in gender_options:
        gender_default_idx = gender_options.index(st.session_state.gender)
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

    cattle_in_milk = st.number_input(
        labels['No. of Cattle in Milk'], min_value=0,
        value=int(st.session_state.cattle_in_milk),
        key="cattle_in_milk"
    )
    calves = st.number_input(
        labels['No. of Calves/Heifers'], min_value=0,
        value=int(st.session_state.calves),
        key="calves"
    )
    desi_cows = st.number_input(
        labels['No. of Desi cows'], min_value=0,
        value=int(st.session_state.desi_cows),
        key="desi_cows"
    )
    crossbreed_cows = st.number_input(
        labels['No. of Cross breed cows'], min_value=0,
        value=int(st.session_state.crossbreed_cows),
        key="crossbreed_cows"
    )
    buffalo = st.number_input(
        labels['No. of Buffalo'], min_value=0,
        value=int(st.session_state.buffalo),
        key="buffalo"
    )
    milk_production = st.number_input(
        labels['Milk Production'], min_value=0.0, format="%.2f",
        value=float(st.session_state.milk_production),
        key="milk_production"
    )

    st.header(labels['Specific Questions'])
    green_fodder_options = (labels['Yes'], labels['No'])
    green_fodder_default_idx = 0
    if st.session_state.green_fodder in green_fodder_options:
        green_fodder_default_idx = green_fodder_options.index(st.session_state.green_fodder)
    green_fodder = st.radio(
        labels['Green Fodder'], green_fodder_options,
        index=green_fodder_default_idx,
        key="green_fodder"
    )
    if green_fodder == labels['Yes']:
        green_fodder_types = st.multiselect(
            labels['Type of Green Fodder'], GREEN_FODDER_OPTIONS,
            default=st.session_state.green_fodder_types,
            key="green_fodder_types"
        )
        green_fodder_qty = st.number_input(
            labels['Quantity of Green Fodder'], min_value=0.0, format="%.2f",
            value=float(st.session_state.green_fodder_qty),
            key="green_fodder_qty"
        )
    else:
        # Clear associated session state values when "No" is selected
        st.session_state.green_fodder_types = []
        st.session_state.green_fodder_qty = 0.0
        green_fodder_types = [] # For data collection
        green_fodder_qty = 0.0 # For data collection

    dry_fodder_options = (labels['Yes'], labels['No'])
    dry_fodder_default_idx = 0
    if st.session_state.dry_fodder in dry_fodder_options:
        dry_fodder_default_idx = dry_fodder_options.index(st.session_state.dry_fodder)
    dry_fodder = st.radio(
        labels['Dry Fodder'], dry_fodder_options,
        index=dry_fodder_default_idx,
        key="dry_fodder"
    )
    if dry_fodder == labels['Yes']:
        dry_fodder_types = st.multiselect(
            labels['Type of Dry Fodder'], DRY_FODDER_OPTIONS,
            default=st.session_state.dry_fodder_types,
            key="dry_fodder_types"
        )
        dry_fodder_qty = st.number_input(
            labels['Quantity of Dry Fodder'], min_value=0.0, format="%.2f",
            value=float(st.session_state.dry_fodder_qty),
            key="dry_fodder_qty"
        )
    else:
        st.session_state.dry_fodder_types = []
        st.session_state.dry_fodder_qty = 0.0
        dry_fodder_types = []
        dry_fodder_qty = 0.0

    pellet_feed_options = (labels['Yes'], labels['No'])
    pellet_feed_default_idx = 0
    if st.session_state.pellet_feed in pellet_feed_options:
        pellet_feed_default_idx = pellet_feed_options.index(st.session_state.pellet_feed)
    pellet_feed = st.radio(
        labels['Pellet Feed'], pellet_feed_options,
        index=pellet_feed_default_idx,
        key="pellet_feed"
    )
    if pellet_feed == labels['Yes']:
        pellet_feed_brands = st.multiselect(
            labels['Pellet Feed Brand'], PELLET_FEED_BRANDS,
            default=st.session_state.pellet_feed_brands,
            key="pellet_feed_brands"
        )
        pellet_feed_qty = st.number_input(
            labels['Quantity of Pellet Feed'], min_value=0.0, format="%.2f",
            value=float(st.session_state.pellet_feed_qty),
            key="pellet_feed_qty"
        )
    else:
        st.session_state.pellet_feed_brands = []
        st.session_state.pellet_feed_qty = 0.0
        pellet_feed_brands = []
        pellet_feed_qty = 0.0

    mineral_mixture_options = (labels['Yes'], labels['No'])
    mineral_mixture_default_idx = 0
    if st.session_state.mineral_mixture in mineral_mixture_options:
        mineral_mixture_default_idx = mineral_mixture_options.index(st.session_state.mineral_mixture)
    mineral_mixture = st.radio(
        labels['Mineral Mixture'], mineral_mixture_options,
        index=mineral_mixture_default_idx,
        key="mineral_mixture"
    )
    if mineral_mixture == labels['Yes']:
        mineral_brand_default_idx = 0
        if st.session_state.mineral_brand in MINERAL_MIXTURE_BRANDS:
            mineral_brand_default_idx = MINERAL_MIXTURE_BRANDS.index(st.session_state.mineral_brand)
        mineral_brand = st.selectbox(
            labels['Mineral Mixture Brand'], MINERAL_MIXTURE_BRANDS,
            index=mineral_brand_default_idx,
            key="mineral_brand"
        )
        mineral_qty = st.number_input(
            labels['Quantity of Mineral Mixture'], min_value=0.0, format="%.2f",
            value=float(st.session_state.mineral_qty),
            key="mineral_qty"
        )
    else:
        st.session_state.mineral_brand = MINERAL_MIXTURE_BRANDS[0] if MINERAL_MIXTURE_BRANDS else "" # Ensure a string or None
        st.session_state.mineral_qty = 0.0
        mineral_brand = ""
        mineral_qty = 0.0

    silage_options = (labels['Yes'], labels['No'])
    silage_default_idx = 0
    if st.session_state.silage in silage_options:
        silage_default_idx = silage_options.index(st.session_state.silage)
    silage = st.radio(
        labels['Silage'], silage_options,
        index=silage_default_idx,
        key="silage"
    )
    if silage == labels['Yes']:
        silage_source = st.text_input(
            labels['Source and Price of Silage'],
            value=st.session_state.silage_source,
            key="silage_source"
        )
        silage_qty = st.number_input(
            labels['Quantity of Silage'], min_value=0.0, format="%.2f",
            value=float(st.session_state.silage_qty),
            key="silage_qty"
        )
    else:
        st.session_state.silage_source = ""
        st.session_state.silage_qty = 0.0
        silage_source = ""
        silage_qty = 0.0

    water_sources = st.multiselect(
        labels['Source of Water'], WATER_SOURCE_OPTIONS,
        default=st.session_state.water_sources,
        key="water_sources"
    )

    # --- Photo Upload Snippet ---
    st.header(labels['Upload Photos'])
    uploaded_files = st.file_uploader(
        labels['Upload Photos'],
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="image_uploader"
    )

    # Display existing photos in the draft if any
    if st.session_state.uploaded_photo_paths:
        st.subheader("Currently uploaded photos (Draft):")
        cols = st.columns(3)
        for i, photo_path in enumerate(st.session_state.uploaded_photo_paths):
            if os.path.exists(photo_path):
                try:
                    with open(photo_path, "rb") as f:
                        encoded_string = base64.b64encode(f.read()).decode()
                        cols[i % 3].image(f"data:image/png;base64,{encoded_string}", use_column_width=True)
                        cols[i % 3].caption(os.path.basename(photo_path))
                except Exception as e:
                    cols[i % 3].error(f"Could not load image {os.path.basename(photo_path)}: {e}")
            else:
                st.warning(f"Draft photo path not found: {photo_path}. It might have been moved or deleted.")

    # Process new uploads
    if uploaded_files:
        # Limit to 3 files if more are uploaded
        if len(uploaded_files) > 3:
            st.warning(labels['Please upload up to 3 photos.'])
            uploaded_files = uploaded_files[:3] # Take only the first 3

        # Clear existing paths and save new ones
        # This part should probably be moved to a callback function if you want to avoid re-upload on every rerun
        # For now, it's inside the form, meaning it will re-process on submit.
        # However, the key "image_uploader" will retain the uploaded files until the form is cleared/reset.
        # This is where the photo path handling needs to be careful to not overwrite too eagerly.
        # Let's refine this to append/manage.
        
        # New: If there are new files, append them to the session state list, respecting the limit.
        for uploaded_file in uploaded_files:
            try:
                # Check if this file has already been processed in the current form instance
                # This is a simple check, more robust might involve hashing content.
                if any(uploaded_file.name in path for path in st.session_state.uploaded_photo_paths):
                    continue # Skip if already in the list

                # Create a unique filename for the uploaded image
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") # Add microseconds for higher uniqueness
                file_extension = uploaded_file.name.split('.')[-1]
                unique_filename = f"{timestamp}_{uploaded_file.name.replace(' ', '_')}"
                photo_path = os.path.join(IMAGE_DIR, unique_filename)

                with open(photo_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Add to session state only if we are within the limit
                if len(st.session_state.uploaded_photo_paths) < 3:
                    st.session_state.uploaded_photo_paths.append(photo_path)
                    st.success(f"{labels['Photo uploaded successfully!']} {uploaded_file.name}")
                else:
                    st.warning(f"Skipping {uploaded_file.name}: {labels['Please upload up to 3 photos.']}")
                    # Optionally remove the newly saved file if it exceeds the limit immediately
                    os.remove(photo_path) # Clean up the excess file
            except Exception as e:
                st.error(f"{labels['Error uploading photo:']} {uploaded_file.name}. {e}")
    else:
        if not st.session_state.uploaded_photo_paths:
            st.info(labels['No photo uploaded.'])


    st.header("Survey Details")
    surveyor_name_default_idx = 0
    if st.session_state.surveyor_name in SURVEYOR_NAMES:
        surveyor_name_default_idx = SURVEYOR_NAMES.index(st.session_state.surveyor_name)
    surveyor_name = st.selectbox(
        labels['Name'], SURVEYOR_NAMES,
        index=surveyor_name_default_idx,
        key="surveyor_name"
    )
    
    # Ensure visit_date is a datetime.date object before passing to st.date_input
    if not isinstance(st.session_state.visit_date, datetime.date):
        st.session_state.visit_date = datetime.date.today()

    visit_date = st.date_input(
        labels['Date of Visit'],
        value=st.session_state.visit_date,
        key="visit_date"
    )

    # --- Submit Button ---
    submitted = st.form_submit_button(labels['Submit'])

    if submitted:
        # Determine the final farmer name based on selection
        final_farmer_name = farmer_name_other if farmer_name_selected == labels['Others'] else farmer_name_selected

        # Collect all data for submission
        data = {
            "Language": lang,
            "VLCC Name": vlcc_name,
            "HPC/MCC Code": hpc_code,
            "Type": types,
            "Farmer Name": final_farmer_name,
            "Farmer Code / Pourer ID": farmer_code,
            "Gender": gender,
            "Number of Cows": cows,
            "No. of Cattle in Milk": cattle_in_milk,
            "No. of Calves/Heifers": calves,
            "No. of Desi cows": desi_cows,
            "No. of Cross breed cows": crossbreed_cows,
            "No. of Buffalo": buffalo,
            "Milk Production (liters/day)": milk_production,
            "Green Fodder Provided": green_fodder,
            "Type of Green Fodder": ", ".join(green_fodder_types) if green_fodder == labels['Yes'] else "",
            "Quantity of Green Fodder (Kg/day)": green_fodder_qty if green_fodder == labels['Yes'] else 0.0,
            "Dry Fodder Provided": dry_fodder,
            "Type of Dry Fodder": ", ".join(dry_fodder_types) if dry_fodder == labels['Yes'] else "",
            "Quantity of Dry Fodder (Kg/day)": dry_fodder_qty if dry_fodder == labels['Yes'] else 0.0,
            "Pellet Feed Provided": pellet_feed,
            "Pellet Feed Brand": ", ".join(pellet_feed_brands) if pellet_feed == labels['Yes'] else "",
            "Quantity of Pellet Feed (Kg/day)": pellet_feed_qty if pellet_feed == labels['Yes'] else 0.0,
            "Mineral Mixture Provided": mineral_mixture,
            "Mineral Mixture Brand": mineral_brand if mineral_mixture == labels['Yes'] else "",
            "Quantity of Mineral Mixture (gm/day)": mineral_qty if mineral_mixture == labels['Yes'] else 0.0,
            "Silage Provided": silage,
            "Source and Price of Silage": silage_source if silage == labels['Yes'] else "",
            "Quantity of Silage (Kg/day)": silage_qty if silage == labels['Yes'] else 0.0,
            "Source of Water": ", ".join(water_sources),
            "Name of Surveyor": surveyor_name,
            "Date of Visit": visit_date.isoformat(), # ISO format for consistent saving
            "Photo Paths": ", ".join(st.session_state.uploaded_photo_paths) # Save photo paths
        }

        # Convert to DataFrame and save
        df = pd.DataFrame([data])

        # Define filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SAVE_DIR, f"survey_response_{timestamp}.csv")

        # Save to CSV
        try:
            # Append to file if it exists, otherwise create it
            if not os.path.exists(file_path):
                df.to_csv(file_path, index=False)
            else:
                df.to_csv(file_path, mode='a', header=False, index=False)
            st.success("Survey data submitted successfully!")

            # --- CORRECTED RESET LOGIC ---
            # Instead of setting st.session_state values directly for widgets already instantiated,
            # clear the relevant keys from session_state. When rerun, they will get their
            # default values from initial_values_defaults.
            for key in initial_values_defaults.keys():
                if key != 'lang_select' and key != 'app_initialized_flag' and key != 'last_saved_time_persistent':
                    if key in st.session_state: # Only delete if it exists
                        del st.session_state[key]

            # Remove the draft file after successful submission
            draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
            if os.path.exists(draft_filename):
                os.remove(draft_filename)
                st.session_state.last_saved_time_persistent = None # Clear auto-save message

            st.rerun() # Rerun to clear the form fields and update display
        except Exception as e:
            st.error(f"Error saving data: {e}")

# Function to load all saved CSVs and display them
def load_all_survey_data():
    all_files = [os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR) if f.endswith('.csv')]
    if not all_files:
        return pd.DataFrame()
    
    # Filter out draft files if any CSVs named like drafts exist in SAVE_DIR
    survey_files = [f for f in all_files if not "draft" in f]

    if not survey_files:
        return pd.DataFrame()

    list_df = []
    for file in survey_files:
        try:
            df = pd.read_csv(file)
            list_df.append(df)
        except pd.errors.EmptyDataError:
            st.warning(f"Skipping empty file: {file}")
            continue
        except Exception as e:
            st.error(f"Error reading {file}: {e}")
            continue

    if list_df:
        return pd.concat(list_df, ignore_index=True)
    return pd.DataFrame()

# Download Button for all collected data
st.markdown("---")
if st.button(labels['Download CSV']):
    all_data_df = load_all_survey_data()
    if not all_data_df.empty:
        # Use a BytesIO object to create a CSV in memory for download
        csv_buffer = all_data_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Click to Download Data",
            data=csv_buffer,
            file_name="all_dairy_survey_data.csv",
            mime="text/csv",
            key="download_all_csv"
        )
    else:
        st.info("No survey data collected yet to download.")
