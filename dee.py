import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Analyse des Fournisseurs", layout="wide")

# Fonction pour charger les données
@st.cache_data
def load_data():
    # Normalement, vous utiliseriez:
    # df = pd.read_csv('votre_fichier.csv', sep=';')
    
    # Pour la démonstration, je vais créer un DataFrame à partir des données d'exemple
    data = """Fournisseur;Document d'achat;Poste;Article;Nº d'appel;Date livraison;QTE;Date de transmission appel;Dernière date EM;Statut livraison;Quantité corrigée;Différence jours
100590;5500041768;190;0204207170;489;2023-12-08;1500;2023-12-12;2023-11-29;Date EM absente;;
100590;5500041768;190;0204207170;489;2023-12-12;2500;2023-12-12;2023-11-29;Date EM absente;;"""
    
    # Génération de données supplémentaires pour une meilleure visualisation
    additional_data = []
    fournisseurs = [100590, 100591, 100592, 100593, 100594]
    statuts = ["Livré à temps", "Retard", "Livré partiellement", "Date EM absente", "Annulé"]
    articles = ["0204207170", "0204207171", "0204207172", "0204207173"]
    
    for i in range(50):
        fournisseur = np.random.choice(fournisseurs)
        article = np.random.choice(articles)
        document = f"55000{np.random.randint(10000, 99999)}"
        poste = np.random.randint(100, 999)
        appel = np.random.randint(100, 999)
        
        # Dates
        date_livraison_souhaitee = datetime(2023, np.random.randint(1, 12), np.random.randint(1, 28))
        jours_diff = np.random.randint(-5, 15)  # Négatif: en avance, Positif: en retard
        date_livraison = date_livraison_souhaitee + pd.Timedelta(days=jours_diff)
        date_transmission = date_livraison_souhaitee - pd.Timedelta(days=np.random.randint(1, 10))
        date_em = date_transmission - pd.Timedelta(days=np.random.randint(1, 5))
        
        # Quantités
        qte_souhaitee = np.random.randint(500, 5000)
        ratio_correction = np.random.uniform(0.7, 1.2)
        qte_corrigee = int(qte_souhaitee * ratio_correction) if np.random.random() > 0.3 else ""
        
        statut = np.random.choice(statuts)
        
        row = [
            fournisseur, document, poste, article, appel,
            date_livraison_souhaitee.strftime('%Y-%m-%d'),
            qte_souhaitee,
            date_transmission.strftime('%Y-%m-%d'),
            date_em.strftime('%Y-%m-%d') if np.random.random() > 0.2 else "",
            statut,
            qte_corrigee,
            jours_diff if np.random.random() > 0.3 else ""
        ]
        additional_data.append(row)
    
    # Convertir la chaîne en DataFrame
    from io import StringIO
    df = pd.read_csv(StringIO(data), sep=';')
    
    # Ajouter les données supplémentaires
    columns = df.columns
    df_additional = pd.DataFrame(additional_data, columns=columns)
    df = pd.concat([df, df_additional], ignore_index=True)
    
    # Conversion des types de données
    df['Date livraison'] = pd.to_datetime(df['Date livraison'], errors='coerce')
    df['Date de transmission appel'] = pd.to_datetime(df['Date de transmission appel'], errors='coerce')
    df['Dernière date EM'] = pd.to_datetime(df['Dernière date EM'], errors='coerce')
    df['QTE'] = pd.to_numeric(df['QTE'], errors='coerce')
    df['Quantité corrigée'] = pd.to_numeric(df['Quantité corrigée'], errors='coerce')
    df['Différence jours'] = pd.to_numeric(df['Différence jours'], errors='coerce')
    
    # Calcul des métriques dérivées
    df['Livré à temps'] = (df['Différence jours'] <= 0).astype(int)
    df['Taux de complétion'] = df.apply(lambda x: x['Quantité corrigée']/x['QTE'] if pd.notna(x['Quantité corrigée']) else 1, axis=1)
    
    # Pour les fournisseurs qui n'ont pas de différence de jours renseignée, on considère que c'est une donnée manquante
    df['Performance de livraison'] = df.apply(lambda x: 
        (1 if x['Livré à temps'] == 1 else max(0, 1 - x['Différence jours']/30)) * 
        (x['Taux de complétion'] if pd.notna(x['Taux de complétion']) else 1) * 100, 
        axis=1)
    
    return df

