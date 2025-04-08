from datetime import datetime
import pandas as pd 
import os
import subprocess
# ✅ Exécuter traitement_data.py après l'enregistrement du fichier
        subprocess.run(["python", r"C:\Users\ennaa\Desktop\Hitachi_Astemo_Vf\server.py"])

# Charger le fichier Excel avec toutes les feuilles
file_path = 'NVdata.xlsx'

# Fonction pour nettoyer les noms de colonnes
def clean_column_names(df):
    df.columns = df.columns.str.lstrip("'")  # Supprime les apostrophes en début de nom de colonne
    return df

# Charger et nettoyer les feuilles
ekeh = clean_column_names(pd.read_excel(file_path, sheet_name='EKEH'))
ekek = clean_column_names(pd.read_excel(file_path, sheet_name='EKEK'))
ekbe = clean_column_names(pd.read_excel(file_path, sheet_name='EKBE'))
ekko = clean_column_names(pd.read_excel(file_path, sheet_name='EKKO'))
ekpo = clean_column_names(pd.read_excel(file_path, sheet_name='EKPO'))

# Sauvegarder les tables en CSV
ekeh.to_csv('EKEH2.csv', index=False)
ekek.to_csv('EKEK2.csv', index=False)
ekbe.to_csv('EKBE2.csv', index=False)
ekko.to_csv('EKKO2.csv', index=False)
ekpo.to_csv('EKPO2.csv', index=False)

#_____________________________________________________________________
import pandas as pd

# Charger les fichiers CSV
ekko = pd.read_csv("ekko2.csv", dtype=str)
ekpo = pd.read_csv("ekpo2.csv", dtype=str)

# Filtrer les données (supprimer les lignes où 'Code de suppression' == 'S')
ekko_filtre = ekko[ekko["Code de suppression"] != "S"]
ekpo_filtre = ekpo[ekpo["Code de suppression"] != "S"]

# Sauvegarder les fichiers filtrés
ekko_filtre.to_csv("EKKO2_filtre.csv", index=False)
ekpo_filtre.to_csv("EKPO2_filtre.csv", index=False)

print("Les fichiers filtrés ont été enregistrés avec succès.")
#______________________________________________________________________
import pandas as pd

# Charger le fichier CSV
ekeh = pd.read_csv("ekeh2.csv")

# Vérifier que les colonnes existent dans le fichier
if "Quantité échéancée" in ekeh.columns and "Quantité livrée" in ekeh.columns:
    # Ajouter la colonne QTE
    ekeh["QTE"] = ekeh["Quantité échéancée"] - ekeh["Quantité livrée"]
    
    # Sauvegarder le fichier modifié
    ekeh.to_csv("ekeh2.csv", index=False, encoding="utf-8")
    
    print("Colonne 'QTE' ajoutée avec succès dans 'ekeh2.csv' !")
else:
    print("Erreur : Vérifiez que les colonnes 'Quantité échéancée' et 'Quantité livrée' existent dans le fichier.")
#______________________________________________________________________
import pandas as pd

# Lire le fichier CSV
df = pd.read_csv("ekbe2.csv")

# Trier les données par "Document d'achat" et "Poste", puis par "Date comptable" croissante
df.sort_values(by=["Document d'achat", "Poste", "Date comptable"], ascending=[True, True, True], inplace=True)

# Identifier les "Document référence" associés à un Code mouvement == 102, mais en excluant les NaN
docs_a_supprimer = df.loc[(df["Code mouvement"] == 102) & (df["Document référence"].notna()), "Document référence"]

# Supprimer toutes les lignes où "Document référence" est dans cette liste, mais en excluant les NaN
df_filtre = df[~df["Document référence"].isin(docs_a_supprimer) | df["Document référence"].isna()]

# Identifier les lignes où Code mouvement == 102 et Document référence est NaN
lignes_102_vides = df_filtre[(df_filtre["Code mouvement"] == 102) & (df_filtre["Document référence"].isna())]

