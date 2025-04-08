import streamlit as st
from streamlit import session_state as state
import base64
import subprocess


# Configuration de la page
st.set_page_config(
    page_title="Astemo - Plateforme Fournisseurs",
    layout="wide",
    initial_sidebar_state="collapsed"
)
query_params = st.query_params.to_dict()
if "page" in query_params:
    if query_params["page"] == "dashboard":
        st.switch_page("pages/dashboard.py")
    elif query_params["page"] == "data-entry":
        st.switch_page("pages/NouveauData.py")
def add_logo():
    # Encodage logo
    with open("logo.png", "rb") as f:
        image_data = f.read()
    b64_image = base64.b64encode(image_data).decode()
    
    # Encodage header image
    with open("image.png", "rb") as f:
        header_img_data = f.read()
    b64_header_image = base64.b64encode(header_img_data).decode()

    st.markdown(
        f"""
        <style>
            /* Supprime tous les paddings/marges de la page */
            [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"], .block-container {{
                padding: 0 !important;
                margin: 0 !important;
            }}
            [data-testid="stHeader"] {{
                display: none !important;
            }}

            /* Conteneur du logo */
            .logo-container {{
                position: absolute;
                top: 5px;
                left: 5px;
                z-index: 9999;
            }}

            /* Image pleine largeur */
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

            /* Texte centré sur l'image */
             .header-text  {{
                 position:absolute;
                top: 60%;
                left: 50%;
                font-size: 2.5rem; /* Taille fixe en rem */
                font-weight: bold;
                margin: 0;
                white-space: nowrap; /* Empêche le retour à la ligne */
                width: 100%;
                text-overflow: ellipsis;
                transform: translate(-50%, -50%);
                color: black;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }}
            .header-text h1 {{
                font-size: 3vw;
                font-weight: bold;
                margin: 0;
            }}
            .header-text p {{
                font-size: 1.5vw;
                margin: 0.1vw 0 0 0;
            }}

            /* Ajustement pour petits écrans */
            @media (max-width: 320px) {{
                .header-text h1 {{
                    font-size: 1.1rem;
                }}
                .header-text p {{
                    font-size: 0.6rem;
                }}
            }}
            
            /* Conteneur des boutons */
            .button-container {{
                display: flex;
                justify-content: space-evenly; /* Espacement entre les boutons */
                margin-top: 110px;
                width: 100%;
            }}

            /* Style des boutons */
            .custom-button {{
                background-color: #C72828;
                color: white !important;
                padding: 1rem 1rem;  /* Taille augmentée des boutons */
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
                width: 20 rem;  /* Largeur fixe des boutons */
                height: auto;  /* Hauteur ajustée en fonction du contenu */
            }}

            .custom-button:hover {{
                background-color: #008000;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}

            /* Texte en bas de page */
            .footer-text {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                text-align: center;
                padding: 10px 0;
                margin: 0;
                background-color: white; /* Ajoutez une couleur de fond si nécessaire */
                z-index: 1000;
                font-size: 1rem;
                color: black;
                background-color: #f8f9fa;
            }}
        </style>
        
        <!-- Logo en haut à gauche -->
        <div class="logo-container">
            <img src="data:image/png;base64,{b64_image}" style="height:50px; width:auto;">
        </div>
        
        <!-- Bandeau plein écran avec texte centré -->
        <div class="full-width-header">
            <img src="data:image/png;base64,{b64_header_image}" style="height:13rem;">
            <div class="header-text">
                <h1>Plateforme de gestion des données des fournisseurs</h1>
                <p>Optimisez votre gestion de données industrielles grâce à notre plateforme sécurisée et intuitive.</p>
            </div>
        </div>
        
        <!-- Conteneur des boutons -->
        <div class="button-container">
            <a href="?page=dashboard" class="custom-button" style="text-decoration:none;">Accéder au Dashboard</a>
            <a href="?page=data-entry" class="custom-button" style="text-decoration:none;">Entrer une nouvelle donnée</a>
        </div>
        
        <!-- Texte en bas de page -->
        <div class="footer-text">
            © 2025 Astemo Angers
        </div>
        """,
        unsafe_allow_html=True
    )

add_logo()
subprocess.run(["python", r"C:\Users\ennaa\Desktop\Hitachi_Astemo_Vf\server.py"])