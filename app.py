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

# Parse the provided farmer data
farmer_data_raw = """
S No.	Year	HPC Code	HPC Name	Member Code	Rep ID	Farmer Name	Average of SNF	Slabs
1	Feb-25	3028	HPC-BONAMVARI PALLI	0008	9300033214	C VIJAYAKUMARI	8.02	Slab 5
2	Feb-25	3028	HPC-BONAMVARI PALLI	0013	9300040221	SHAIK SUBAHAN ALI	7.86	Slab 5
3	Feb-25	3028	HPC-BONAMVARI PALLI	0015	9300072079	V NIRMALA	7.87	Slab 5
4	Feb-25	3028	HPC-BONAMVARI PALLI	0016	9300125159	BHAGYAMMA NAGISETTI	7.94	Slab 5
5	Feb-25	3029	HPC-BOMMAICHERUVU PALLI	0005	9300032616	K JAYALAKSHMI	7.84	Slab 5
6	Feb-25	3029	HPC-BOMMAICHERUVU PALLI	0009	9300132054	K MOHAN REDDY	7.93	Slab 5
7	Feb-25	3030	HPC-BADDALAVARI PALLI	0005	9300033766	KATTARI VASANTA KUMARI	7.94	Slab 5
8	Feb-25	3030	HPC-BADDALAVARI PALLI	0006	9300033767	GUDISI NARAYANAMMA	7.85	Slab 5
9	Feb-25	3030	HPC-BADDALAVARI PALLI	0007	9300033768	P SUREKHA	7.90	Slab 5
10	Feb-25	3030	HPC-BADDALAVARI PALLI	0008	9300033769	VAGUMALLU SUDHAKARREDDY	7.89	Slab 5
11	Feb-25	3030	HPC-BADDALAVARI PALLI	0015	9300033777	VANGUNALLI REDDY SEKHAR REDDY	7.83	Slab 5
12	Feb-25	3030	HPC-BADDALAVARI PALLI	0017	9300047283	Y REDDEMMA	7.90	Slab 5
13	Feb-25	3033	HPC-CHINNAGOTTIGALLU	0002	9300037634	PARVATHA REDDY SHOBARANI	8.02	Slab 5
14	Feb-25	3033	HPC-CHINNAGOTTIGALLU	0009	9300043625	NAGESWARA RAO YALAKATURI	7.94	Slab 5
15	Feb-25	3034	HPC-T VADDI PALLI	0001	9300038197	SUMATHI KOTAKONDA	7.84	Slab 5
16	Feb-25	3034	HPC-T VADDI PALLI	0003	9300038203	INDIRAVATHI MARRIPATTI	7.86	Slab 5
17	Feb-25	3034	HPC-T VADDI PALLI	0008	9300038217	CHIKATIPALLI VASANTHA	7.86	Slab 5
18	Feb-25	3034	HPC-T VADDI PALLI	0011	9300038221	BIRE LAKSHMI DEVI	7.92	Slab 5
19	Feb-25	3034	HPC-T VADDI PALLI	0013	9300038387	B SAMPURNA	7.84	Slab 5
20	Feb-25	3034	HPC-T VADDI PALLI	0016	9300038393	R PADMA	7.87	Slab 5
21	Feb-25	3034	HPC-T VADDI PALLI	0017	9300038394	KRISHTNAMMA KOTAKONDA	7.84	Slab 5
22	Feb-25	3034	HPC-T VADDI PALLI	0018	9300038395	A LAKSHMAIAH	7.97	Slab 5
23	Feb-25	3034	HPC-T VADDI PALLI	0019	9300038401	NAGAIAH BANDARLA	7.85	Slab 5
24	Feb-25	3034	HPC-T VADDI PALLI	0021	9300038404	CANDRAKALA GURRAMKONDA	7.84	Slab 5
25	Feb-25	3034	HPC-T VADDI PALLI	0023	9300038406	P ARUNA KUMARI	7.84	Slab 5
26	Feb-25	3034	HPC-T VADDI PALLI	0025	9300038414	P JYOTHI	7.84	Slab 5
27	Feb-25	3034	HPC-T VADDI PALLI	0030	9300045445	M KANTHAMMA	8.03	Slab 5
28	Feb-25	3034	HPC-T VADDI PALLI	0033	9300052308	M CHANDRA	8.00	Slab 5
29	Feb-25	3034	HPC-T VADDI PALLI	0036	9300079673	C SURYA PRAKASH	8.04	Slab 5
30	Feb-25	3036	HPC-MUDUPULAVEMULA KASPA	0001	9300040026	P SHANKARAMMA	7.88	Slab 5
31	Feb-25	3036	HPC-MUDUPULAVEMULA KASPA	0006	9300040032	P CHINNAREDDEMMA	7.99	Slab 5
32	Feb-25	3036	HPC-MUDUPULAVEMULA KASPA	0008	9300040037	G KUMARI	7.80	Slab 5
33	Feb-25	3036	HPC-MUDUPULAVEMULA KASPA	0015	9300051935	P CHANDRA	7.80	Slab 5
34	Feb-25	3037	HPC-BAYYAREDDYGARI PALLI	0004	9300040058	NASROON VAJRALA	7.88	Slab 5
35	Feb-25	3037	HPC-BAYYAREDDYGARI PALLI	0008	9300040068	NAGARATHNAMNAIDU G	8.02	Slab 5
36	Feb-25	3037	HPC-BAYYAREDDYGARI PALLI	0009	9300053795	G CHANDRASEKHAR  NAIDU	7.86	Slab 5
37	Feb-25	3037	HPC-BAYYAREDDYGARI PALLI	0010	9300054152	G SREENIVASULU NAIDU	7.88	Slab 5
38	Feb-25	3037	HPC-BAYYAREDDYGARI PALLI	0012	9300125591	V PRAMEELA	7.99	Slab 5
39	Feb-25	3037	HPC-BAYYAREDDYGARI PALLI	0013	9300142882	VEMPALLI LAKSHMI DEVI	7.99	Slab 5
40	Feb-25	3038	HPC-THUMMALAVARI PALLI	0002	9300040310	RUKMANAMMA KAMBAM	8.09	Slab 5
41	Feb-25	3038	HPC-THUMMALAVARI PALLI	0003	9300040311	RAJINI KUMAR REDDY M	7.96	Slab 5
42	Feb-25	3038	HPC-THUMMALAVARI PALLI	0008	9300041910	D ANITHA	8.02	Slab 5
43	Feb-25	3038	HPC-THUMMALAVARI PALLI	0011	9300046454	M KAMALAMMA	8.01	Slab 5
44	Feb-25	3038	HPC-THUMMALAVARI PALLI	0016	9300086100	V AMRUTHA	8.02	Slab 5
45	Feb-25	3038	HPC-THUMMALAVARI PALLI	0017	9300089778	V BALA RAJU	8.00	Slab 5
46	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0002	9300046466	D GOPAL NAIDU	8.00	Slab 5
47	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0003	9300046468	D PRASAD REDDY	8.07	Slab 5
48	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0004	9300046469	D SRAVANTHI	7.83	Slab 5
49	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0006	9300046471	G RATHNAMMA	7.88	Slab 5
50	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0007	9300046473	G VIJAYA LAKSHRNI	7.85	Slab 5
51	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0009	9300046475	M NARAYANAMMA	7.85	Slab 5
52	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0012	9300046478	V DEVAKI	7.88	Slab 5
53	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0013	9300045920	C JYOTHI	7.98	Slab 5
54	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0015	9300047549	D KUMARI	7.86	Slab 5
55	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0016	9300047550	G JYOTHI	8.01	Slab 5
56	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0017	9300047551	K ERRAMMA	7.83	Slab 5
57	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0018	9300047673	A PRAMEELAMMA	7.85	Slab 5
58	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0019	9300047674	C MANJULA	7.84	Slab 5
59	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0025	9300089776	O VASUNDARAMMA	7.83	Slab 5
60	Feb-25	3040	HPC-MARAMREDDYGARI PALLI	0026	9300093113	P HARSHA VARDHAN REDDY	7.97	Slab 5
61	Feb-25	3041	HPC-C BARINE PALLI	0001	9300047676	B ADILAKSHMI	8.04	Slab 5
62	Feb-25	3041	HPC-C BARINE PALLI	0003	9300047678	B BHAGYAMMA(B YARRAPPA)	7.97	Slab 5
63	Feb-25	3041	HPC-C BARINE PALLI	0004	9300047679	B GOWTAMI	7.99	Slab 5
64	Feb-25	3041	HPC-C BARINE PALLI	0007	9300047682	B NAGARATHNAMMA	8.05	Slab 5
65	Feb-25	3041	HPC-C BARINE PALLI	0009	9300047684	B RAMACHANDRA	8.03	Slab 5
66	Feb-25	3041	HPC-C BARINE PALLI	0011	9300047686	B SHOBARANI	7.93	Slab 5
67	Feb-25	3041	HPC-C BARINE PALLI	0015	9300047690	Y HARI	7.96	Slab 5
68	Feb-25	3041	HPC-C BARINE PALLI	0016	9300048698	B DHANA LAKSHMI	7.96	Slab 5
69	Feb-25	3041	HPC-C BARINE PALLI	0018	9300048700	B NEELAVATHI	7.97	Slab 5
70	Feb-25	3041	HPC-C BARINE PALLI	0019	9300048701	B REDDEMMA	8.07	Slab 5
71	Feb-25	3041	HPC-C BARINE PALLI	0020	9300048702	C RAMANAIAH	7.91	Slab 5
72	Feb-25	3041	HPC-C BARINE PALLI	0021	9300048703	B NAGARAJA S/O B P VENKATADRI	8.07	Slab 5
73	Feb-25	3041	HPC-C BARINE PALLI	0022	9300049458	K SUMITHRA	7.98	Slab 5
74	Feb-25	3042	HPC-CHERUVUMUDARA PALLI	0002	9300047692	J RAMADEVI	7.89	Slab 5
75	Feb-25	3042	HPC-CHERUVUMUDARA PALLI	0003	9300047693	N SIDDAMA	7.88	Slab 5
76	Feb-25	3042	HPC-CHERUVUMUDARA PALLI	0005	9300047954	J ESWARAMMA	7.98	Slab 5
77	Feb-25	3042	HPC-CHERUVUMUDARA PALLI	0006	9300047956	M SIDDAMMA	7.83	Slab 5
78	Feb-25	3042	HPC-CHERUVUMUDARA PALLI	0008	9300047958	Y DEVAKI DEVI	7.96	Slab 5
79	Feb-25	3044	HPC-MARAMPATIVARI PALLI	0003	9300053798	C RAMANAIAH	8.03	Slab 5
80	Feb-25	3044	HPC-MARAMPATIVARI PALLI	0009	9300085869	M SUJATHA	8.09	Slab 5
81	Feb-25	3044	HPC-MARAMPATIVARI PALLI	0014	9300128266	P REDDY PRASAD	8.04	Slab 5
82	Feb-25	3045	HPC-DADDLAVARI PALLI	0001	9300050572	B BALAKRISHNA	7.91	Slab 5
83	Feb-25	3045	HPC-DADDLAVARI PALLI	0002	9300050574	B VARA LAKSHMI	7.94	Slab 5
84	Feb-25	3045	HPC-DADDLAVARI PALLI	0003	9300050575	D NAGARJUNA	7.94	Slab 5
85	Feb-25	3045	HPC-DADDLAVARI PALLI	0008	9300054153	B. AMARANATH	7.88	Slab 5
86	Feb-25	3045	HPC-DADDLAVARI PALLI	0010	9300077783	B PAVANI	7.94	Slab 5
87	Feb-25	3045	HPC-DADDLAVARI PALLI	0017	9300101162	KIRAN VANKITALA	8.04	Slab 5
88	Feb-25	3045	HPC-DADDLAVARI PALLI	0019	9300140619	K LATHA	7.96	Slab 5
89	Feb-25	3046	HPC-BANDAKINDA PALLI	0001	9300052622	C USHARANI	7.87	Slab 5
90	Feb-25	3046	HPC-BANDAKINDA PALLI	0002	9300052628	C YARAM REDDY	7.80	Slab 5
91	Feb-25	3046	HPC-BANDAKINDA PALLI	0006	9300052635	S SHAHEEDA BEGUM	7.83	Slab 5
92	Feb-25	3046	HPC-BANDAKINDA PALLI	0007	9300052636	S SHAMSHAD	7.86	Slab 5
93	Feb-25	3046	HPC-BANDAKINDA PALLI	0008	9300052642	S USHA RANI	7.84	Slab 5
94	Feb-25	3046	HPC-BANDAKINDA PALLI	0010	9300053027	V REDDY RANI	7.96	Slab 5
95	Feb-25	3046	HPC-BANDAKINDA PALLI	0012	9300056866	A KALAVATHI	8.01	Slab 5
96	Feb-25	3046	HPC-BANDAKINDA PALLI	0014	9300061773	S YASHODA	7.94	Slab 5
97	Feb-25	3046	HPC-BANDAKINDA PALLI	0015	9300064805	N RESHMA	7.87	Slab 5
98	Feb-25	3046	HPC-BANDAKINDA PALLI	0016	9300066824	D RAMADEVI	8.08	Slab 5
99	Feb-25	3046	HPC-BANDAKINDA PALLI	0017	9300067375	S SHARMILA	7.87	Slab 5
100	Feb-25	3046	HPC-BANDAKINDA PALLI	0018	9300071975	B RANI	7.88	Slab 5
101	Feb-25	3046	HPC-BANDAKINDA PALLI	0022	9300072084	MASTHAN SAHEB  SHAIK	7.90	Slab 5
102	Feb-25	3046	HPC-BANDAKINDA PALLI	0027	9300081856	DESIREDDY PALLAVI	8.00	Slab 5
103	Feb-25	3046	HPC-BANDAKINDA PALLI	0028	9300085867	C SREERAMI REDDY	7.88	Slab 5
104	Feb-25	3047	HPC-MARASANIVARI PALLI	0001	9300053644	A RADHA	7.91	Slab 5
105	Feb-25	3047	HPC-MARASANIVARI PALLI	0002	9300053645	K CHINNAKKA	7.87	Slab 5
106	Feb-25	3047	HPC-MARASANIVARI PALLI	0003	9300053646	K GOWRAMMA	7.88	Slab 5
107	Feb-25	3047	HPC-MARASANIVARI PALLI	0004	9300053647	M ANANDHA	7.92	Slab 5
108	Feb-25	3047	HPC-MARASANIVARI PALLI	0005	9300053648	M JYOSHNA	7.91	Slab 5
109	Feb-25	3047	HPC-MARASANIVARI PALLI	0006	9300053649	M SUDARSAN REDDY	8.08	Slab 5
110	Feb-25	3047	HPC-MARASANIVARI PALLI	0007	9300053650	M VENKATRAMAIAH	7.95	Slab 5
111	Feb-25	3047	HPC-MARASANIVARI PALLI	0012	9300054156	M YARRAMMA	8.05	Slab 5
112	Feb-25	3047	HPC-MARASANIVARI PALLI	0013	9300055109	M VENKTRAMAIAH	7.97	Slab 5
113	Feb-25	3047	HPC-MARASANIVARI PALLI	0023	9300061776	M BHARATHI	7.98	Slab 5
114	Feb-25	3047	HPC-MARASANIVARI PALLI	0025	9300066825	M KRISHNA REDDY	7.99	Slab 5
115	Feb-25	3047	HPC-MARASANIVARI PALLI	0026	9300074993	B MANGAMMA	7.86	Slab 5
116	Feb-25	3047	HPC-MARASANIVARI PALLI	0028	9300128261	M DEEPIKA	8.02	Slab 5
117	Feb-25	3047	HPC-MARASANIVARI PALLI	0029	9300128262	M LAKSHMI DEVI	7.99	Slab 5
118	Feb-25	3048	HPC-R KUMMARA PALLI	0001	9300054644	C GOVIDAMMA	7.86	Slab 5
119	Feb-25	3048	HPC-R KUMMARA PALLI	0002	9300054647	M BHARGAVI	7.81	Slab 5
120	Feb-25	3048	HPC-R KUMMARA PALLI	0003	9300054648	M LAKSHMI MOUNIKA	7.85	Slab 5
121	Feb-25	3048	HPC-R KUMMARA PALLI	0005	9300054655	MUNIKRISHNA	7.94	Slab 5
122	Feb-25	3048	HPC-R KUMMARA PALLI	0006	9300054658	N GANGAIAH	7.83	Slab 5
123	Feb-25	3048	HPC-R KUMMARA PALLI	0007	9300054659	N JYOTHI	7.88	Slab 5
124	Feb-25	3048	HPC-R KUMMARA PALLI	0008	9300054660	N LAKSHMIDEVI	8.04	Slab 5
125	Feb-25	3048	HPC-R KUMMARA PALLI	0009	9300054662	N PURUSHOTHAM	7.85	Slab 5
126	Feb-25	3048	HPC-R KUMMARA PALLI	0011	9300054664	N RAMADEVI	7.82	Slab 5
127	Feb-25	3048	HPC-R KUMMARA PALLI	0012	9300054665	N VENKATRAMANA	7.84	Slab 5
128	Feb-25	3048	HPC-R KUMMARA PALLI	0013	9300054666	V JAYALAXMI	7.89	Slab 5
129	Feb-25	3048	HPC-R KUMMARA PALLI	0014	9300054667	V NARAYANAMMA	7.85	Slab 5
130	Feb-25	3048	HPC-R KUMMARA PALLI	0015	9300054668	V RAJAMMA	7.84	Slab 5
131	Feb-25	3048	HPC-R KUMMARA PALLI	0016	9300054669	V RAMBABU	7.84	Slab 5
132	Feb-25	3048	HPC-R KUMMARA PALLI	0017	9300054670	Y LAKSHMI	7.84	Slab 5
133	Feb-25	3048	HPC-R KUMMARA PALLI	0018	9300054671	Y NAGAVENI	7.84	Slab 5
134	Feb-25	3048	HPC-R KUMMARA PALLI	0019	9300055111	C VIJAYA	7.87	Slab 5
135	Feb-25	3048	HPC-R KUMMARA PALLI	0020	9300055112	M NARASAMMA	7.95	Slab 5
136	Feb-25	3048	HPC-R KUMMARA PALLI	0021	9300055114	N DAMODARA	8.07	Slab 5
137	Feb-25	3048	HPC-R KUMMARA PALLI	0023	9300071406	N  MALLIKA	7.83	Slab 5
138	Feb-25	3048	HPC-R KUMMARA PALLI	0025	9300077785	M VENKATAPATHI	7.84	Slab 5
139	Feb-25	3048	HPC-R KUMMARA PALLI	0026	9300077786	N SRINIVASULU	7.83	Slab 5
140	Feb-25	3048	HPC-R KUMMARA PALLI	0027	9300086744	N LAVANYA	8.02	Slab 5
141	Feb-25	3048	HPC-R KUMMARA PALLI	0028	9300092313	N HARITHA	7.84	Slab 5
142	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0001	9300059314	B LAKSHMIDEVI	7.97	Slab 5
143	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0002	9300059315	B MURALI	7.92	Slab 5
144	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0003	9300059316	K DEVI	8.00	Slab 5
145	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0004	9300059317	K REDDEPPA	7.92	Slab 5
146	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0008	9300059326	RUPA LAVANYA	8.00	Slab 5
147	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0011	9300059331	V JAYANTHI	7.92	Slab 5
148	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0013	9300061844	R LEELA KUMAR	8.01	Slab 5
149	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0014	9300062337	S MUBARAK ALI	7.91	Slab 5
150	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0015	9300062339	S SABEEN TAJ	7.93	Slab 5
151	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0017	9300085648	P JALEEL KHAN	7.99	Slab 5
152	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0018	9300085649	P REDDY KHAN	7.92	Slab 5
153	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0019	9300086275	D NARASAMMA	8.03	Slab 5
154	Feb-25	3049	HPC-HANUMANTHARAYUNI PETTA	0020	9300092828	V RANI	7.93	Slab 5
155	Feb-25	3050	HPC-CHENCHAMREDDYGARI PALLI	0001	9300059332	A RAJAMMA	7.90	Slab 5
156	Feb-25	3050	HPC-CHENCHAMREDDYGARI PALLI	0002	9300059334	C PRABAKAR	8.06	Slab 5
157	Feb-25	3050	HPC-CHENCHAMREDDYGARI PALLI	0006	9300059353	D SURENDRA REDDY	8.04	Slab 5
158	Feb-25	3050	HPC-CHENCHAMREDDYGARI PALLI	0008	9300059358	M VISHNUVARDHAN REDDY	7.90	Slab 5
159	Feb-25	3050	HPC-CHENCHAMREDDYGARI PALLI	0009	9300059360	T VENKATARAMANA	7.94	Slab 5
160	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0008	9300062401	K KALAVATHI	7.88	Slab 5
161	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0010	9300062412	K SAHADEVA	7.93	Slab 5
162	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0016	9300062437	O MAHESWAR REDDY	7.83	Slab 5
163	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0017	9300062444	P SAIDANNI	7.85	Slab 5
164	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0019	9300062449	S SAYAD BHASHA	7.87	Slab 5
165	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0029	9300094787	O KRISHNAMMA	7.80	Slab 5
166	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0035	9300094793	D PRASANNA	7.91	Slab 5
167	Feb-25	3051	HPC-BODUMALLUVARI PALLI	0036	9300104122	K ESWARAMMA	7.90	Slab 5
168	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0002	9300062913	D ASHOK KUMAR	7.90	Slab 5
169	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0003	9300062916	D KALAVTHI	8.07	Slab 5
170	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0006	9300062921	D RATHNAMMA	7.90	Slab 5
171	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0008	9300062929	K BHUDEVI	7.86	Slab 5
172	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0009	9300062932	K GEETHA RANI	7.89	Slab 5
173	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0011	9300062939	K SANDHYA	7.99	Slab 5
174	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0013	9300062945	K VASANTHA KUMARI	7.85	Slab 5
175	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0014	9300062949	K VENKATRAMAIAH	7.86	Slab 5
176	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0017	9300072434	V SARADA	7.89	Slab 5
177	Feb-25	3052	HPC-BANDAKINDAPALLI HW	0020	9300132040	DOVALA RAMANAIAH	8.04	Slab 5
178	Feb-25	3055	HPC-N D VADDIPALLI	0010	9300076356	G PARVATHAMMA	8.08	Slab 5
179	Feb-25	3055	HPC-N D VADDIPALLI	0011	9300076354	G SYAMALAMMA	8.04	Slab 5
180	Feb-25	3055	HPC-N D VADDIPALLI	0016	9300081340	G MADHAVI	7.89	Slab 5
181	Feb-25	3055	HPC-N D VADDIPALLI	0021	9300107480	K THULASAMMA	7.96	Slab 5
182	Feb-25	3055	HPC-N D VADDIPALLI	0023	9300134967	K ROOPA	8.02	Slab 5
183	Feb-25	3057	HPC-KUKKALAODDU	0001	9300082822	D KAMALA	8.02	Slab 5
184	Feb-25	3057	HPC-KUKKALAODDU	0002	9300082785	G CHITTEMMA	8.05	Slab 5
185	Feb-25	3057	HPC-KUKKALAODDU	0003	9300082779	G ESWARAMMA	7.94	Slab 5
186	Feb-25	3057	HPC-KUKKALAODDU	0005	9300082780	G VASANTHA	7.98	Slab 5
187	Feb-25	3057	HPC-KUKKALAODDU	0006	9300082778	P CHANDU	8.07	Slab 5
188	Feb-25	3057	HPC-KUKKALAODDU	0007	9300082782	P LAKSHMI DEVI	8.03	Slab 5
189	Feb-25	3057	HPC-KUKKALAODDU	0008	9300082783	P REDDY RANI	8.02	Slab 5
190	Feb-25	3057	HPC-KUKKALAODDU	0010	9300082784	P VEDAVATHI	8.07	Slab 5
191	Feb-25	3057	HPC-KUKKALAODDU	0011	9300082781	P YELLAMMA	8.10	Slab 5
192	Feb-25	3057	HPC-KUKKALAODDU	0012	9300082777	S CHANGAMMA	7.96	Slab 5
193	Feb-25	3057	HPC-KUKKALAODDU	0015	9300083852	D MANI KUMAR	7.90	Slab 5
194	Feb-25	3057	HPC-KUKKALAODDU	0016	9300084604	G GANGADHARA	8.01	Slab 5
195	Feb-25	3057	HPC-KUKKALAODDU	0018	9300118043	prabhakar	8.10	Slab 5
196	Feb-25	3059	HPC-GUNDLURIVARI PALLI	0006	9300086948	K RAJAMMA	7.99	Slab 5
197	Feb-25	3059	HPC-GUNDLURIVARI PALLI	0008	9300086950	P ANASUYA	7.83	Slab 5
198	Feb-25	3059	HPC-GUNDLURIVARI PALLI	0010	9300086943	P RAJAMMA	7.83	Slab 5
199	Feb-25	3059	HPC-GUNDLURIVARI PALLI	0012	9300086942	P SAHADEVAREDDY	7.98	Slab 5
200	Feb-25	3059	HPC-GUNDLURIVARI PALLI	0015	9300090637	P BHARATHAMMA	7.92	Slab 5
201	Feb-25	3059	HPC-GUNDLURIVARI PALLI	0017	9300090635	S GOWRAMMA	7.87	Slab 5
202	Feb-25	3060	HPC-BALIREDDYGARIPALLI	0001	9300095607	V RANEMMA	8.09	Slab 5
203	Feb-25	3060	HPC-BALIREDDYGARIPALLI	0003	9300095609	B GANNIMITTA	7.83	Slab 5
204	Feb-25	3060	HPC-BALIREDDYGARIPALLI	0004	9300095610	V BHASKAR REDDY	7.90	Slab 5
205	Feb-25	3060	HPC-BALIREDDYGARIPALLI	0008	9300095614	V PADMAJA	7.99	Slab 5
206	Feb-25	3061	HPC-CHEEKALA CHENU	0002	9300096474	PACHIPALA SURENDRA	8.07	Slab 5
207	Feb-25	3061	HPC-CHEEKALA CHENU	0004	9300096476	PACHIPALA SUDAKARA	8.06	Slab 5
208	Feb-25	3061	HPC-CHEEKALA CHENU	0007	9300096479	PACHIPALA MANEESH	7.82	Slab 5
209	Feb-25	3061	HPC-CHEEKALA CHENU	0008	9300096480	MALLE KIRAN KUMAR	7.83	Slab 5
210	Feb-25	3061	HPC-CHEEKALA CHENU	0009	9300096481	PACHIPALA VENUGOPALU	7.82	Slab 5
211	Feb-25	3061	HPC-CHEEKALA CHENU	0010	9300096482	V CHITTEMMA	7.82	Slab 5
212	Feb-25	3061	HPC-CHEEKALA CHENU	0014	9300097911	APPINENI NARASAMMA	7.86	Slab 5
213	Feb-25	3061	HPC-CHEEKALA CHENU	0017	9300102353	B GIRI BABU	7.95	Slab 5
214	Feb-25	3061	HPC-CHEEKALA CHENU	0019	9300119676	P MOHAN BABU	7.85	Slab 5
215	Feb-25	3061	HPC-CHEEKALA CHENU	0020	9300119677	B MURALI	7.84	Slab 5
216	Feb-25	3061	HPC-CHEEKALA CHENU	0022	9300142878	M RAMADEVI	7.92	Slab 5
217	Feb-25	3062	HPC-GANTAVARI PALLI	0002	9300096701	SREENIVASULU	8.04	Slab 5
218	Feb-25	3062	HPC-GANTAVARI PALLI	0012	9300096711	C NARSAMMA	8.06	Slab 5
219	Feb-25	3062	HPC-GANTAVARI PALLI	0015	9300097218	A YARRAIAH	8.06	Slab 5
220	Feb-25	3062	HPC-GANTAVARI PALLI	0017	9300097220	G MUNEMMA	7.83	Slab 5
221	Feb-25	3062	HPC-GANTAVARI PALLI	0020	9300100969	KUKATI RAJESH	8.07	Slab 5
222	Feb-25	3063	HPC-GONGIVARI PALLI	0004	9300096489	A CHANDRAMMA	7.81	Slab 5
223	Feb-25	3063	HPC-GONGIVARI PALLI	0005	9300096490	P NANDINI	7.93	Slab 5
224	Feb-25	3063	HPC-GONGIVARI PALLI	0006	9300096491	ANKIREDDY RAMIREDDY	7.80	Slab 5
225	Feb-25	3063	HPC-GONGIVARI PALLI	0007	9300096492	K SRI RAMULU	7.87	Slab 5
226	Feb-25	3063	HPC-GONGIVARI PALLI	0008	9300096493	G NAGESH	7.81	Slab 5
227	Feb-25	3063	HPC-GONGIVARI PALLI	0009	9300096494	U VENKATAMUNI NAIDU	7.90	Slab 5
228	Feb-25	3063	HPC-GONGIVARI PALLI	0011	9300097092	A NAGARAJA	7.80	Slab 5
229	Feb-25	3063	HPC-GONGIVARI PALLI	0012	9300097093	G ANJAMMA	7.82	Slab 5
230	Feb-25	3063	HPC-GONGIVARI PALLI	0013	9300097094	A MARUTHEESWARA REDDY	7.90	Slab 5
231	Feb-25	3063	HPC-GONGIVARI PALLI	0014	9300098209	G RAMNJULU	7.81	Slab 5
232	Feb-25	3063	HPC-GONGIVARI PALLI	0015	9300100972	A BHUDEVI	7.81	Slab 5
233	Feb-25	3063	HPC-GONGIVARI PALLI	0016	9300115028	K VISWANADHA	7.86	Slab 5
234	Feb-25	3063	HPC-GONGIVARI PALLI	0017	9300115029	A RAGHUVA REDDY	7.85	Slab 5
235	Feb-25	3063	HPC-GONGIVARI PALLI	0018	9300119680	P SYAMALAMMA	7.95	Slab 5
236	Feb-25	3063	HPC-GONGIVARI PALLI	0019	9300123431	K BHARGAVI	7.89	Slab 5
237	Feb-25	3064	HPC-GANDLA PALLI	0001	9300096463	SAHADEVAIAH N	8.09	Slab 5
238	Feb-25	3064	HPC-GANDLA PALLI	0005	9300096467	LAXMIDEV B	7.83	Slab 5
239	Feb-25	3064	HPC-GANDLA PALLI	0006	9300096468	P HANUMANTHU	7.95	Slab 5
240	Feb-25	3064	HPC-GANDLA PALLI	0009	9300096471	HARI PRASAD P	7.89	Slab 5
241	Feb-25	3064	HPC-GANDLA PALLI	0010	9300096472	K ESWARAMMA	7.92	Slab 5
242	Feb-25	3064	HPC-GANDLA PALLI	0012	9300097090	M LAKSHMIDEVI	8.05	Slab 5
243	Feb-25	3064	HPC-GANDLA PALLI	0013	9300097091	K MALLESWARI	8.06	Slab 5
244	Feb-25	3064	HPC-GANDLA PALLI	0014	9300097912	SANKARAIH C	7.97	Slab 5
245	Feb-25	3064	HPC-GANDLA PALLI	0015	9300097913	B KUMARI	7.95	Slab 5
246	Feb-25	3064	HPC-GANDLA PALLI	0016	9300097914	M YERRAKKA	7.88	Slab 5
247	Feb-25	3064	HPC-GANDLA PALLI	0017	9300097915	V GANGADEVI	7.90	Slab 5
248	Feb-25	3064	HPC-GANDLA PALLI	0018	9300097916	C PADMAVATHAMMA	8.09	Slab 5
249	Feb-25	3064	HPC-GANDLA PALLI	0021	9300097919	M CHANDRAMMA	7.87	Slab 5
250	Feb-25	3064	HPC-GANDLA PALLI	0027	9300103262	N CHARAN KUMAR	8.03	Slab 5
"""

