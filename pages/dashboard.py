import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(page_title="Dashboard", layout="wide",initial_sidebar_state="collapsed")

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def load_data():
    try:
        df = pd.read_csv("statut_QTE_final.csv", sep=';')
        date_columns = ['Date livraison', 'Date de transmission appel', 'Dernière date EM']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        numeric_columns = ['QTE', 'Quantité corrigée', 'Différence jours']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

def calculate_kpis(df):
    kpis = {}
    kpis['nombre_fournisseurs'] = len(df['Fournisseur'].unique())
    
    # Supprimer les lignes sans valeur dans 'Différence jours'
    df_valid = df[df['Différence jours'].notna()]

    # Filtrer les livraisons conformes (Différence jours <= 0)
    livraisons_conformes = df_valid[df_valid['Différence jours'] <= 0]

    # Calculer le taux
    kpis['taux_livraison_conforme'] = round((len(livraisons_conformes) / len(df_valid)) * 100, 2) if len(df_valid) > 0 else 0

    retards = df[df['Différence jours'].notna() & (df['Différence jours'] > 0)]['Différence jours']

# Calculer la moyenne
    kpis['retard_moyen'] = round(retards.mean(), 1) if not retards.empty else 0     
    #df_with_qty = df.dropna(subset=['QTE', 'Quantité corrigée'])
    # Calcul des quantités livrées
   # df_with_qty['Quantité livrée'] = df_with_qty['QTE'] - df_with_qty['Quantité corrigée'].fillna(0)

# Calcul du taux de complétion en pourcentage
   # On évite la division par zéro
    #df_with_qty_filtered = df_with_qty[df_with_qty['QTE'] != 0]

    # Calcul du taux de complétion
   # df_with_qty_filtered['taux_completion'] = (df_with_qty_filtered['Quantité livrée'] / df_with_qty_filtered['QTE']) * 100

    # Moyenne du taux de complétion
    #kpis['taux_completion'] = round(df_with_qty_filtered['taux_completion'].mean(), 2)
    #problemes_em = df[df['Statut livraison'].str.contains('EM', case=False, na=False)].shape[0]
    problemes_em = df[df['Différence jours'].isna() | (df['Différence jours'] == '')].shape[0]
    kpis['problemes_em'] = problemes_em
    
    return kpis

def convert_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Charger les images
left_image_base64 = get_image_base64("logo.png")
right_image_base64 = get_image_base64("icon1.png")

# CSS personnalisé
st.markdown("""
    <style>
        html, body, .stApp {
            background-color: #F1F1F1 !important;
            margin: 0;
            padding: 0;
        }
        .stApp > header { display: none !important; }
        #MainMenu, header, footer { visibility: hidden; }
        
        .block-container, .appview-container .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
            max-width: 100%;
        }
        .title {
            font-size: 10px !important;
            text-decoration: underline ;
        }
        .header-container, .main-container {
            width: 80% !important;
            margin: 0 auto !important;
            display: flex;
            justify-content: center;
            padding-top: 0;
        }
        
        .header {
            background-color: #E5E5E5;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .header h1{
            color:#B61818;
            margin:0;
            text-align:center;
            font-size: 26px;
        }
        
        .download-button {
            width: 100% !important;
            margin-top: 15px !important;
        }
        
        .indicateurs-container {
            background-color: #E5E5E5;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .indicateur {
            background-color: #FAF9F6;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .indicateur-titre {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .indicateur-valeur {
            color: #B61818;
            font-size: 18px;
        }
         @media (max-width: 800px) {
            .header-container { width: 95%; }
            .header h1 {font-size: 16px;}
            .header img {height: 25px;}
            .indicateurs { flex-direction: column; }
        }
         @media (max-width: 500px) {
            .header-container { width: 95%; }
            .header h1 {font-size: 14px;}
            .header img {height: 20px;}
            .indicateurs { flex-direction: column; }
        }
        .indicateurs-title {
            font-size: 20px;
            font-weight: bold;
            text-decoration: underline;
            margin-bottom: 10px;
            text-align:center;
        }
    </style>
""", unsafe_allow_html=True)

# Structure principale
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Entête
st.markdown(f"""
    <div class="header">
        <img src="data:image/png;base64,{left_image_base64}" height="40">
        <h1><u>Visualisation de l'Impact des Fournisseurs<U></h1>
        <img src="data:image/png;base64,{right_image_base64}" height="40">
    </div>
""", unsafe_allow_html=True)

# Chargement des données
df = load_data()

# Application des filtres dynamiques
df_filtered = df.copy()

