import threading
import streamlit as st
import requests
import base64
from flask import Flask, request, jsonify
import pandas as pd
from openpyxl import load_workbook
import subprocess

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Astemo - Entrée de Données",
    layout="wide",
    initial_sidebar_state="collapsed"
)
query_params = st.query_params.to_dict()
if "page" in query_params:
    if query_params["page"] == "dashboard":
        st.switch_page("pages/dashboard.py")

def add_logo():
    # Encodage du logo
    with open("logo.png", "rb") as f:
        image_data = f.read()
    b64_image = base64.b64encode(image_data).decode()

    # Encodage de l'image du header
    with open("image.png", "rb") as f:
        header_img_data = f.read()
    b64_header_image = base64.b64encode(header_img_data).decode()

    st.markdown(
        f"""
        <style>
            [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"], .block-container {{
                padding: 0 !important;
                margin: 0 !important;
            }}
            [data-testid="stHeader"] {{
                display: none !important;
            }}
            .logo-container {{
                position: absolute;
                top: 5px;
                left: 5px;
                z-index: 9999;
            }}
            .full-width-header {{
                margin-top: 70px;
                width: 100vw;
                overflow: hidden;
                position: relative;
            }}
            .full-width-header img {{
                width: 100vw;
                height: auto;
                display: block;
              
            }}
            .header-text  {{
                position:absolute;
                top: 60%;
                left: 50%;
                font-size: 2.5rem;
                font-weight: bold;
                margin: 0;
                white-space: nowrap;
                width: 100%;
                text-overflow: ellipsis;
                transform: translate(-50%, -50%);
                color: black;
                text-align: center;
            }}
            .header-text p {{
                font-size: 1.5vw;
                margin: 0.1vw 0 0 0;
            }}

            .stFileUploader > div {{
                width: 100% !important;
                max-width: 500px;
                margin: 1.5rem auto 1rem auto;  /* Modifié */
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 10px;
            }}
            .upload-text {{
                font-size: 1.5rem;
                text-align: center;
                margin-top: 1.5rem;
                color: #333;
                font-weight: bold;
            }}
            .stButton > button {{
                background-color: #28a745;
                color: white;
                font-size: 1.2rem;
                font-weight: bold;
                border-radius: 8px;
                padding: 0.5rem 1.5rem;
                border: none;
                transition: background-color 0.3s ease;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .stButton {{
                display: flex !important;
                justify-content: center !important;
                margin: 0rem 0 1.5rem 0 !important;  /* Modifié */
            }}
            .stButton > button:hover {{
                background-color: #218838;
            }}
            .button-container {{
                display: flex;
                justify-content: space-evenly; /* Espacement entre les boutons */
                margin-top: 0.1rem;
                width: 100%;
            }}
            /* Style des boutons */
            .custom-button {{
                background-color: #C72828;
                color: white !important;
                padding: 1rem 1rem;  
                border-radius: 10px;
                border: none;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
                text-decoration: none;
                align-items: center;
                justify-content: center;
                text-align: center;
                font-size: 1rem;
                width: auto;  
                height: auto; 
             
            }}
            .custom-button:hover {{
                background-color: #008000;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
        </style>
        
        <div class="logo-container">
            <img src="data:image/png;base64,{b64_image}" style="height:50px; width:auto;">
        </div>
        
        <div class="full-width-header">
            <img src="data:image/png;base64,{b64_header_image}" style="height:13rem;">
            <div class="header-text">
                <h1>Mettre à jour votre base de données</h1>
                <p>Importez un fichier Excel pour mettre à jour la base de données.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_success_message(message):
   
     # Ajout du bouton "Accéder au dashboard" après le message de succès
    st.markdown(
        """
        <div class="button-container">
            <a href="?page=dashboard" class="custom-button" style="text-decoration:none;";>Accéder au dashboard</a>
        </div>
        """,
        unsafe_allow_html=True
    )

def send_file_to_server(uploaded_file):
    url = "http://127.0.0.1:5001/upload"
    files = {"file": uploaded_file}

    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            display_success_message("✅ Données importées avec succès!")
           

       
        else:
            error_msg = response.json().get("error", "Erreur inconnue")
            st.error(f"❌ Erreur lors de l'importation : {error_msg}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Impossible de se connecter au serveur Flask. Assurez-vous qu'il est en cours d'exécution.")

# Interface Streamlit
add_logo()
st.markdown('<div class="upload-text"></div>', unsafe_allow_html=True)

with st.container():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        uploaded_file = st.file_uploader("Choisir un fichier", type=["xlsx", "xls"], label_visibility="collapsed")

if uploaded_file is not None:
    if st.button("Enregistrer les données"):
        send_file_to_server(uploaded_file)


# Flask App
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = None

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier reçu"}), 400
        
        file = request.files["file"]

        try:
            df = pd.ExcelFile(file)
        except Exception as e:
            return jsonify({"error": f"Impossible de lire le fichier Excel : {str(e)}"}), 400

        save_path = "NVdata.xlsx"
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            for sheet_name in df.sheet_names:
                df.parse(sheet_name).to_excel(writer, sheet_name=sheet_name, index=False)
        # ✅ Exécuter traitement_data.py après l'enregistrement du fichier
        subprocess.run(["python", r"C:\Users\ennaa\Desktop\Hitachi_Astemo_Vf\traitement_data.py"])

        return jsonify({"message": "Fichier enregistré avec succès!"}), 200

    except Exception as e:
        return jsonify({"error": f"Erreur interne : {str(e)}"}), 500

def run_flask():
    app.run(port=5001, debug=True)

flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()