FARMER_DATA = {}
# Skip the header row and then process each line
for line in farmer_data_raw.strip().split('\n')[1:]:
    parts = line.split('\t')
    if len(parts) >= 7:  # Ensure there are enough columns
        member_code = parts[4].strip()
        farmer_name = parts[6].strip()
        FARMER_DATA[member_code] = farmer_name

# Create lists for dropdowns based on the new FARMER_DATA
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
    'uploaded_temp_photo_paths': [],  # To store paths of temporarily uploaded photos
    'final_submitted_data': None,  # To store data ready for review/submission
    'current_step': 'form_entry',  # 'form_entry', 'review', 'submitted'
    'farmer_name_selected_prev': FARMER_NAMES_ORIGINAL[0] if FARMER_NAMES_ORIGINAL else 'Others' # To track previous farmer name selection
}

# Function to save current form data to a draft file
def save_draft():
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    # Get current values from session_state, falling back to defaults if not present
    # Only save the keys that are part of the form's state
    draft_data = {key: st.session_state.get(key, initial_values_defaults.get(key)) for key in initial_values_defaults.keys()}
    
    # Convert datetime.date objects to string for JSON serialization
    if 'visit_date' in draft_data and isinstance(draft_data['visit_date'], datetime.date):
        draft_data['visit_date'] = draft_data['visit_date'].isoformat()
    
    # Special handling for uploaded_temp_photo_paths to ensure it's a list even if it was None/empty
    if 'uploaded_temp_photo_paths' not in draft_data or not isinstance(draft_data['uploaded_temp_photo_paths'], list):
        draft_data['uploaded_temp_photo_paths'] = []

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
                elif key in ['green_fodder_types', 'dry_fodder_types', 'pellet_feed_brands', 'water_sources', 'uploaded_temp_photo_paths']:
                    # Ensure multiselect defaults are lists
                    st.session_state[key] = list(value) if isinstance(value, list) else []
                else:
                    st.session_state[key] = value
            
            # --- VALIDATE DROPDOWN SELECTIONS AFTER LOADING DRAFT ---
            # Ensure vlcc_name is a valid option if it exists in loaded_data
            if 'vlcc_name' in st.session_state and st.session_state['vlcc_name'] not in VLCC_NAMES:
                st.session_state['vlcc_name'] = VLCC_NAMES[0] if VLCC_NAMES else None
            
            # Re-validate other dropdown selections based on current language
            # This requires fetching labels *after* lang_select might have been updated from draft
            temp_lang = loaded_data.get('lang_select', 'English')
            current_labels = dict_translations.get(temp_lang, dict_translations['English'])
            
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
            
            # For farmer_name_selected, ensure it's a valid option or "Others"
            farmer_names_with_others_for_load = FARMER_NAMES_ORIGINAL + [current_labels['Others']]
            if 'farmer_name_selected' in st.session_state and st.session_state['farmer_name_selected'] not in farmer_names_with_others_for_load:
                st.session_state['farmer_name_selected'] = FARMER_NAMES_ORIGINAL[0] if FARMER_NAMES_ORIGINAL else current_labels['Others']

            # For farmer_code, ensure it's a valid option
            if 'farmer_code' in st.session_state and st.session_state['farmer_code'] not in FARMER_CODES:
                st.session_state['farmer_code'] = FARMER_CODES[0] if FARMER_CODES else None

            # For mineral_brand, ensure it's a valid option
            if 'mineral_brand' in st.session_state and st.session_state['mineral_brand'] not in MINERAL_MIXTURE_BRANDS:
                st.session_state['mineral_brand'] = MINERAL_MIXTURE_BRANDS[0] if MINERAL_MIXTURE_BRANDS else None
            
            # For surveyor_name, ensure it's a valid option
            if 'surveyor_name' in st.session_state and st.session_state['surveyor_name'] not in SURVEYOR_NAMES:
                st.session_state['surveyor_name'] = SURVEYOR_NAMES[0] if SURVEYOR_NAMES else None

            # Explicitly ensure uploaded_temp_photo_paths is a list after loading
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
    # Define keys to *always keep* (not clear)
    persistent_keys = ['lang_select', 'app_initialized_flag', 'current_step']

    # Iterate through all session state keys and delete those not in persistent_keys
    # Create a list of keys to delete to avoid modifying dict during iteration
    keys_to_delete = [key for key in st.session_state.keys() if key not in persistent_keys]

    for key in keys_to_delete:
        if key in st.session_state: # Check if key still exists before deleting
            del st.session_state[key]
    
    # Reset specific keys to their defaults for a fresh form
    for key, default_value in initial_values_defaults.items():
        if key not in st.session_state: # Only set if it was deleted or never existed
            st.session_state[key] = default_value
    
    # Ensure current_step is back to form_entry
    st.session_state.current_step = 'form_entry'
    st.session_state.last_saved_time_persistent = None # Clear auto-save message
    
    # Clear temporary images
    for f in os.listdir(TEMP_IMAGE_DIR):
        os.remove(os.path.join(TEMP_IMAGE_DIR, f))
    st.session_state.uploaded_temp_photo_paths = [] # Also clear paths in session state

    # Important: Remove the draft file after successful submission
    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
    if os.path.exists(draft_filename):
        os.remove(draft_filename)

    st.rerun() # Rerun to clear the form fields and update display