with st.sidebar:
    st.header("Filtres")

    # Filtre Fournisseur
    fournisseur_options = df_filtered["Fournisseur"].dropna().unique()
    fournisseur_select = st.multiselect("Fournisseurs", sorted(fournisseur_options))
    if fournisseur_select:
        df_filtered = df_filtered[df_filtered["Fournisseur"].isin(fournisseur_select)]

    # Filtre Document d'achat
    doc_achat_options = df_filtered["Document d'achat"].dropna().unique()
    doc_achat_select = st.multiselect("Documents d'achat", sorted(doc_achat_options))
    if doc_achat_select:
        df_filtered = df_filtered[df_filtered["Document d'achat"].isin(doc_achat_select)]

    # Filtre Poste
    poste_options = df_filtered["Poste"].dropna().unique()
    poste_select = st.multiselect("Postes", sorted(poste_options))
    if poste_select:
        df_filtered = df_filtered[df_filtered["Poste"].isin(poste_select)]

    # Filtre Article
    article_options = df_filtered["Article"].dropna().unique()
    article_select = st.multiselect("Articles", sorted(article_options))
    if article_select:
        df_filtered = df_filtered[df_filtered["Article"].isin(article_select)]

    # Filtre Date
    date_filter_type = st.selectbox("Filtrer par date :", ["Toutes dates", "Plage de dates", "Année", "Mois"])
    
    if date_filter_type == "Plage de dates":
        date_min = df_filtered["Date livraison"].min()
        date_max = df_filtered["Date livraison"].max()
        date_range = st.date_input("Sélectionner une plage :", [date_min, date_max], min_value=date_min, max_value=date_max)
        if isinstance(date_range, list) and len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df_filtered = df_filtered[(df_filtered["Date livraison"] >= start) & (df_filtered["Date livraison"] <= end)]

    elif date_filter_type == "Année":
        years = df_filtered["Date livraison"].dt.year.dropna().unique()
        selected_year = st.selectbox("Choisir une année :", sorted(years))
        df_filtered = df_filtered[df_filtered["Date livraison"].dt.year == selected_year]

    elif date_filter_type == "Mois":
        years = df_filtered["Date livraison"].dt.year.dropna().unique()
        selected_year = st.selectbox("Année :", sorted(years))
        months = df_filtered[df_filtered["Date livraison"].dt.year == selected_year]["Date livraison"].dt.month.unique()
        selected_month = st.selectbox("Mois :", sorted(months))
        df_filtered = df_filtered[
            (df_filtered["Date livraison"].dt.year == selected_year) &
            (df_filtered["Date livraison"].dt.month == selected_month)
        ]
if df_filtered.empty:
    st.markdown("<h3 style='text-align: center; color: black;'>Aucune donnée disponible après filtrage</h3>", unsafe_allow_html=True)
    st.stop()

