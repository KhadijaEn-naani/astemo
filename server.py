from flask import Flask, request, jsonify
import pandas as pd
from openpyxl import load_workbook
import subprocess

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier reçu"}), 400
        
        file = request.files["file"]

        # Charger le fichier Excel
        try:
            df = pd.ExcelFile(file)
        except Exception as e:
            return jsonify({"error": f"Impossible de lire le fichier Excel : {str(e)}"}), 400

        # Enregistrement du fichier
        save_path = "NVdata.xlsx"
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            for sheet_name in df.sheet_names:
                df.parse(sheet_name).to_excel(writer, sheet_name=sheet_name, index=False)
        # ✅ Exécuter traitement_data.py après l'enregistrement du fichier
        subprocess.run(["python", r"C:\Users\ennaa\Desktop\Hitachi_Astemo_Vf\traitement_data.py"])
        return jsonify({"message": "Fichier enregistré avec succès!"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erreur interne : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True,use_reloader=False)
