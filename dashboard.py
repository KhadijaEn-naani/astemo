import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO

# Configuration de la page
st.set_page_config(page_title="Dashboard", layout="wide")

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Charger les images
left_image_base64 = get_image_base64("logo.png")
right_image_base64 = get_image_base64("icon1.png")

# CSS personnalisé
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        body, .stApp {background-color: #F1F1F1 !important;}
        .header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #E5E5E5;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        }
        .header img {height: 40px;}
        .header h1 {flex-grow: 1; text-align: center; color: #B61818; font-size: 26px; font-weight: bold; margin: 0;}
        @media (max-width: 730px) {
            .header h1 {font-size: 16px;}
            .header img {height: 25px;}
        }
        .spacer {
            margin-top: 70px;
        }
        .stPlotlyChart {
            display: flex;
            justify-content: center;
            border-radius:10px !important;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            align-items: center;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Affichage de la bannière
st.markdown(f"""
    <div class="header">
        <img src="data:image/png;base64,{left_image_base64}" alt="Logo Gauche">
        <h1>Visualisation de l'Impact des Fournisseurs</h1>
        <img src="data:image/png;base64,{right_image_base64}" alt="Logo Droite">
    </div>
    <div class="spacer"></div>
""", unsafe_allow_html=True)

# Chargement des données
df = pd.read_csv("statut_QTE_final.csv", delimiter=";", dtype=str)
df["Date livraison"] = pd.to_datetime(df["Date livraison"], errors="coerce")
df["Date de transmission appel"] = pd.to_datetime(df["Date de transmission appel"], errors="coerce")
df["QTE"] = pd.to_numeric(df["QTE"], errors="coerce")
df["Différence jours"] = pd.to_numeric(df["Différence jours"], errors="coerce") 

# Initialisation des filtres
df_filtered = df.copy()

# Filtres dynamiques dans l'ordre hiérarchique
with st.sidebar:
    # Filtre Fournisseur
    fournisseur_options = df_filtered["Fournisseur"].unique()
    fournisseur_select = st.multiselect("Sélectionner un ou plusieurs fournisseurs :", fournisseur_options)
    if fournisseur_select:
        df_filtered = df_filtered[df_filtered["Fournisseur"].isin(fournisseur_select)]
    
    # Filtre Document d'achat
    doc_achat_options = df_filtered["Document d'achat"].unique()
    doc_achat_select = st.multiselect("Sélectionner un ou plusieurs documents d'achat :", doc_achat_options)
    if doc_achat_select:
        df_filtered = df_filtered[df_filtered["Document d'achat"].isin(doc_achat_select)]
    
    # Filtre Poste
    poste_options = df_filtered["Poste"].unique()
    poste_select = st.multiselect("Sélectionner un ou plusieurs postes :", poste_options)
    if poste_select:
        df_filtered = df_filtered[df_filtered["Poste"].isin(poste_select)]
    
    # Filtre Article
    article_options = df_filtered["Article"].unique()
    article_select = st.multiselect("Sélectionner un ou plusieurs articles :", article_options)
    if article_select:
        df_filtered = df_filtered[df_filtered["Article"].isin(article_select)]
    
    # Filtre Date
    date_filter_type = st.selectbox("Choisir le type de filtre de date :", ["Plage de dates", "Année", "Mois"])
    
    if date_filter_type == "Plage de dates":
        date_min = df_filtered["Date livraison"].min()
        date_max = df_filtered["Date livraison"].max()
        date_range = st.date_input("Sélectionner une plage de dates :", [date_min, date_max], min_value=date_min, max_value=date_max)
        if isinstance(date_range, list) and len(date_range) == 2:
            date_start = pd.to_datetime(date_range[0])
            date_end = pd.to_datetime(date_range[1])
            df_filtered = df_filtered[(df_filtered["Date livraison"] >= date_start) & (df_filtered["Date livraison"] <= date_end)]
    
    elif date_filter_type == "Année":
        years = df_filtered["Date livraison"].dt.year.unique()
        selected_year = st.selectbox("Sélectionner une année :", years)
        df_filtered = df_filtered[df_filtered["Date livraison"].dt.year == selected_year]
    
    elif date_filter_type == "Mois":
        years = df_filtered["Date livraison"].dt.year.unique()
        selected_year = st.selectbox("Sélectionner une année :", years)
        months = df_filtered[df_filtered["Date livraison"].dt.year == selected_year]["Date livraison"].dt.month.unique()
        selected_month = st.selectbox("Sélectionner un mois :", months)
        df_filtered = df_filtered[(df_filtered["Date livraison"].dt.year == selected_year) & 
                                 (df_filtered["Date livraison"].dt.month == selected_month)]

def determine_status(row):
    diff = row["Différence jours"]
    if pd.isna(diff):
        return "Non spécifié"
    elif diff > 0:
        return "En retard"
    elif diff < 0:
        return "En avance"
    else:
        return "À l'heure"

df_filtered["Statut Livraison"] = df_filtered.apply(determine_status, axis=1)

if df_filtered.empty:
    st.markdown("<h3 style='text-align: center; color: black;'>Aucune donnée disponible après filtrage</h3>", unsafe_allow_html=True)
    st.stop()

# Affichage des données
st.subheader("📋 Données filtrées :")
st.dataframe(df_filtered.reset_index(drop=True), height=300, use_container_width=True)

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        writer.close()
    return output.getvalue()

st.download_button(
    label="📥 Télécharger les données en Excel",
    data=convert_df_to_excel(df_filtered),
    file_name="donnees_filtrees.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Première ligne de graphiques
col1, col2 = st.columns(2)
with col1:
    status_counts = df_filtered["Statut Livraison"].value_counts().reset_index()
    status_counts.columns = ["Statut", "Nombre de livraisons"]
    
    color_map = {"En retard": "red", "À l'heure": "green", "En avance": "black"}
    fig1 = px.bar(status_counts, x="Statut", y="Nombre de livraisons", 
                 color="Statut", color_discrete_map=color_map, text_auto=True)
    fig1.update_layout(title_text="<u>Répartition des Livraisons par Statut</u>", 
                      title_x=0.1, height=350, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    delay_counts = df_filtered["Différence jours"].value_counts(normalize=True).sort_index().reset_index()
    delay_counts.columns = ["J+/-x", "Pourcentage"]
    delay_counts["Pourcentage"] *= 100
    fig2 = px.bar(delay_counts, x="J+/-x", y="Pourcentage")
    fig2.update_layout(title_text="<u>Échéances reçues à J+/-x</u>", 
                      title_x=0.1, height=350, yaxis_tickformat=".1f%")
    st.plotly_chart(fig2, use_container_width=True)

# Deuxième ligne avec graphique et tableau côte à côte
col3, col4 = st.columns(2)

with col3:
    advance = len(df_filtered[df_filtered["Différence jours"] < 0])
    on_time = len(df_filtered[df_filtered["Différence jours"] == 0])
    j1 = len(df_filtered[df_filtered["Différence jours"] == 1])
    j2 = len(df_filtered[df_filtered["Différence jours"] == 2])
    j3 = len(df_filtered[df_filtered["Différence jours"] == 3])
    j4plus = len(df_filtered[df_filtered["Différence jours"] >= 4])

    delivery_data = {
        "Avance": advance,
        "J": on_time,
        "J+1": j1,
        "J+2": j2,
        "J+3": j3,
        "J>=4": j4plus
    }
    performance_colors = {
        "A": "#006400",  # Vert foncé
        "B": "#32CD32",  # Vert clair
        "C": "#90EE90",  # Vert pâle
        "D": "#98FB98",  # Vert très clair
        "E": "#FF0000"   # Rouge
    }

    total = sum(delivery_data.values())
    performance = "E"
    performance_text = "Reste"
    
    if total > 0:
        if (on_time/total) >= 0.95: 
            performance = "A"
            performance_text = "95%+ à J (Excellent)"
        elif (on_time/total) >= 0.85: 
            performance = "B"
            performance_text = "85%+ à J (Bon)"
        elif ((on_time + advance)/total) >= 0.85: 
            performance = "C"
            performance_text = "85%+ à J/avance (Moyen)"
        elif ((on_time + advance + j1)/total) >= 0.85: 
            performance = "D"
            performance_text = "85%+ à J+1 (Acceptable)"

    fig3 = go.Figure(data=[go.Pie(
        labels=list(delivery_data.keys()),
        values=list(delivery_data.values()),
        hole=0.6,
        marker=dict(colors=["black", "green", "yellow", "orange", "purple", "red"]))])
    
    fig3.add_annotation(
        text=f"<b style='color:{performance_colors[performance]}'>{performance}</b>",
        font_size=40,
        showarrow=False,
        x=0.5,
        y=0.5,
        xanchor="center",
        yanchor="middle"
    )
  
    fig3.update_layout(
        title_text="<u>Répartition par Catégories de Jours</u>", 
        height=350,
        title_x=0.1,
        margin=dict(t=80, b=80)
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(f"<div style='text-align: center; margin-top: -50px;'><strong>{performance}</strong> : {performance_text}</div>", unsafe_allow_html=True)

with col4:
    st.markdown("<h4><u>Tableau Récapitulatif</u></h4>", unsafe_allow_html=True)
    df_filtered["Statut"] = df_filtered["Différence jours"].apply(
        lambda x: "En retard" if x > 0 else "À l'heure" if x == 0 else "En avance"
    )
    summary_df = df_filtered[['Fournisseur', 'Article', 'Date livraison', 'QTE', 'Différence jours', 'Statut']]
    summary_df = summary_df.rename(columns={
        "QTE": "Quantité Échéance",
        "Différence jours": "Écart Jours"
    })
    st.dataframe(summary_df, height=220, use_container_width=True)
    st.download_button(
        label="📥 Télécharger ce tableau en Excel",
        data=convert_df_to_excel(summary_df),
        file_name="recapitulatif_livraisons.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Section analyse de couverture
st.markdown("<h4><u>Analyse de Couverture des Stocks</u></h4>", unsafe_allow_html=True)

delay_distribution = df_filtered["Différence jours"].value_counts(normalize=True).sort_index().cumsum().reset_index()
delay_distribution.columns = ["Jours", "Couverture"]
delay_distribution["Couverture"] *= 100

col_config, col_chart = st.columns([1, 2])

with col_config:
    st.markdown("""
    <style>
        .stTextInput>div>div>input {
            background-color: #66666615 !important;
            padding: 8px !important;
            border-radius: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    securisation_input = st.text_input(
        "**Niveau de sécurisation souhaité (%)**",
        value="80.0",
        help="Entrez un pourcentage entre 0 et 100 (ex: 85.5) pour définir le niveau de couverture souhaité"
    )
    
    try:
        securisation = float(securisation_input)
        if securisation < 0:
            st.warning("La valeur ne peut pas être négative. Réglage à 0%.")
            securisation = 0.0
        elif securisation > 100:
            st.warning("La valeur ne peut pas dépasser 100%. Réglage à 100%.")
            securisation = 100.0
    except ValueError:
        st.warning("Saisie invalide. Utilisation de la valeur par défaut (80.0%).")
        securisation = 80.0

    try:
        jours_necessaires = delay_distribution[delay_distribution["Couverture"] >= securisation]["Jours"].min()
        couverture_reelle = delay_distribution[delay_distribution["Jours"] == jours_necessaires]["Couverture"].values[0]
    except:
        jours_necessaires = delay_distribution["Jours"].max()
        couverture_reelle = delay_distribution["Couverture"].max()

    st.markdown("<br>", unsafe_allow_html=True)
    st.metric(
        label="**Jours de stock nécessaires**",
        value=f"{jours_necessaires} jours",
        help="Nombre de jours de stock requis pour atteindre la couverture souhaitée"
    )
    st.caption(f"**Couverture réelle obtenue :** {couverture_reelle:.1f}%")

with col_chart:
    fig = px.line(
        delay_distribution, 
        x="Jours", 
        y="Couverture",
        markers=True,
        height=250,
    )
    fig.update_layout(
        title_text=f"<u>Couverture cumulative à {securisation}%</u>",
        title_x=0.1,
        title_font=dict(size=16)
    )
    
    fig.add_shape(
        type="line",
        x0=0, y0=securisation,
        x1=jours_necessaires, y1=securisation,
        line=dict(color="red", dash="dot")
    )
    
    fig.add_annotation(
        x=jours_necessaires,
        y=securisation,
        text=f"{jours_necessaires} jours → {couverture_reelle:.1f}%",
        showarrow=True,
        arrowhead=1,
        bgcolor="white"
    )
    
    st.plotly_chart(fig, use_container_width=True)