# Function to create a ZIP file of all images
def create_zip_file():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(FINAL_IMAGE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, FINAL_IMAGE_DIR))
    zip_buffer.seek(0)
    return zip_buffer

# Function to get all survey responses as a DataFrame
def get_all_responses_df():
    all_files = [os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR) if f.endswith('.csv') and f.startswith('survey_response_')]
    
    if not all_files:
        return pd.DataFrame() # Return empty DataFrame if no files

    # Read each CSV file and concatenate them
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


# Initialize session state for the first time or load draft
if 'app_initialized_flag' not in st.session_state:
    st.session_state.app_initialized_flag = True
    st.session_state.last_saved_time_persistent = None
    
    # Initialize all defaults first
    for key, default_value in initial_values_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Then try to load draft, which will overwrite defaults if successful and valid
    load_draft()

# Language Selection
initial_lang_options = ("English", "Hindi", "Marathi", "Telugu")
# Ensure st.session_state.lang_select is initialized before using it for index
if 'lang_select' not in st.session_state or st.session_state.lang_select not in initial_lang_options:
    st.session_state.lang_select = "English"

initial_lang_index = initial_lang_options.index(st.session_state.lang_select)

lang = st.sidebar.selectbox( # Moved to sidebar
    "Language / भाषा / भाषा / భాష", # Updated display text for sidebar
    initial_lang_options,
    index=initial_lang_index,
    key="lang_select",
    on_change=save_draft # Save draft when language changes
)
labels = dict_translations.get(lang, dict_translations['English'])