# Liste des index des lignes à supprimer
index_a_supprimer = set()

# Parcourir chaque ligne concernée
for index, ligne in lignes_102_vides.iterrows():
    poste = ligne["Poste"]
    date_102 = ligne["Date comptable"]
    quantite_a_supprimer = ligne["Quantité"]
    
    # Filtrer les lignes précédentes avec le même poste et une date antérieure
    lignes_precedentes = df_filtre[(df_filtre["Poste"] == poste) & (df_filtre["Date comptable"] == date_102)]
    lignes_precedentes = lignes_precedentes.sort_values(by="Date comptable", ascending=False)
    
    quantite_cumulee = 0
    
    for idx, ligne_prec in lignes_precedentes.iterrows():
        quantite_cumulee += ligne_prec["Quantité"]
        index_a_supprimer.add(idx)
        if quantite_cumulee >= quantite_a_supprimer:
            break
    
    # Ajouter aussi la ligne 102 à supprimer
    index_a_supprimer.add(index)

# Supprimer les lignes identifiées
df_filtre = df_filtre.drop(index=index_a_supprimer)

# Enregistrer le fichier filtré
df_filtre.to_csv("ekbe2_filtre.csv", index=False)

print("✅ Le fichier filtré a été enregistré sous 'ekbe2_filtre.csv'")
#________________________________________________________________________
import pandas as pd

# Charger le fichier CSV
df = pd.read_csv("ekbe2_filtre.csv")

# Définir les colonnes pour le regroupement
colonnes_groupe = ["Document d'achat", "Poste", "Date comptable", "Référence"]

# Calculer la somme des quantités par groupe
df["Quantité"] = df.groupby(colonnes_groupe)["Quantité"].transform("sum")

# Supprimer les doublons pour garder une seule ligne par groupe
df = df.drop_duplicates(subset=colonnes_groupe)

# Enregistrer le fichier modifié
df.to_csv("ekbe2_filtre2.csv", index=False)

print("Traitement terminé, fichier enregistré sous 'ekbe2_filtre2.csv'")
#_______________________________________________________________________
import pandas as pd

# Charger les fichiers CSV en tant que chaînes de caractères
ekeh = pd.read_csv('ekeh2.csv', dtype=str)
ekek = pd.read_csv('ekek2.csv', dtype=str)
ekko = pd.read_csv('ekko2_filtre.csv', dtype=str)
ekpo = pd.read_csv('ekpo2_filtre.csv', dtype=str)

# Nettoyer les noms de colonnes pour éviter les problèmes d'espacement ou de caractères invisibles
for df in [ekeh, ekek, ekko, ekpo]:
    df.columns = df.columns.str.strip()

# Convertir les colonnes de date en format datetime
ekeh['Date livraison'] = pd.to_datetime(ekeh['Date livraison'], errors='coerce')
ekek['Date de transmission appel'] = pd.to_datetime(ekek['Date de transmission appel'], errors='coerce')
ekek['Dernière date EM'] = pd.to_datetime(ekek['Dernière date EM'], errors='coerce')

# Trier EKEH par 'Date livraison' (ordre croissant)
ekeh_sorted = ekeh.sort_values(by='Date livraison', ascending=True)

# Fusionner EKEH avec EKKO pour ajouter le Fournisseur (via Document d'achat)
ekeh = ekeh.merge(ekko[['Document d\'achat', 'Fournisseur']], on='Document d\'achat', how='left')

# Remplacer les valeurs manquantes
ekeh = ekeh.fillna({'Document d\'achat': 'Inconnu', 'Poste': 'Inconnu', 'Fournisseur': 'Inconnu'})

# Convertir 'QTE' en numérique
ekeh['QTE'] = pd.to_numeric(ekeh['QTE'], errors='coerce').fillna(0)