# Indicateurs clés
if not df.empty:
    kpis = calculate_kpis(df_filtered)
    st.markdown(f"""
        <div class="indicateurs-container">
            <div class="indicateurs-title">Indicateurs Clés</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px;">
                <div class="indicateur">
                    <div class="indicateur-titre">Livraison Conforme</div>
                    <div class="indicateur-valeur">{kpis['taux_livraison_conforme']}%</div>
                </div>
                <div class="indicateur">
                    <div class="indicateur-titre">Retard Moyen</div>
                    <div class="indicateur-valeur">{kpis['retard_moyen']} jours</div>
                </div>
                <div class="indicateur">
                    <div class="indicateur-titre">Fournisseurs</div>
                    <div class="indicateur-valeur">{kpis['nombre_fournisseurs']}</div>
                </div>
                <div class="indicateur">
                    <div class="indicateur-titre">Problèmes EM</div>
                    <div class="indicateur-valeur">{kpis['problemes_em']}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Création des deux colonnes
    col1, col2 = st.columns(2)
    
    # Colonne 1: Données filtrées
    with col1:
    
        st.markdown('<h4><u>Données Filtrées</u></h4>', unsafe_allow_html=True)
        st.dataframe(df_filtered, height=200, use_container_width=True)
        
        # Bouton de téléchargement
        st.download_button(
            label="📥 Télécharger les données",
            data=convert_to_excel(df_filtered),
            file_name="donnees_filtrees.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Colonne 2: Tableau récapitulatif
    with col2:
        st.markdown("<h4><u>Tableau Récapitulatif</u></h4>", unsafe_allow_html=True)
        
        # Création du statut basé sur la différence de jours
        df_filtered["Statut"] = df_filtered["Différence jours"].apply(
            lambda x: "En retard" if x > 0 else "À l'heure" if x == 0 else "En avance"
        )
        
        # Sélection et renommage des colonnes pour le récapitulatif
        summary_df = df_filtered[['Fournisseur', 'Article', 'Date livraison', 'QTE', 'Différence jours', 'Statut']]
        summary_df = summary_df.rename(columns={
            "QTE": "Quantité Échéance",
            "Différence jours": "Écart Jours"
        })
        
        # Affichage du tableau récapitulatif
        st.dataframe(summary_df, height=200, use_container_width=True)
        
        # Bouton de téléchargement pour le récapitulatif
        st.download_button(
            label="📥 Télécharger ce tableau en Excel",
            data=convert_to_excel(summary_df),
            file_name="recapitulatif_livraisons.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
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
# Section analyse de couverture
# Paramètres calculés

with col4:
    
    # Graphique du retard moyen par fournisseur avec matplotlib
    if not df_filtered.empty:
        # Filtrer seulement les retards positifs
        df_retards = df_filtered[df_filtered['Différence jours'] > 0]
        
        if not df_retards.empty:
            # Préparer les données filtrées
            df_plot = df_retards.groupby('Fournisseur')['Différence jours'].mean().sort_values(ascending=True)
            
            # Création de la figure
            fig, ax = plt.subplots(figsize=(15,5))
          
            # Tracer le graphique
            df_plot.plot(kind='barh', ax=ax, color='skyblue')
            ax.set_title("Retard Moyen par Fournisseur", pad=20)
            ax.set_xlabel("Jours de retard moyen")
            
            # Ajuster l'espacement
            plt.subplots_adjust(left=0.3)
            
            # Affichage dans Streamlit
            st.pyplot(fig)
            
            # Nettoyage mémoire matplotlib
            plt.clf()
            plt.close()
            
        else:
            st.markdown("<div style='text-align: center; padding: 18px; color: gray;'>Aucun retard à afficher</div>", unsafe_allow_html=True)
st.markdown("---")   
delay_distribution = df_filtered["Différence jours"].value_counts(normalize=True).sort_index().cumsum().reset_index()
delay_distribution.columns = ["Jours", "Couverture"]
delay_distribution["Couverture"] *= 100
st.markdown("<h4><u>Suivi des livraisons des fournisseurs</u></h4>", unsafe_allow_html=True)

# Charger les données
@st.cache_data
def load_data():
    df = pd.read_csv("statut_QTE_final.csv", delimiter=';', parse_dates=['Date livraison', 'Dernière date EM'])
    return df

df = load_data()

# CSS personnalisé
st.markdown("""
    <style>
        /* Style commun pour les selectbox */
        .stSelectbox>div>div>div>div>select {
            background-color: #dbdbdb !important;
            padding: 8px 32px 8px 12px !important;
            border-radius: 4px !important;
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            appearance: none !important;
            border: 1px solid #e0e0e0 !important;
        }
        
        .stSelectbox>div>div>div>svg {
            color: #B61818 !important;
            right: 12px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Création des colonnes
col_config, col_chart = st.columns([1, 2])
# Section configuration
with col_config:
    # Sélection de la période avec style déroulant
    periode = st.selectbox(
        "Période d'affichage :",
        ["Jour", "Mois"],
        index=0,
        help="Choisissez la granularité temporelle de l'analyse"
    )

    # Sélection du fournisseur
    fournisseurs = ["Tous"] + sorted(df['Fournisseur'].unique())
    fournisseur_select = st.selectbox(
        "Sélectionner un fournisseur :",
        fournisseurs,
        help="Filtrer les résultats par fournisseur spécifique"
    )
# Préparation des données
df_filtered = df.copy()
if fournisseur_select != "Tous":
    df_filtered = df_filtered[df_filtered['Fournisseur'] == fournisseur_select]

df_filtered['Mois'] = df_filtered['Date livraison'].dt.to_period('M').astype(str)
group_by_col = 'Date livraison' if periode == "Jour" else 'Mois'

# Agrégation des données
df_grouped = df_filtered.groupby([group_by_col, 'Fournisseur']).agg({
    'Différence jours': 'mean',
    'QTE': 'sum'
}).reset_index().sort_values(group_by_col)

# Création du graphique
with col_chart:
    fig = px.line(
        df_grouped,
        x=group_by_col,
        y='Différence jours',
        color='Fournisseur',
        markers=True,
        hover_data={
            'Différence jours': ':.1f',
            'QTE': ':,.0f',
            group_by_col: True
        },
        title=f"Évolution des retards de livraison ({periode.lower()})",
        height=300
    )
    
    fig.update_layout(
        hoverlabel=dict(bgcolor="white", font_size=12),
        xaxis_title=None,
        yaxis_title="Retard moyen (jours)",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="red",
        annotation_text="Échéance cible",
        annotation_position="bottom right"
    )
    
    st.plotly_chart(fig, use_container_width=True)  #verture
st.markdown("---")
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
col3, col4 = st.columns(2)

st.markdown('</div>', unsafe_allow_html=True)  # Fermeture du container principal3