# Display auto-save status
if st.session_state.last_saved_time_persistent and st.session_state.current_step == 'form_entry':
    st.info(f"{labels['Auto-saved!']} Last saved: {st.session_state.last_saved_time_persistent}")
else:
    if st.session_state.current_step == 'form_entry':
        st.info("No auto-saved draft found, or draft cleared. Start filling the form!")

# --- Main Application Logic based on current_step ---
if st.session_state.current_step == 'form_entry':
    st.title(labels['Farmer Profile'])

    # Form Start
    with st.form("survey_form"):
        st.header(labels['Farmer Profile'])

        # Safely get vlcc_name from session state for default index
        current_vlcc_name = st.session_state.get('vlcc_name', VLCC_NAMES[0] if VLCC_NAMES else None)
        vlcc_name_default_idx = 0
        if current_vlcc_name in VLCC_NAMES:
            vlcc_name_default_idx = VLCC_NAMES.index(current_vlcc_name)
        elif VLCC_NAMES:
            vlcc_name_default_idx = 0

        vlcc_name = st.selectbox(
            labels['VLCC Name'], VLCC_NAMES,
            index=vlcc_name_default_idx,
            key="vlcc_name",
            disabled=(not VLCC_NAMES)
        )

        hpc_code = st.text_input(
            labels['HPC/MCC Code'],
            value=st.session_state.get('hpc_code', ''), # Safely get
            key="hpc_code"
        )

        types_options = (labels['HPC'], labels['MCC'])
        current_types = st.session_state.get('types', types_options[0]) # Safely get
        types_default_idx = 0
        if current_types in types_options:
            types_default_idx = types_options.index(current_types)
        types = st.selectbox(
            labels['Types'], types_options,
            index=types_default_idx,
            key="types"
        )

        farmer_names_with_others = FARMER_NAMES_ORIGINAL + [labels['Others']]
        current_farmer_name_selected = st.session_state.get('farmer_name_selected', farmer_names_with_others[0] if farmer_names_with_others else labels['Others'])
        farmer_name_default_idx = 0
        if current_farmer_name_selected in farmer_names_with_others:
            farmer_name_default_idx = farmer_names_with_others.index(current_farmer_name_selected)
        elif farmer_names_with_others:
            farmer_name_default_idx = 0

        farmer_name_selected = st.selectbox(
            labels['Farmer Name'], options=farmer_names_with_others,
            index=farmer_name_default_idx,
            key="farmer_name_selected",
            disabled=(not farmer_names_with_others)
        )

        # Logic to handle "Others" for Farmer Name
        # Ensure farmer_name_other is correctly retrieved/initialized
        farmer_name_other = st.session_state.get('farmer_name_other', '')
        
        # Store the current selection to compare in the next run
        # This needs to be outside the if block so it's always updated
        # It's better to manage this logic after the form submission or with explicit callbacks
        # For now, relying on Streamlit's reruns for visibility
        if farmer_name_selected == labels['Others']:
            farmer_name_other = st.text_input(
                labels['Specify Farmer Name'],
                value=farmer_name_other,
                key="farmer_name_other"
            )
        else:
            # If "Others" is not selected, ensure the 'farmer_name_other' in session state is cleared
            # This is crucial for data integrity, as form submission only captures current state.
            if 'farmer_name_other' in st.session_state:
                st.session_state['farmer_name_other'] = ""
            farmer_name_other = "" # Ensure local variable is also empty

        current_farmer_code = st.session_state.get('farmer_code', FARMER_CODES[0] if FARMER_CODES else None) # Safely get
        farmer_code_default_idx = 0
        if current_farmer_code in FARMER_CODES:
            farmer_code_default_idx = FARMER_CODES.index(current_farmer_code)
        elif FARMER_CODES:
            farmer_code_default_idx = 0

        farmer_code = st.selectbox(
            labels['Farmer Code'], options=FARMER_CODES,
            index=farmer_code_default_idx,
            key="farmer_code",
            disabled=(not FARMER_CODES)
        )

        gender_options = (labels['Male'], labels['Female'])
        current_gender = st.session_state.get('gender', gender_options[0]) # Safely get
        gender_default_idx = 0
        if current_gender in gender_options:
            gender_default_idx = gender_options.index(current_gender)
        gender = st.selectbox(
            labels['Gender'], gender_options,
            index=gender_default_idx,
            key="gender"
        )

        st.header(labels['Farm Details'])
        cows = st.number_input(
            labels['Number of Cows'], min_value=0,
            value=int(st.session_state.get('cows', 0)), # Safely get
            key="cows"
        )

        cattle_in_milk = st.number_input(
            labels['No. of Cattle in Milk'], min_value=0,
            value=int(st.session_state.get('cattle_in_milk', 0)),
            key="cattle_in_milk"
        )
        calves = st.number_input(
            labels['No. of Calves/Heifers'], min_value=0,
            value=int(st.session_state.get('calves', 0)),
            key="calves"
        )
        desi_cows = st.number_input(
            labels['No. of Desi cows'], min_value=0,
            value=int(st.session_state.get('desi_cows', 0)),
            key="desi_cows"
        )
        crossbreed_cows = st.number_input(
            labels['No. of Cross breed cows'], min_value=0,
            value=int(st.session_state.get('crossbreed_cows', 0)),
            key="crossbreed_cows"
        )
        buffalo = st.number_input(
            labels['No. of Buffalo'], min_value=0,
            value=int(st.session_state.get('buffalo', 0)),
            key="buffalo"
        )
        milk_production = st.number_input(
            labels['Milk Production'], min_value=0.0, format="%.2f",
            value=float(st.session_state.get('milk_production', 0.0)),
            key="milk_production"
        )

        st.header(labels['Specific Questions'])
        green_fodder_options = (labels['Yes'], labels['No'])
        current_green_fodder = st.session_state.get('green_fodder', green_fodder_options[0])
        green_fodder_default_idx = 0
        if current_green_fodder in green_fodder_options:
            green_fodder_default_idx = green_fodder_options.index(current_green_fodder)
        green_fodder = st.radio(
            labels['Green Fodder'], green_fodder_options,
            index=green_fodder_default_idx,
            key="green_fodder"
        )
        
        # Initialize with current session state values, or empty list/0.0
        green_fodder_types_current = st.session_state.get('green_fodder_types', [])
        green_fodder_qty_current = st.session_state.get('green_fodder_qty', 0.0)

        if green_fodder == labels['Yes']:
            green_fodder_types = st.multiselect(
                labels['Type of Green Fodder'], GREEN_FODDER_OPTIONS,
                default=green_fodder_types_current,
                key="green_fodder_types"
            )
            green_fodder_qty = st.number_input(
                labels['Quantity of Green Fodder'], min_value=0.0, format="%.2f",
                value=float(green_fodder_qty_current),
                key="green_fodder_qty"
            )
        else:
            # Clear associated session state values when "No" is selected
            if 'green_fodder_types' in st.session_state: del st.session_state['green_fodder_types']
            if 'green_fodder_qty' in st.session_state: del st.session_state['green_fodder_qty']
            green_fodder_types = [] # Ensure local variables are also reset
            green_fodder_qty = 0.0

        dry_fodder_options = (labels['Yes'], labels['No'])
        current_dry_fodder = st.session_state.get('dry_fodder', dry_fodder_options[0])
        dry_fodder_default_idx = 0
        if current_dry_fodder in dry_fodder_options:
            dry_fodder_default_idx = dry_fodder_options.index(current_dry_fodder)
        dry_fodder = st.radio(
            labels['Dry Fodder'], dry_fodder_options,
            index=dry_fodder_default_idx,
            key="dry_fodder"
        )
        
        dry_fodder_types_current = st.session_state.get('dry_fodder_types', [])
        dry_fodder_qty_current = st.session_state.get('dry_fodder_qty', 0.0)
        if dry_fodder == labels['Yes']:
            dry_fodder_types = st.multiselect(
                labels['Type of Dry Fodder'], DRY_FODDER_OPTIONS,
                default=dry_fodder_types_current,
                key="dry_fodder_types"
            )
            dry_fodder_qty = st.number_input(
                labels['Quantity of Dry Fodder'], min_value=0.0, format="%.2f",
                value=float(dry_fodder_qty_current),
                key="dry_fodder_qty"
            )
        else:
            if 'dry_fodder_types' in st.session_state: del st.session_state['dry_fodder_types']
            if 'dry_fodder_qty' in st.session_state: del st.session_state['dry_fodder_qty']
            dry_fodder_types = []
            dry_fodder_qty = 0.0

        pellet_feed_options = (labels['Yes'], labels['No'])
        current_pellet_feed = st.session_state.get('pellet_feed', pellet_feed_options[0])
        pellet_feed_default_idx = 0
        if current_pellet_feed in pellet_feed_options:
            pellet_feed_default_idx = pellet_feed_options.index(current_pellet_feed)
        pellet_feed = st.radio(
            labels['Pellet Feed'], pellet_feed_options,
            index=pellet_feed_default_idx,
            key="pellet_feed"
        )
        
        pellet_feed_brands_current = st.session_state.get('pellet_feed_brands', [])
        pellet_feed_qty_current = st.session_state.get('pellet_feed_qty', 0.0)
        if pellet_feed == labels['Yes']:
            pellet_feed_brands = st.multiselect(
                labels['Pellet Feed Brand'], PELLET_FEED_BRANDS,
                default=pellet_feed_brands_current,
                key="pellet_feed_brands"
            )
            pellet_feed_qty = st.number_input(
                labels['Quantity of Pellet Feed'], min_value=0.0, format="%.2f",
                value=float(pellet_feed_qty_current),
                key="pellet_feed_qty"
            )
        else:
            if 'pellet_feed_brands' in st.session_state: del st.session_state['pellet_feed_brands']
            if 'pellet_feed_qty' in st.session_state: del st.session_state['pellet_feed_qty']
            pellet_feed_brands = []
            pellet_feed_qty = 0.0

        mineral_mixture_options = (labels['Yes'], labels['No'])
        current_mineral_mixture = st.session_state.get('mineral_mixture', mineral_mixture_options[0])
        mineral_mixture_default_idx = 0
        if current_mineral_mixture in mineral_mixture_options:
            mineral_mixture_default_idx = mineral_mixture_options.index(current_mineral_mixture)
        mineral_mixture = st.radio(
            labels['Mineral Mixture'], mineral_mixture_options,
            index=mineral_mixture_default_idx,
            key="mineral_mixture"
        )
        
        mineral_brand_current = st.session_state.get('mineral_brand', MINERAL_MIXTURE_BRANDS[0] if MINERAL_MIXTURE_BRANDS else None)
        mineral_qty_current = st.session_state.get('mineral_qty', 0.0)
        if mineral_mixture == labels['Yes']:
            mineral_brand_default_idx = 0
            if mineral_brand_current in MINERAL_MIXTURE_BRANDS:
                mineral_brand_default_idx = MINERAL_MIXTURE_BRANDS.index(mineral_brand_current)
            mineral_brand = st.selectbox(
                labels['Mineral Mixture Brand'], MINERAL_MIXTURE_BRANDS,
                index=mineral_brand_default_idx,
                key="mineral_brand"
            )
            mineral_qty = st.number_input(
                labels['Quantity of Mineral Mixture'], min_value=0.0, format="%.2f",
                value=float(mineral_qty_current),
                key="mineral_qty"
            )
        else:
            if 'mineral_brand' in st.session_state: del st.session_state['mineral_brand']
            if 'mineral_qty' in st.session_state: del st.session_state['mineral_qty']
            mineral_brand = ""
            mineral_qty = 0.0

        silage_options = (labels['Yes'], labels['No'])
        current_silage = st.session_state.get('silage', silage_options[0])
        silage_default_idx = 0
        if current_silage in silage_options:
            silage_default_idx = silage_options.index(current_silage)
        silage = st.radio(
            labels['Silage'], silage_options,
            index=silage_default_idx,
            key="silage"
        )
        
        silage_source_current = st.session_state.get('silage_source', '')
        silage_qty_current = st.session_state.get('silage_qty', 0.0)
        if silage == labels['Yes']:
            silage_source = st.text_input(
                labels['Source and Price of Silage'],
                value=silage_source_current,
                key="silage_source"
            )
            silage_qty = st.number_input(
                labels['Quantity of Silage'], min_value=0.0, format="%.2f",
                value=float(silage_qty_current),
                key="silage_qty"
            )
        else:
            if 'silage_source' in st.session_state: del st.session_state['silage_source']
            if 'silage_qty' in st.session_state: del st.session_state['silage_qty']
            silage_source = ""
            silage_qty = 0.0

        water_sources_current = st.session_state.get('water_sources', [])
        water_sources = st.multiselect(
            labels['Source of Water'], WATER_SOURCE_OPTIONS,
            default=water_sources_current,
            key="water_sources"
        )

        # --- Photo Upload Snippet ---
        st.header(labels['Upload Photos'])
        uploaded_files = st.file_uploader(
            labels['Upload Photos'],
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="image_uploader" # Unique key for file uploader
        )

        # Process newly uploaded files
        if uploaded_files:
            # This loop runs *every time* the form is submitted or a rerun happens.
            # We need to ensure we only add new files and handle duplicates properly.
            for uploaded_file in uploaded_files:
                # Use a more robust check for uniqueness - combining filename and size or content hash
                # For this example, we'll use a combination of name and size as a basic check
                file_content = uploaded_file.getvalue()
                file_hash = base64.b64encode(file_content).decode() # Simple hash based on content

                # Check if this file (by content hash) has already been uploaded in this session
                is_duplicate = False
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
                        except Exception as e:
                            st.error(f"{labels['Error uploading photo:']} {uploaded_file.name}. {e}")
                    else:
                        st.warning(f"Could not upload {uploaded_file.name}: {labels['Please upload up to 3 photos.']}")
                # else:
                #     st.info(f"Skipped duplicate upload: {uploaded_file.name}") # Optional: inform user about duplicates
        
        # Display existing temporary photos and provide a remove option
        if st.session_state.get('uploaded_temp_photo_paths'):
            st.subheader("Currently uploaded photos:")
            # Use a copy of the list for iteration to avoid issues when modifying during iteration
            photos_to_display = list(st.session_state.uploaded_temp_photo_paths)
            
            # Clear invalid paths first to avoid errors during display
            valid_photos = []
            for photo_path in photos_to_display:
                if os.path.exists(photo_path):
                    valid_photos.append(photo_path)
                else:
                    st.warning(f"Temporary photo path not found: {os.path.basename(photo_path)}. It might have been moved or deleted.")
            st.session_state.uploaded_temp_photo_paths = valid_photos # Update session state with only valid paths
            
            cols = st.columns(3) # Adjust number of columns as needed
            for i, photo_path in enumerate(st.session_state.uploaded_temp_photo_paths):
                try:
                    with open(photo_path, "rb") as f:
                        encoded_string = base64.b64encode(f.read()).decode()
                    
                    with cols[i % 3]: # Distribute images across columns
                        st.image(f"data:image/png;base64,{encoded_string}", caption=os.path.basename(photo_path), use_column_width=True)
                        # Button inside a column, unique key per photo
                        if st.button(f"Remove", key=f"remove_photo_{i}_{os.path.basename(photo_path).replace('.', '_')}"):
                            os.remove(photo_path)
                            st.session_state.uploaded_temp_photo_paths.remove(photo_path) # Remove the path from the session state list
                            st.rerun() # Rerun to update the display after removal
                except Exception as e:
                    cols[i % 3].error(f"Could not load image {os.path.basename(photo_path)}: {e}")
                    # If file cannot be loaded, consider removing it from the list to avoid future errors
                    if photo_path in st.session_state.uploaded_temp_photo_paths:
                        st.session_state.uploaded_temp_photo_paths.remove(photo_path)
                        st.rerun()
        else:
            st.info(labels['No photo uploaded.'])


        st.header("Survey Details")
        current_surveyor_name = st.session_state.get('surveyor_name', SURVEYOR_NAMES[0] if SURVEYOR_NAMES else None) # Safely get
        surveyor_name_default_idx = 0
        if current_surveyor_name in SURVEYOR_NAMES:
            surveyor_name_default_idx = SURVEYOR_NAMES.index(current_surveyor_name)
        surveyor_name = st.selectbox(
            labels['Name'], SURVEYOR_NAMES,
            index=surveyor_name_default_idx,
            key="surveyor_name"
        )
        
        current_visit_date = st.session_state.get('visit_date', datetime.date.today())
        if not isinstance(current_visit_date, datetime.date):
            try:
                current_visit_date = datetime.date.fromisoformat(current_visit_date)
            except (TypeError, ValueError):
                current_visit_date = datetime.date.today()

        visit_date = st.date_input(
            labels['Date of Visit'],
            value=current_visit_date,
            key="visit_date"
        )

        # --- Submit Button (MUST BE INSIDE THE FORM) ---
        submit_for_review = st.form_submit_button(labels['Submit'])

        if submit_for_review:
            # Determine the final farmer name based on selection
            final_farmer_name = farmer_name_other if farmer_name_selected == labels['Others'] else farmer_name_selected

            # Collect all data for review from session state
            data_for_review = {
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
                "Type of Green Fodder": ", ".join(st.session_state.get('green_fodder_types', [])) if st.session_state.get('green_fodder') == labels['Yes'] else "N/A",
                "Quantity of Green Fodder (Kg/day)": st.session_state.get('green_fodder_qty', 0.0) if st.session_state.get('green_fodder') == labels['Yes'] else 0.0,
                "Dry Fodder Provided": dry_fodder,
                "Type of Dry Fodder": ", ".join(st.session_state.get('dry_fodder_types', [])) if st.session_state.get('dry_fodder') == labels['Yes'] else "N/A",
                "Quantity of Dry Fodder (Kg/day)": st.session_state.get('dry_fodder_qty', 0.0) if st.session_state.get('dry_fodder') == labels['Yes'] else 0.0,
                "Pellet Feed Provided": pellet_feed,
                "Pellet Feed Brand": ", ".join(st.session_state.get('pellet_feed_brands', [])) if st.session_state.get('pellet_feed') == labels['Yes'] else "N/A",
                "Quantity of Pellet Feed (Kg/day)": st.session_state.get('pellet_feed_qty', 0.0) if st.session_state.get('pellet_feed') == labels['Yes'] else 0.0,
                "Mineral Mixture Provided": mineral_mixture,
                "Mineral Mixture Brand": st.session_state.get('mineral_brand') if st.session_state.get('mineral_mixture') == labels['Yes'] else "N/A",
                "Quantity of Mineral Mixture (gm/day)": st.session_state.get('mineral_qty', 0.0) if st.session_state.get('mineral_mixture') == labels['Yes'] else 0.0,
                "Silage Provided": silage,
                "Source and Price of Silage": st.session_state.get('silage_source', '') if st.session_state.get('silage') == labels['Yes'] else "N/A",
                "Quantity of Silage (Kg/day)": st.session_state.get('silage_qty', 0.0) if st.session_state.get('silage') == labels['Yes'] else 0.0,
                "Source of Water": ", ".join(st.session_state.get('water_sources', [])) if st.session_state.get('water_sources') else "N/A",
                "Name of Surveyor": surveyor_name,
                "Date of Visit": visit_date.isoformat(), # ISO format for consistent saving
                "Photo Paths": st.session_state.uploaded_temp_photo_paths # Store temp paths for review
            }
            st.session_state.final_submitted_data = data_for_review
            st.session_state.current_step = 'review'
            save_draft() # Save draft here, after data is collected and state updated
            st.rerun()