# Conversion de 'Nº d'appel' en numérique
ekeh['Nº d\'appel'] = pd.to_numeric(ekeh['Nº d\'appel'], errors='coerce')
ekek['Nº d\'appel'] = pd.to_numeric(ekek['Nº d\'appel'], errors='coerce')

ekeh_sorted.to_csv('ekeh_sorted.csv', index=False, encoding='utf-8')

# Liste pour stocker les résultats
resultats = []

# Grouper par Fournisseur puis Document d'achat puis Poste
for (fournisseur, doc_achat, poste), group in ekeh.groupby(['Fournisseur', 'Document d\'achat', 'Poste']):
    for date_livraison, sub_group in group.groupby('Date livraison'):
        # Sélectionner le plus grand (max) Nº d'appel pour chaque groupe de date de livraison
        max_num_appel = sub_group["Nº d'appel"].max()

        # Filtrer toutes les lignes ayant ce même Nº d'appel
        appels_group = sub_group[sub_group["Nº d'appel"] == max_num_appel]

        # Somme des QTE pour ce numéro d'appel
        total_qte = appels_group['QTE'].sum()
       
        # Chercher la ligne correspondante dans EKEK
        ekek_row = ekek[ekek['Nº d\'appel'] == max_num_appel]

        if not ekek_row.empty:
            # Filtrer ekek pour avoir les lignes correspondant au même Document d'achat, Poste, et Nº d'appel
            ekek_filtered = ekek[(ekek['Document d\'achat'] == doc_achat) & 
                                 (ekek['Poste'] == poste) & 
                                 (ekek['Nº d\'appel'] == max_num_appel)]
            
            # Prendre la dernière 'Dernière date EM' parmi les lignes filtrées
            if not ekek_filtered.empty:
                derniere_em = ekek_filtered['Dernière date EM'].max()  # Prendre la plus récente
                date_transmission = ekek_filtered['Date de transmission appel'].values[0]  # Date de transmission correspondante
            else:
                date_transmission = None
                derniere_em = None
        else:
            date_transmission = None
            derniere_em = None

        # Récupérer l'Article depuis EKPO
        article_row = ekpo[(ekpo['Document d\'achat'] == doc_achat) & (ekpo['Poste'] == poste)]
        article = article_row['Article'].values[0] if not article_row.empty else 'Inconnu'

        # Ajouter les résultats à la liste
        resultats.append([fournisseur, doc_achat, poste, article, max_num_appel, date_livraison, total_qte, date_transmission, derniere_em])

# Convertir la liste en DataFrame
df_resultats = pd.DataFrame(resultats, columns=["Fournisseur", "Document d'achat", "Poste", "Article", "Nº d'appel", "Date livraison", "QTE", "Date de transmission appel", "Dernière date EM"])

# Sauvegarder dans un fichier unique
df_resultats.to_csv('resultats_final_1.csv', index=False, encoding="utf-8")

print("✅ Fichier unique 'resultats_final1.csv' généré avec succès !")
#__________________________________________________________________________
# Charger le fichier principal
resultats_file = "resultats_final_1.csv"
df = pd.read_csv(resultats_file, parse_dates=["Date livraison", "Date de transmission appel"])

# Vérifier si les colonnes nécessaires existent avant de continuer
if "Date livraison" in df.columns and "Date de transmission appel" in df.columns:
    # Calculer la différence en jours
    df["Diff_jours"] = (df["Date livraison"] - df["Date de transmission appel"]).dt.days

    # Filtrer les lignes où la différence est <= 14 jours
    df_filtre = df[df["Diff_jours"] <= 14].drop(columns=["Diff_jours"])

    # Enregistrer le fichier filtré
    resultats_filtre_file = "resultats_final_filtre.csv"
    df_filtre.to_csv(resultats_filtre_file, index=False, encoding="utf-8")

    print(f"✅ Le fichier filtré a été enregistré sous '{resultats_filtre_file}'")
else:
    print("⚠️ Erreur : Les colonnes 'Date livraison' et 'Date de transmission appel' sont manquantes dans le fichier.")
