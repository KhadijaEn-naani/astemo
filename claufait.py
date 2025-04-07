import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Configurer la page
st.set_page_config(page_title="Dashboard Fournisseurs", layout="wide")

# Charger les données
uploaded_file = st.file_uploader("Télécharger le fichier CSV", type="csv")
if not uploaded_file:
    st.stop()

df = pd.read_csv(uploaded_file, sep=';', parse_dates=['Date livraison', 'Date de transmission appel', 'Dernière date EM'])

# Nettoyage des données
df['Différence jours'] = df['Différence jours'].fillna(0)
df['Quantité corrigée'] = df['Quantité corrigée'].fillna(0)

# Calcul des KPIs
def calculate_kpis(data):
    return {
        "Taux Livraison Conforme": np.mean((data['Différence jours'] == 0) & (data['Quantité corrigée'] == 0)),
        "Retard Moyen": data['Différence jours'].mean(),
        "Écart Qté Moyen": data['Quantité corrigée'].mean(),
        "Problèmes EM": data[data['Statut livraison'] == 'Date EM absente'].shape[0]
    }

# Interface Streamlit
st.title("Analyse de la Performance des Fournisseurs")

# Section KPIs
st.header("Indicateurs Clés")
col1, col2, col3, col4 = st.columns(4)
kpis = calculate_kpis(df)
col1.metric("Taux Livraison Conforme", f"{kpis['Taux Livraison Conforme']:.1%}")
col2.metric("Retard Moyen", f"{kpis['Retard Moyen']:.1f} jours")
col3.metric("Écart Qté Moyen", f"{kpis['Écart Qté Moyen']:.0f} unités")
col4.metric("Problèmes EM", kpis['Problèmes EM'])

# Filtres
st.sidebar.header("Filtres")
fournisseurs = st.sidebar.multiselect("Choisir fournisseurs", df['Fournisseur'].unique())
date_min = st.sidebar.date_input("Date début", df['Date livraison'].min())
date_max = st.sidebar.date_input("Date fin", df['Date livraison'].max())

# Appliquer filtres
filtered_df = df[
    (df['Fournisseur'].isin(fournisseurs) if fournisseurs else True) &
    (df['Date livraison'] >= pd.to_datetime(date_min)) &
    (df['Date livraison'] <= pd.to_datetime(date_max))
]

# Visualisations
with st.expander("Performance par Fournisseur"):
    fig, ax = plt.subplots(figsize=(10, 6))
    filtered_df.groupby('Fournisseur')['Différence jours'].mean().sort_values().plot(
        kind='barh', ax=ax, color='skyblue'
    )
    ax.set_title("Retard Moyen par Fournisseur")
    ax.set_xlabel("Jours de retard moyen")
    st.pyplot(fig)

with st.expander("Analyse des Retards"):
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 4))
        filtered_df['Différence jours'].plot(
            kind='hist', bins=20, ax=ax, color='salmon'
        )
        ax.set_title("Distribution des Retards")
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4))
        filtered_df.groupby(filtered_df['Date livraison'].dt.month)['Différence jours'].mean().plot(
            kind='line', ax=ax, marker='o'
        )
        ax.set_title("Évolution Mensuelle des Retards")
        st.pyplot(fig)

with st.expander("Analyse des Quantités"):
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        filtered_df['Différence jours'], 
        filtered_df['Quantité corrigée'],
        c=filtered_df['Fournisseur'].astype('category').cat.codes,
        cmap='tab20'
    )
    ax.set_title("Relation Retard vs Écart Quantité")
    ax.set_xlabel("Jours de retard")
    ax.set_ylabel("Écart de quantité")
    plt.colorbar(scatter, ax=ax, label="Fournisseur")
    st.pyplot(fig)

with st.expander("Fournisseurs à Risque"):
    risk_df = filtered_df.groupby('Fournisseur').agg(
        Retard_Moyen=('Différence jours', 'mean'),
        Ecart_Qté=('Quantité corrigée', 'mean'),
        Total_Commandes=('Fournisseur', 'count')
    ).reset_index()
    
    risk_df['Score_Risque'] = (
        0.6 * risk_df['Retard_Moyen'] + 
        0.4 * np.abs(risk_df['Ecart_Qté'])
    )
    
    fig, ax = plt.subplots(figsize=(10, 6))
    risk_df.sort_values('Score_Risque').tail(10).plot(
        kind='barh', x='Fournisseur', y='Score_Risque', ax=ax, color='darkred'
    )
    ax.set_title("Top 10 Fournisseurs à Risque")
    st.pyplot(fig)

with st.expander("Données Brutes"):
    st.dataframe(filtered_df.style.highlight_max(
        subset=['Différence jours', 'Quantité corrigée'], color='#fffd75'
    ))