elif st.session_state.current_step == 'review':
    st.title(labels['Review Your Submission'])
    st.write("Please review the information below before final submission.")

    data_to_review = st.session_state.final_submitted_data

    if data_to_review:
        # Display all collected data in a more structured way
        st.subheader("Farmer Profile")
        st.write(f"**{labels['Language']}:** {data_to_review['Language']}")
        st.write(f"**{labels['VLCC Name']}:** {data_to_review['VLCC Name']}")
        st.write(f"**{labels['HPC/MCC Code']}:** {data_to_review['HPC/MCC Code']}")
        st.write(f"**{labels['Types']}:** {data_to_review['Type']}")
        st.write(f"**{labels['Farmer Name']}:** {data_to_review['Farmer Name']}")
        st.write(f"**{labels['Farmer Code']}:** {data_to_review['Farmer Code / Pourer ID']}")
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
                # Move photos from temp to final directory
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
                            final_photo_paths.append(temp_path) # Keep temp path if move fails
                    else:
                        st.warning(f"Temporary photo {os.path.basename(temp_path)} not found during final submission. Skipping.")
                
                # Update the photo paths in the data to be saved to CSV (joining paths with comma)
                data_to_review["Photo Paths"] = ", ".join(final_photo_paths)

                # Convert to DataFrame and save
                df = pd.DataFrame([data_to_review])

                # Define filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(SAVE_DIR, f"survey_response_{timestamp}.csv")

                # Save to CSV
                try:
                    # Append to file if it exists, otherwise create it
                    # Check if the file exists to decide whether to write header
                    file_exists = os.path.exists(file_path)
                    df.to_csv(file_path, mode='a', header=not file_exists, index=False)
                    
                    st.session_state.current_step = 'submitted'
                    st.session_state.last_saved_time_persistent = None # Clear auto-save message
                    
                    # Clear temporary image directory after successful submission
                    for f in os.listdir(TEMP_IMAGE_DIR):
                        os.remove(os.path.join(TEMP_IMAGE_DIR, f))
                    st.session_state.uploaded_temp_photo_paths = [] # Clear the list in session state

                    # Important: Remove the draft file after successful submission
                    draft_filename = os.path.join(DRAFT_DIR, "current_draft.json")
                    if os.path.exists(draft_filename):
                        os.remove(draft_filename)

                    st.rerun() # Rerun to show success message
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
        clear_form_fields() # This function will reset state and rerun

# --- Sidebar for Download Options ---
st.sidebar.markdown("---")
st.sidebar.header("Download Options")

# Download All Responses (CSV)
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

    # Download All Responses (Excel)
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

# Download All Photos (ZIP)
# Check if FINAL_IMAGE_DIR exists and contains files
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