#___________________________________________________________________________
import pandas as pd

# Charger les fichiers
resultats_file = "resultats_final_filtre.csv"
ekeb_file = "ekbe2_filtre2.csv"

# Charger les fichiers CSV
resultats_df = pd.read_csv(resultats_file, delimiter=",", dtype=str)
ekeb_df = pd.read_csv(ekeb_file, delimiter=",", dtype=str)

# Nettoyage des noms de colonnes
resultats_df.columns = resultats_df.columns.str.strip()
ekeb_df.columns = ekeb_df.columns.str.strip()

# Conversion des dates
resultats_df['Dernière date EM'] = pd.to_datetime(resultats_df['Dernière date EM'], errors='coerce')
resultats_df['Date livraison'] = pd.to_datetime(resultats_df['Date livraison'], errors='coerce')
ekeb_df['Date comptable'] = pd.to_datetime(ekeb_df['Date comptable'], errors='coerce')

# Vérification et conversion des valeurs numériques
resultats_df['QTE'] = pd.to_numeric(resultats_df['QTE'], errors='coerce').fillna(0)
ekeb_df['Quantité'] = pd.to_numeric(ekeb_df['Quantité'], errors='coerce').fillna(0)

# Fonction de traitement de chaque ligne
def traiter_ligne(row):
    date_em = row['Dernière date EM']
    quantite_echange = row['QTE']
    date_livraison = row['Date livraison']
    document_achat = row['Document d\'achat']  # Ajoutez ici le nom de la colonne du document d'achat
    poste = row['Poste']  # Ajoutez ici le nom de la colonne du poste

    # Vérifier si la "Dernière date EM" existe dans "Date comptable" pour le même document d'achat et le même poste
    ekeb_filtered_check = ekeb_df[(ekeb_df['Date comptable'] == date_em) & 
                                  (ekeb_df['Document d\'achat'] == document_achat) & 
                                  (ekeb_df['Poste'] == poste)]

    if ekeb_filtered_check.empty:
        return pd.Series(['Date EM absente', None, None])  # Si absente, on retourne des valeurs par défaut

    # Filtrer les lignes de ekeb_df qui ont une date comptable après la date EM ET qui correspondent au document d'achat et au poste
    ekeb_filtered = ekeb_df[(ekeb_df['Date comptable'] > date_em) & 
                            (ekeb_df['Document d\'achat'] == document_achat) & 
                            (ekeb_df['Poste'] == poste)]

    # Initialisation des variables
    quantite_cumulee = 0
    date_associee = None
    quantite_corrigee = 0

    for _, ekeb_row in ekeb_filtered.iterrows():
        quantite_cumulee += ekeb_row['Quantité']
        
        # Si la quantité cumulée dépasse ou atteint la quantité échangée, on arrête le cumul
        if quantite_cumulee >= quantite_echange:
            date_associee = ekeb_row['Date comptable']
            quantite_corrigee = quantite_cumulee - quantite_echange  # Calcul de la quantité corrigée
            break

    # Vérification de la date associée et de la livraison
    if date_associee is not None:
        difference_jours = (date_associee - date_livraison).days
        if difference_jours > 0:
            statut = f'Livraison en retard de {difference_jours} jours'
        elif difference_jours < 0:
            statut = f'Livraison en avance de {-difference_jours} jours'
        else:
            statut = 'Livraison à la date prévue'
    else:
        statut = 'Quantité non trouvée'
        difference_jours = None

    return pd.Series([statut, quantite_corrigee, difference_jours])

# Appliquer la fonction de traitement
resultats_df[['Statut livraison', 'Quantité corrigée', 'Différence jours']] = resultats_df.apply(traiter_ligne, axis=1)

# Enregistrer les résultats dans un nouveau fichier
output_file = "statut_QTE_final.csv"
resultats_df.to_csv(output_file, index=False, sep=";", encoding="utf-8")

print(f"✅ Le fichier final '{output_file}' a été généré avec succès !")