# Charger les données
df = load_data()

# Titre du dashboard
st.title("📊 Dashboard d'Analyse des Performances des Fournisseurs")
st.markdown("Ce tableau de bord permet d'analyser la performance des fournisseurs sur plusieurs critères clés.")

# Créer des filtres
st.sidebar.header("Filtres")
fournisseurs = df['Fournisseur'].unique()
selected_fournisseurs = st.sidebar.multiselect("Sélectionner des fournisseurs:", fournisseurs, default=fournisseurs)

articles = df['Article'].unique()
selected_articles = st.sidebar.multiselect("Sélectionner des articles:", articles, default=articles)

# Filtrer les données
filtered_df = df[(df['Fournisseur'].isin(selected_fournisseurs)) & (df['Article'].isin(selected_articles))]

# 1. Vue d'ensemble des métriques
st.header("1. Vue d'ensemble")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Nombre total de commandes", filtered_df.shape[0])
    
with col2:
    on_time_rate = filtered_df['Livré à temps'].mean() * 100
    st.metric("Taux de livraison à temps", f"{on_time_rate:.2f}%")
    
with col3:
    avg_delay = filtered_df[filtered_df['Différence jours'] > 0]['Différence jours'].mean()
    st.metric("Retard moyen (jours)", f"{avg_delay:.1f}" if not pd.isna(avg_delay) else "N/A")
    
with col4:
    completion_rate = filtered_df['Taux de complétion'].mean() * 100
    st.metric("Taux moyen de complétion", f"{completion_rate:.2f}%")

# 2. Score de performance globale des fournisseurs
st.header("2. Performance globale des fournisseurs")

# Calcul de la performance par fournisseur
perf_by_supplier = filtered_df.groupby('Fournisseur').agg({
    'Livré à temps': 'mean',
    'Taux de complétion': 'mean',
    'Performance de livraison': 'mean',
    'Fournisseur': 'count'
}).rename(columns={'Fournisseur': 'Nombre de commandes'})

perf_by_supplier['Livré à temps'] = perf_by_supplier['Livré à temps'] * 100
perf_by_supplier['Taux de complétion'] = perf_by_supplier['Taux de complétion'] * 100

# Créer le graphique radar pour comparer les fournisseurs
fig_radar = go.Figure()

categories = ['Livré à temps (%)', 'Taux de complétion (%)', 'Performance globale (%)']

for fournisseur in perf_by_supplier.index:
    values = [
        perf_by_supplier.loc[fournisseur, 'Livré à temps'],
        perf_by_supplier.loc[fournisseur, 'Taux de complétion'],
        perf_by_supplier.loc[fournisseur, 'Performance de livraison']
    ]
    # Ajouter une valeur pour fermer le radar
    values_radar = values + [values[0]]
    categories_radar = categories + [categories[0]]
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values_radar,
        theta=categories_radar,
        fill='toself',
        name=f'Fournisseur {fournisseur}'
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )),
    showlegend=True,
    height=500
)

# Afficher les graphiques côte à côte
col1, col2 = st.columns([3, 2])

with col1:
    st.plotly_chart(fig_radar, use_container_width=True)

with col2:
    # Tableau des performances
    st.dataframe(
        perf_by_supplier.sort_values(by='Performance de livraison', ascending=False)
        .style.format({
            'Livré à temps': '{:.2f}%',
            'Taux de complétion': '{:.2f}%',
            'Performance de livraison': '{:.2f}%'
        }),
        height=400
    )

