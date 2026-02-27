import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os

# Initialisation de l'application 
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.FLATLY])
server = app.server

def charger_fusionner_et_nettoyer(fichier_2021, fichier_2023):
    """
    Cette fonction va charger les données depuis les deux fichiers Excel, les fusionner et les nettoyer.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path2021 = os.path.join(BASE_DIR, fichier_2021)
    path2023 = os.path.join(BASE_DIR, fichier_2023)
    
    # On sélectionne uniquement les colonnes qui nous seront utiles lors du chargement
    colonnes_utiles = [
        'libellé profession', 
        'libellé tranche d\'age', 
        'libellé sexe', 
        'Libellé durée d\'exposition', 
        'Libellé tableau de MP',
        'Nombre de MP en premier règlement', 
        'Nombre de nouvelles IP', 
        'Nombre de décès', 
        'Nombre de journées perdues', 
        'Somme des taux d\'IP'
    ]
    df_21 = pd.read_excel(path2021, usecols = colonnes_utiles, engine = 'openpyxl')
    df_23 = pd.read_excel(path2023, usecols = colonnes_utiles, engine = 'openpyxl')
    
    # On ajoute une colonne "Année" à chacun d'eux avant la fusion
    df_21['Année'] = 2021
    df_23['Année'] = 2023
    
    # La fameuse fusion
    df = pd.concat([df_21, df_23], ignore_index = True)
    
    # On force le format numérique pour les colonnes de calcul et on remplace les vides par des 0
    colonnes_num = [
        'Nombre de MP en premier règlement', 
        'Nombre de nouvelles IP', 
        'Nombre de décès', 
        'Nombre de journées perdues', 
        'Somme des taux d\'IP'
    ]
    for col in colonnes_num:
        # On s'assure que c'est du texte pour pouvoir le manipuler
        df[col] = df[col].astype(str)
        # On enlève les espaces et on remplace les virgules par des points
        df[col] = df[col].str.replace(' ', '', regex=False).str.replace(',', '.', regex=False)
        # 3. Maintenant, on peut convertir en nombre en toute sécurité !
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    # On s'occupe ensuite des vaelurs textuelles vides
    colonnes_texte = [
        'libellé profession', 
        'libellé tranche d\'age', 
        'libellé sexe', 
        'Libellé durée d\'exposition', 
        'Libellé tableau de MP'
    ]
    for col in colonnes_texte:
        df[col] = df[col].fillna('Non renseigné')
        df[col] = df[col].astype(str).str.strip()
        
    return df

df_final = charger_fusionner_et_nettoyer("mp2021.xlsx", "mp2023.xlsx")


# Les listes déroulantes
professions_uniques = df_final["libellé profession"].unique()

ages_uniques = df_final['libellé tranche d\'age'].unique()


# Disposition de la page
filtres = html.Div([
        # La profession
        dbc.Row([
            dbc.Label("Profession", className = 'fw-bold'),
            dbc.Col([
                dcc.Dropdown(id='dropdown-profession', 
                             placeholder = "Rechercher une profession", 
                             options = [{'label' : prof, 'value' : prof} for prof in professions_uniques],
                             value = "Agents d'entretien dans les bureaux, les hôtels et autres établissements",
                             searchable = True,
                             clearable = False)
            ], width = 12, className = "mb-4")
        ]),
        
        # Les filtres
        dbc.Row([
            dbc.Col([
                html.Label("Année"),
                dcc.Dropdown(id='dropdown-annee', 
                             options = [2021, 2023], 
                             value = 2023,
                             clearable = False)
            ], width = 4),
            dbc.Col([
                html.Label("Tranche d'âge"),
                dcc.Dropdown(id='dropdown-age', 
                            options = [{'label' : tranche, 'value' : tranche} for tranche in ages_uniques], 
                            value = ages_uniques[0],
                            clearable = False)
            ], width = 4)
        ], className = "mb-4")
    ], style = {'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})


contenu = html.Div([
    dbc.Row([
        dbc.Col(html.H2("Risques professionnels en France", className = "text-center mt-3"))
    ]),
    
    # Quelques stats
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Nouveaux cas", className = 'card-title'), html.H2(id = 'kpi-cas', className = 'text-info')]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Journées perdues", className = 'card-title'), html.H2(id = 'kpi-jours', className = 'text-warning')]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Gravité moyenne", className = 'card-title'), html.H2(id = 'kpi-gravite', className = 'text-danger')])))
    ], className = 'mb-5'),
    
    # Les graphiques 
    
    # Profil
    dbc.Row([
        dbc.Col([
            html.H3("Profil des victimes"),
            dcc.Graph(id = 'graph-profil')
        ], width = 12)
        ]),
    
    # Fréquentes
    dbc.Row([
        dbc.Col([
            html.H3("Maladies fréquentes"),
            dcc.Graph(id = 'graph-frequence')
        ], width = 12)
    ]),
    
    # Incapacitantes
    dbc.Row([
        html.H3("Maladies responsables d'incapacités permanentes"),
        dbc.Col([
            dcc.Graph(id = 'graph-ip-bar')
        ], width = 12),
        dbc.Col([
            dcc.Graph(id = 'graph-ip-scatter')
        ], width = 12)
    ]),
    
    # Mortelles
    dbc.Row([
        dbc.Col([
            html.H3("Focus sur les maladies létales"),
            dash_table.DataTable(
                id = 'table-deces',
                columns = [
                    {'name': "Maladie / Syndrome", 'id': "Libellé tableau de MP"},
                    {'name': "Nombre de décès", 'id': "Nombre de décès"}
                ],
                style_header={
                    'backgroundColor': '#E74C3C',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '12px',
                    'fontFamily': 'sans-serif'
                },
                page_size=5, # Affiche un maximum de 5 lignes pour rester compact
                style_table={'overflowX': 'auto'}
            )
        ], width = 12),
        dbc.Col([
            html.H3("Heatmap des victimes", className="text-danger mt-5 mb-3"),
            dcc.Graph(id='graph-heatmap-deces')
        ], width = 12)
    ]),
], style = {'padding' : '2rem'})


app.layout = dbc.Container(
    [
        dbc.Row([dbc.Col(filtres)]),
        dbc.Row([dbc.Col(contenu)])
    ],
    fluid = True
)



# Les callbacks
@app.callback(
    [Output('kpi-cas', 'children'),
     Output('kpi-jours', 'children'),
     Output('kpi-gravite', 'children')],
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value')]
)
def update_kpi(profession, annee, age):
    df_filtre = df_final.copy()
    
    if annee: 
        df_filtre = df_filtre[df_filtre['Année'] == int(annee)]
    
    if profession:
        df_filtre = df_filtre[df_filtre['libellé profession'] == profession]
    
    if age:
        df_filtre = df_filtre[df_filtre['libellé tranche d\'age'] == age]
    
    # Calcul des indicateurs 
    cas = df_filtre['Nombre de MP en premier règlement'].sum()
    jours = df_filtre['Nombre de journées perdues'].sum()
    
    somme_ip = df_filtre['Somme des taux d\'IP'].sum()
    nb_ip = df_filtre['Nombre de nouvelles IP'].sum()
    
    if nb_ip > 0:
        gravite = round(somme_ip / nb_ip, 2)
    else:
        gravite = 0
     
    return cas, jours, gravite


@app.callback(
    Output('graph-frequence', 'figure'),
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value')]
)
def update_graphe_frequence(profession, annee, age):
    df_filtre = df_final.copy()
    
    if annee: 
        df_filtre = df_filtre[df_filtre['Année'] == int(annee)]
    
    if profession:
        df_filtre = df_filtre[df_filtre['libellé profession'] == profession]
    
    if age:
        df_filtre = df_filtre[df_filtre['libellé tranche d\'age'] == age]
        
    # Au cas où il n'y a pas de données
    if df_filtre.empty or df_filtre['Nombre de MP en premier règlement'].sum() == 0:
        fig_vide = px.bar(title="Aucune donnée pour ces filtres")
        fig_vide.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        return fig_vide
    
    df_groupe = df_filtre.groupby('Libellé tableau de MP')['Nombre de MP en premier règlement'].sum().reset_index()
    
    df_top10 = df_groupe.sort_values(by='Nombre de MP en premier règlement', ascending=False).head(10) # Les 10 premiers
    
    df_top10 = df_top10.sort_values(by='Nombre de MP en premier règlement', ascending=True) # Pour inverser l'ordre des barres avant le dessin 
    
    df_top10 = df_top10[df_top10['Nombre de MP en premier règlement'] > 0]
    
    fig = px.bar(
        df_top10,
        x='Nombre de MP en premier règlement',
        y='Libellé tableau de MP',
        orientation='h', # C'est cette option qui met les barres à l'horizontale
        title="Top 10 des maladies professionnelles les plus fréquentes",
        labels={
            'Nombre de MP en premier règlement': 'Nombre de nouveaux cas',
            'Libellé tableau de MP': '' # On vide ce titre car les noms parlent d'eux-mêmes
        },
        color_discrete_sequence=['#2C3E50'] # Une couleur sobre et pro (bleu nuit)
    )
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'), # Une grille légère verticale pour lire les montants
        yaxis=dict(showgrid=False), # Pas de grille horizontale pour ne pas surcharger
        plot_bgcolor='rgba(0,0,0,0)', # Fond transparent pour s'intégrer parfaitement à ton thème
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=20, t=50, b=0) # On ajuste les marges pour que le graphique respire
    )
    
    return fig


@app.callback(
    Output('graph-ip-bar', 'figure'),
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value')]
)
def update_graphe_ip_bar(profession, annee, age):
    df_filtre = df_final.copy()
    
    if annee: 
        df_filtre = df_filtre[df_filtre['Année'] == int(annee)]
    
    if profession:
        df_filtre = df_filtre[df_filtre['libellé profession'] == profession]
    
    if age:
        df_filtre = df_filtre[df_filtre['libellé tranche d\'age'] == age]
    
    df_ip = df_filtre.groupby('Libellé tableau de MP').agg({
        'Somme des taux d\'IP': 'sum',
        'Nombre de nouvelles IP': 'sum'
    }).reset_index()
    df_ip = df_ip[df_ip['Nombre de nouvelles IP'] > 0]
    
    if df_ip.empty:
        fig_vide = px.bar(title="Aucune donnée d'incapacité pour cette sélection")
        fig_vide.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        return fig_vide
    
    df_ip['Taux moyen IP (%)'] = df_ip['Somme des taux d\'IP'] / df_ip['Nombre de nouvelles IP']
    
    # On garde les 10 maladies les plus invalidantes (et on trie pour l'affichage de bas en haut)
    df_top_ip = df_ip.sort_values(by='Taux moyen IP (%)', ascending=True).tail(10)
    
    fig = px.bar(
        df_top_ip,
        x='Taux moyen IP (%)',
        y='Libellé tableau de MP',
        orientation='h',
        title="Top 10 des maladies les plus invalidantes (Taux moyen d'IP)",
        labels={
            'Taux moyen IP (%)': 'Taux d\'incapacité moyen (%)',
            'Libellé tableau de MP': ''
        },
        color='Taux moyen IP (%)', # Ajoute un dégradé de couleur selon la gravité
        color_continuous_scale='Reds' # Les taux les plus élevés seront en rouge foncé
    )
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor='#e9ecef', ticksuffix="%"), # Ajoute le symbole % sur l'axe
        yaxis=dict(showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False # Cache la barre de légende du dégradé pour faire plus propre
    )
    
    # Arrondir les valeurs affichées au survol à 1 décimale
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Taux moyen: %{x:.1f}%<extra></extra>")
    
    return fig


@app.callback(
    Output('graph-ip-scatter', 'figure'),
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value')]
)
def update_graphe_ip_scatter(profession, annee, age):
    df_filtre = df_final.copy()
    
    if annee: 
        df_filtre = df_filtre[df_filtre['Année'] == int(annee)]
    
    if profession:
        df_filtre = df_filtre[df_filtre['libellé profession'] == profession]
    
    if age:
        df_filtre = df_filtre[df_filtre['libellé tranche d\'age'] == age]
        
    # Regroupement par maladie pour avoir le total des cas et le total des jours perdus
    df_scatter = df_filtre.groupby('Libellé tableau de MP').agg({
        'Nombre de MP en premier règlement': 'sum',
        'Nombre de journées perdues': 'sum'
    }).reset_index()
        
    if df_scatter.empty:
        fig_vide = px.scatter(title="Aucune donnée pour la matrice d'impact")
        fig_vide.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        return fig_vide
    
    fig_scatter = px.scatter(
        df_scatter,
        x='Nombre de MP en premier règlement',
        y='Nombre de journées perdues',
        hover_name='Libellé tableau de MP', # Le nom de la maladie apparaît au survol de la souris
        title="Matrice d'impact : Fréquence vs Journées perdues",
        labels={
            'Nombre de MP en premier règlement': 'Nombre de nouveaux cas',
            'Nombre de journées perdues': 'Journées perdues'
        },
        color_discrete_sequence=['#E67E22'] # Une couleur orange vif pour bien voir les points
    )
    
    fig_scatter.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    
    fig_scatter.update_layout(
        xaxis=dict(showgrid=True, gridcolor='#e9ecef', zeroline=True, zerolinecolor='lightgrey'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', zeroline=True, zerolinecolor='lightgrey'),
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig_scatter
    

@app.callback(
    Output('graph-profil', 'figure'),
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value')]
)
def update_graphe_profil(profession, annee, age):
    df_filtre = df_final.copy()
    
    if annee: 
        df_filtre = df_filtre[df_filtre['Année'] == int(annee)]
    
    if profession:
        df_filtre = df_filtre[df_filtre['libellé profession'] == profession]
    
    if age:
        df_filtre = df_filtre[df_filtre['libellé tranche d\'age'] == age]
        
    # Regroupement par durée d'exposition et par sexe 
    df_profil = df_filtre.groupby(['Libellé durée d\'exposition', 'libellé sexe'])['Nombre de MP en premier règlement'].sum().reset_index()

    # Sécurité anti-crash
    if df_profil.empty or df_profil['Nombre de MP en premier règlement'].sum() == 0:
        fig_vide = px.bar(title="Aucune donnée de profil pour cette sélection")
        fig_vide.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        return fig_vide

    # 3. Création du graphique en barres groupées
    fig = px.bar(
        df_profil,
        x='Libellé durée d\'exposition',
        y='Nombre de MP en premier règlement',
        color='libellé sexe',
        barmode='group', # L'option clé pour mettre les barres côte à côte
        title="Profil des victimes selon le sexe et la durée d'exposition",
        labels={
            'Nombre de MP en premier règlement': 'Nombre de cas',
            'Libellé durée d\'exposition': 'Durée d\'exposition',
            'libellé sexe': 'Sexe'
        },
        # On définit des couleurs claires pour différencier facilement
        color_discrete_map={
            'Hommes': '#3498DB', # Bleu
            'Femmes': '#9B59B6', # Violet
            'Non renseigné': '#BDC3C7' # Gris pour les valeurs vides/inconnues
        }
    )
    
    # 4. Ajustements esthétiques
    fig.update_layout(
        yaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        xaxis=dict(showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            title=None # Masque le mot "Sexe" au-dessus de la légende pour faire plus propre
        )
    )
    
    return fig


@app.callback(
    Output('table-deces', 'data'),
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value')]
)
def update_deces(profession, annee, age):
    df_filtre = df_final.copy()
    
    if annee: 
        df_filtre = df_filtre[df_filtre['Année'] == int(annee)]
    
    if profession:
        df_filtre = df_filtre[df_filtre['libellé profession'] == profession]
    
    if age:
        df_filtre = df_filtre[df_filtre['libellé tranche d\'age'] == age]
        
    df_deces = df_filtre[df_filtre['Nombre de décès'] > 0]
    
    if df_deces.empty:
        return []
    
    # Regroupement par maladie et somme des décès
    df_groupe = df_deces.groupby('Libellé tableau de MP')['Nombre de décès'].sum().reset_index()
    
    df_trie = df_groupe.sort_values(by = 'Nombre de décès', ascending = False)
    
    return df_trie.to_dict('records') # Parce que les données viennent sous forme de dictionnaire


@app.callback(
    Output('graph-heatmap-deces', 'figure'),
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value')]
)
def update_heatmap_deces(profession, annee):
    df_filtre = df_final.copy()
    
    if annee: 
        df_filtre = df_filtre[df_filtre['Année'] == int(annee)]
    
    if profession:
        df_filtre = df_filtre[df_filtre['libellé profession'] == profession]
        
    df_deces = df_filtre[df_filtre['Nombre de décès'] > 0]
    
    if df_deces.empty:
        fig_vide = px.density_heatmap(title="Aucun décès recensé pour cette sélection")
        fig_vide.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig_vide
    
    fig = px.density_heatmap(
        df_deces,
        x="Libellé durée d'exposition",
        y="libellé tranche d\'age",
        z="Nombre de décès",
        histfunc="sum", # C'est ici qu'on dit à Plotly d'additionner les décès par case
        title="Mortalité : Âge vs Durée d'exposition",
        labels={
            "Libellé durée d'exposition": "Durée d'exposition",
            "libellé tranche d\'age": "Tranche d'âge",
            "Nombre de décès": "Décès"
        },
        color_continuous_scale='Reds', # Une échelle de couleur rouge pour l'alerte
        text_auto=True # Affiche le nombre de décès directement au centre de chaque case !
    )
    
    # Finitions
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False, # On cache la barre de couleur à côté car les chiffres sont dans les cases
        yaxis={'categoryorder': 'category ascending'},
    )
    
    return fig
    
if __name__ == '__main__':
    app.run(debug = True)