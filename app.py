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

# Create a dictionary for farmer data (ensure unique keys if possible in real data)
# Note: Duplicate keys in FARMER_DATA like "0008" will result in only the last value being kept.
# It's recommended to have unique farmer codes or a list of tuples if codes can be repeated for different farmers.
FARMER_DATA = {
    "0005": "KATTARI VASANTA KUMARI",
    "0006": "GUDISI NARAYANAMMA",
    "0007": "P SUREKHA",
    "0008": "VAGUMALLU SUDHAKARREDDY", # This will overwrite the previous "0008"
    "0015": "VANGUNALLI REDDY SEKHAR REDDY",
    "0017": "Y REDDEMMA",
    "0003": "INDIRAVATHI MARRIPATTI",
    # "0008": "CHIKATIPALLI VASANTHA", # This was a duplicate key
    "0011": "BIRE LAKSHMI DEVI",
    "0013": "B SAMPURNA",
    "0016": "R PADMA",
    "0017": "KRISHTNAMMA KOTAKONDA", # This will overwrite the previous "0017"
    "0018": "A LAKSHMAIAH",
    "0021": "CANDRAKALA GURRAMKONDA",
    "0025": "P JYOTHI",
    "0030": "M KANTHAMMA",
    "0033": "M CHANDRA",
    "0036": "C SURYA PRAKASH",
    "0001": "P SHANKARAMMA",
    "0012": "V PRAMEELA",
    # "0003": "RAJINI KUMAR REDDY M", # This was a duplicate key
    "0002": "D GOPAL NAIDU",
    # "0003": "D PRASAD REDDY", # This was a duplicate key
    "0006": "G RATHNAMMA", # This will overwrite the previous "0006"
    "0009": "M NARAYANAMMA",
    # "0012": "V DEVAKI", # This was a duplicate key
    "0026": "P HARSHA VARDHAN REDDY",
    "0019": "B REDDEMMA",
    # "0002": "J RAMADEVI", # This was a duplicate key
    # "0003": "N SIDDAMA", # This was a duplicate key
    "0005": "J ESWARAMMA", # This will overwrite the previous "0005"
    "0006": "M SIDDAMMA", # This will overwrite the previous "0006"
    "0008": "Y DEVAKI DEVI", # This will overwrite the previous "0008"
    # "0003": "C RAMANAIAH", # This was a duplicate key
    "0014": "P REDDY PRASAD",
    "0002": "B VARA LAKSHMI", # This will overwrite the previous "0002"
    # "0003": "D NAGARJUNA", # This was a duplicate key
    "0001": "C USHARANI", # This will overwrite the previous "0001"
    "0006": "S SHAHEEDA BEGUM", # This will overwrite the previous "0006"
    "0007": "S SHAMSHAD", # This will overwrite the previous "0007"
    "0008": "S USHA RANI", # This will overwrite the previous "0008"
    "0010": "V REDDY RANI",
    "0012": "A KALAVATHI", # This will overwrite the previous "0012"
    "0014": "S YASHODA", # This will overwrite the previous "0014"
    "0015": "N RESHMA", # This will overwrite the previous "0015"
    "0016": "D RAMADEVI", # This will overwrite the previous "0016"
    "0017": "S SHARMILA", # This will overwrite the previous "0017"
    "0018": "B RANI", # This will overwrite the previous "0018"
    "0027": "DESIREDDY PALLAVI",
    "0028": "C SREERAMI REDDY",
    "0005": "M JYOSHNA", # This will overwrite the previous "0005"
    "0013": "M VENKTRAMAIAH", # This will overwrite the previous "0013"
    "0002": "M BHARGAVI", # This will overwrite the previous "0002"
    "0006": "N GANGAIAH", # This will overwrite the previous "0006"
    "0009": "N PURUSHOTHAM", # This will overwrite the previous "0009"
    "0011": "N RAMADEVI",
    "0017": "Y LAKSHMI", # This will overwrite the previous "0017"
    "0026": "N SRINIVASULU", # This will overwrite the previous "0026"
    "0027": "N LAVANYA", # This will overwrite the previous "0027"
    "0002": "B MURALI", # This will overwrite the previous "0002"
    "0014": "S MUBARAK ALI", # This will overwrite the previous "0014"
    "0015": "S SABEEN TAJ", # This will overwrite the previous "0015"
    "0019": "D NARASAMMA", # This will overwrite the previous "0019"
    "0020": "V RANI",
    "0001": "A RAJAMMA", # This will overwrite the previous "0001"
    "0006": "D SURENDRA REDDY", # This will overwrite the previous "0006"
    "0008": "M VISHNUVARDHAN REDDY", # This will overwrite the previous "0008"
    "0010": "K SAHADEVA",
    "0002": "D ASHOK KUMAR", # This will overwrite the previous "0002"
    "0014": "K VENKATRAMAIAH", # This will overwrite the previous "0014"
    "0006": "K RAJAMMA", # This will overwrite the previous "0006"
    "0008": "P ANASUYA", # This will overwrite the previous "0008"
    "0010": "P RAJAMMA", # This will overwrite the previous "0010"
    "0012": "P SAHADEVAREDDY", # This will overwrite the previous "0012"
    "0015": "P BHARATHAMMA", # This will overwrite the previous "0015"
    "0017": "S GOWRAMMA", # This will overwrite the previous "0017"
    "0008": "V PADMAJA", # This will overwrite the previous "0008"
    "0010": "V CHITTEMMA", # This will overwrite the previous "0010"
    "0017": "B GIRI BABU", # This will overwrite the previous "0017"
    "0019": "P MOHAN BABU", # This will overwrite the previous "0019"
    "0002": "SREENIVASULU", # This will overwrite the previous "0002"
    "0012": "C NARSAMMA", # This will overwrite the previous "0012"
    "0004": "A CHANDRAMMA",
    "0014": "G RAMNJULU", # This will overwrite the previous "0014"
    "0018": "P SYAMALAMMA", # This will overwrite the previous "0018"
    "0019": "K BHARGAVI", # This will overwrite the previous "0019"
    "0012": "M LAKSHMIDEVI", # This will overwrite the previous "0012"
    "0013": "K MALLESWARI", # This will overwrite the previous "0013"
    "0016": "M YERRAKKA", # This will overwrite the previous "0016"
    "0017": "V GANGADEVI", # This will overwrite the previous "0017"
    "0021": "M CHANDRAMMA" # This will overwrite the previous "0021"
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