# 3. Analyse comparative des délais de livraison
st.header("3. Analyse des délais de livraison")

col1, col2 = st.columns(2)

with col1:
    # Boxplot des différences de jours par fournisseur
    fig_box = px.box(
        filtered_df[filtered_df['Différence jours'].notna()], 
        x='Fournisseur', 
        y='Différence jours',
        title='Distribution des écarts de jours de livraison par fournisseur',
        color='Fournisseur',
        height=400
    )
    fig_box.update_layout(xaxis_title='Fournisseur', yaxis_title='Écart (jours)')
    st.plotly_chart(fig_box, use_container_width=True)

with col2:
    # Histogramme des différences de jours
    fig_hist = px.histogram(
        filtered_df[filtered_df['Différence jours'].notna()],
        x='Différence jours',
        color='Fournisseur',
        marginal='box',
        title='Distribution des écarts de jours',
        height=400
    )
    fig_hist.update_layout(xaxis_title='Écart (jours)', yaxis_title='Nombre de commandes')
    st.plotly_chart(fig_hist, use_container_width=True)

# 4. Analyse des quantités livrées
st.header("4. Analyse des quantités livrées")

col1, col2 = st.columns(2)

with col1:
    # Calculer le ratio de livraison (quantité livrée / quantité demandée)
    df_qty = filtered_df[filtered_df['Quantité corrigée'].notna()].copy()
    df_qty['Ratio de livraison'] = df_qty['Quantité corrigée'] / df_qty['QTE']
    
    # Créer un scatter plot
    fig_scatter = px.scatter(
        df_qty,
        x='QTE',
        y='Quantité corrigée',
        color='Fournisseur',
        size=abs(df_qty['Quantité corrigée'] - df_qty['QTE']),
        hover_data=['Article', 'Ratio de livraison'],
        title='Quantité demandée vs Quantité livrée',
        height=400
    )
    # Ajouter une ligne diagonale pour représenter une livraison parfaite
    fig_scatter.add_trace(
        go.Scatter(
            x=[df_qty['QTE'].min(), df_qty['QTE'].max()],
            y=[df_qty['QTE'].min(), df_qty['QTE'].max()],
            mode='lines',
            line=dict(dash='dash', color='gray'),
            name='Livraison parfaite'
        )
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col2:
    # Calculer les statistiques de ratio de livraison par fournisseur
    ratio_stats = df_qty.groupby('Fournisseur')['Ratio de livraison'].agg(['mean', 'std', 'min', 'max', 'count'])
    ratio_stats = ratio_stats.rename(columns={
        'mean': 'Ratio moyen',
        'std': 'Écart-type',
        'min': 'Ratio minimum',
        'max': 'Ratio maximum',
        'count': 'Nombre de livraisons'
    })
    
    # Créer un bar chart pour le ratio moyen
    fig_bar = px.bar(
        ratio_stats.reset_index(),
        x='Fournisseur',
        y='Ratio moyen',
        error_y='Écart-type',
        title='Ratio moyen de livraison par fournisseur',
        color='Fournisseur',
        height=400
    )
    fig_bar.update_layout(xaxis_title='Fournisseur', yaxis_title='Ratio moyen')
    st.plotly_chart(fig_bar, use_container_width=True)

# 5. Score global et recommandation
st.header("5. Évaluation globale et recommandation")

# Calculer un score global pour chaque fournisseur
supplier_score = perf_by_supplier.copy()
supplier_score['Score Global'] = (
    supplier_score['Livré à temps'] * 0.4 +
    supplier_score['Taux de complétion'] * 0.4 +
    supplier_score['Performance de livraison'] * 0.2
)

# Créer un dataframe pour la notation
supplier_rating = supplier_score.copy()
supplier_rating['Note'] = pd.cut(
    supplier_rating['Score Global'],
    bins=[0, 60, 75, 85, 95, 100],
    labels=['E', 'D', 'C', 'B', 'A']
)

# Ajout du nombre de commandes
supplier_rating['Nombre de commandes'] = perf_by_supplier['Nombre de commandes']

# Créer un graphique de jauge pour chaque fournisseur
gauge_figs = []
for fournisseur in supplier_rating.index:
    score = supplier_rating.loc[fournisseur, 'Score Global']
    note = supplier_rating.loc[fournisseur, 'Note']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={'text': f"Fournisseur {fournisseur} (Note: {note})"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 60], 'color': "red"},
                {'range': [60, 75], 'color': "orange"},
                {'range': [75, 85], 'color': "yellow"},
                {'range': [85, 95], 'color': "lightgreen"},
                {'range': [95, 100], 'color': "green"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    fig.update_layout(height=250)
    gauge_figs.append(fig)

# Afficher les jauges dans une grille
cols = st.columns(min(3, len(gauge_figs)))
for i, fig in enumerate(gauge_figs):
    with cols[i % len(cols)]:
        st.plotly_chart(fig, use_container_width=True)

# Tableau de notation finale
st.subheader("Classement des fournisseurs")
sorted_ratings = supplier_rating.sort_values(by='Score Global', ascending=False)
sorted_ratings_display = sorted_ratings.copy()

# Mise en forme du tableau
def highlight_rating(val):
    if val == 'A':
        return 'background-color: green; color: white'
    elif val == 'B':
        return 'background-color: lightgreen'
    elif val == 'C':
        return 'background-color: yellow'
    elif val == 'D':
        return 'background-color: orange'
    elif val == 'E':
        return 'background-color: red; color: white'
    return ''

styled_ratings = sorted_ratings_display.style.format({
    'Livré à temps': '{:.2f}%',
    'Taux de complétion': '{:.2f}%',
    'Performance de livraison': '{:.2f}%',
    'Score Global': '{:.2f}'
}).applymap(highlight_rating, subset=['Note'])

st.dataframe(styled_ratings, height=300)

# 6. Recommandation du fournisseur optimal
st.subheader("Recommandation du fournisseur optimal")

best_supplier = sorted_ratings.index[0]
best_score = sorted_ratings.iloc[0]['Score Global']
best_note = sorted_ratings.iloc[0]['Note']

st.info(f"""
**Le fournisseur optimal est le fournisseur {best_supplier}** avec un score global de {best_score:.2f}/100 (Note: {best_note}).

Ce fournisseur se distingue par:
- Un taux de livraison à temps de {sorted_ratings.iloc[0]['Livré à temps']:.2f}%
- Un taux de complétion des commandes de {sorted_ratings.iloc[0]['Taux de complétion']:.2f}%
- Une performance globale de {sorted_ratings.iloc[0]['Performance de livraison']:.2f}%
- Un total de {sorted_ratings.iloc[0]['Nombre de commandes']} commandes analysées
""")

# Ajouter des conseils supplémentaires
worst_performer = sorted_ratings.index[-1]
st.warning(f"""
**Points d'attention:**
- Le fournisseur {worst_performer} présente les performances les plus faibles avec un score de {sorted_ratings.iloc[-1]['Score Global']:.2f}/100.
- Envisagez de revoir les conditions contractuelles ou d'explorer d'autres alternatives pour ce fournisseur.
""")

# Téléchargement des données
st.header("7. Exporter les données")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Télécharger les données filtrées (CSV)",
    data=csv,
    file_name='analyse_fournisseurs.csv',
    mime='text/csv',
)

# Informations supplémentaires
st.sidebar.markdown("---")
st.sidebar.info("""
**À propos de ce dashboard**

Ce tableau de bord permet d'analyser les performances des fournisseurs selon plusieurs critères:
- Respect des délais de livraison
- Respect des quantités commandées
- Performance globale

Les métriques sont calculées à partir des données fournies et permettent d'identifier le fournisseur optimal pour votre activité.
""")