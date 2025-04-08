==============================
📦 GUIDE COMPLET DU PROJET
==============================

# 📊 Application Web : Analyse et Visualisation de Données avec Streamlit & Flask

Ce projet est une application interactive développée avec **Streamlit** pour l'interface utilisateur et **Flask** pour le backend, destinée à visualiser et traiter des fichiers de données (Excel, CSV) de manière intuitive.

------------------------------
📁 STRUCTURE DU PROJET
------------------------------
📦 MonProjet/
├── Acceuil.py                # Script principal Streamlit à lancer
├── server.py                 # Serveur Flask (optionnel)
├── traitement_data.py        # Fonctions de traitement
├── NVdata.xlsx               # Données Excel
├── statut_QTE_final.csv      # Données CSV
├── logo.png / image.png / icon1.png  # Images utilisées
├── pages/                    # Pages Streamlit supplémentaires
├── requirements.txt          # Fichier des dépendances

------------------------------
🚀 LANCEMENT EN LOCAL
------------------------------
1️⃣ Cloner le dépôt :

    git clone https://github.com/KhadijaEn-naani/astemo.git
    cd astemo

2️⃣ Installer les dépendances :

    pip install -r requirements.txt

3️⃣ Lancer l'application :

    streamlit run Acceuil.py

------------------------------
🌐 DÉPLOIEMENT GRATUIT (CLOUD)
------------------------------
Tu peux déployer cette application gratuitement sur :

✅ Streamlit Cloud : https://streamlit.io/cloud  
→ Idéal si tu utilises uniquement Streamlit.

✅ Render ou Railway (Flask + Streamlit)  
→ Exemple de Procfile pour Render :

    web: streamlit run Acceuil.py --server.port=8000 --server.address=0.0.0.0

------------------------------
📦 REQUIREMENTS.TXT
------------------------------
streamlit  
pandas  
plotly  
matplotlib  
flask  
openpyxl  
requests  

------------------------------
📄 PROCFILE (pour Render / Railway)
------------------------------
web: streamlit run Acceuil.py --server.port=8000 --server.address=0.0.0.0

------------------------------
🚫 .GITIGNORE
------------------------------
__pycache__/  
*.pyc  
.env  
env/  
*.xlsx  
*.csv  
*.log  
.DS_Store  

------------------------------
🧑‍💻 AUTEURE
------------------------------
**Khadija EN-NAANI**  
Étudiante en ingénierie des données et intelligence artificielle  
Double diplomation en Qualité, Fiabilité et Innovation  
Passionnée par la Data Science, l’IA et la Visualisation de données

------------------------------
📸 APERÇU
------------------------------
![image](https://github.com/user-attachments/assets/1523ab86-cd6f-4617-8fee-259d4f3f61ac)
![image](https://github.com/user-attachments/assets/b6e69c70-43f0-4b1d-9f36-7f628bc7267d)
![image](https://github.com/user-attachments/assets/3022346b-21a6-4fc1-98b4-7bbb6ae49c51)
💬
