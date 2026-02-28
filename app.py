import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os
import textwrap

# Initialisation de l'application 
app = dash.Dash(
    __name__, 
    external_stylesheets = [dbc.themes.FLATLY, dbc.icons.FONT_AWESOME],
    title = "SafeWork Dashboard",
    update_title = "Chargement..."
)
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
        
    # On s'occupe ensuite des valeurs textuelles vides
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
filtres = dbc.Row([
    dbc.Col([
        html.Label("Profession", className = "d-block fw-bold"),
        dcc.Dropdown(id='dropdown-profession',
                     options = [{'label' : prof, 'value' : prof} for prof in professions_uniques],
                     value = "Agents d'entretien dans les bureaux, les hôtels et autres établissements",
                     searchable = True,
                     clearable = False)
    ], width = 6),
        
    dbc.Col([
        html.Label("Année", className = "d-block fw-bold"),
        dcc.Dropdown(id='dropdown-annee', 
                     options = [2021, 2023], 
                     value = 2023,
                     clearable = False)
    ], width = 3),
        
    dbc.Col([
        html.Label("Tranche d'âge", className = "d-block fw-bold"),
        dcc.Dropdown(id='dropdown-age', 
                    options = [{'label' : tranche, 'value' : tranche} for tranche in ages_uniques], 
                    value = ages_uniques[0],
                    clearable = False)
    ], width = 3)
], className = "py-3")


titre = html.Div([
    html.Div([
        html.H1([
            html.Span("Safe", style={"color": "#18BC9C", "fontWeight": "bold"}), # Le vert "Santé"
            html.Span("Work", style={"color": "#2C3E50", "fontWeight": "300"}), # Le bleu foncé "Pro"
        ], className="mb-0", style={"letterSpacing": "1px"}),
        
        html.P("Plateforme d'analyse des risques liés aux maladies en milieu professionnel", 
               className="text-muted fw-bold", style={"fontSize": "1.2rem", "marginTop": "15px"})
    ], className="py-4 text-center") # Ajoute un peu d'espace vertical
])


contenu = html.Div([    
    # Quelques stats (KPI)
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Nouveaux cas", className="text-muted mb-1"),
                            html.H3(id = 'kpi-cas', style={"color": "#3498DB", "fontWeight": "bold"}, className="mb-0"),
                        ], width=9),
                        dbc.Col([
                            html.I(className=f"fas {"fa-user-plus"} fa-2x", style={"color": "#3498DB", "opacity": "0.3"})
                        ], width=3, className="d-flex align-items-center justify-content-center")
                    ])
                ]),
                style={
                    "borderRadius": "10px",
                    "borderLeft": f"5px solid {"#3498DB"}", # Liseré de couleur sur le côté
                    "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                    "marginBottom": "10px"
                }
            ), width = 4
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Journées perdues", className="text-muted mb-1"),
                            html.H3(id = 'kpi-jours', style={"color": "#F39C12", "fontWeight": "bold"}, className="mb-0"),
                        ], width=9),
                        dbc.Col([
                            html.I(className=f"fas {"fa-calendar-times"} fa-2x", style={"color": "#F39C12", "opacity": "0.3"})
                        ], width=3, className="d-flex align-items-center justify-content-center")
                    ])
                ]),
                style={
                    "borderRadius": "10px",
                    "borderLeft": f"5px solid {"#F39C12"}", # Liseré de couleur sur le côté
                    "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                    "marginBottom": "10px"
                }
            ), width = 4    
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Gravité moyenne", className="text-muted mb-1"),
                            html.H3(id = 'kpi-gravite', style={"color": "#E74C3C", "fontWeight": "bold"}, className="mb-0"),
                        ], width=9),
                        dbc.Col([
                            html.I(className=f"fas {"fa-notes-medical"} fa-2x", style={"color": "#E74C3C", "opacity": "0.3"})
                        ], width=3, className="d-flex align-items-center justify-content-center")
                    ])
                ]),
                style={
                    "borderRadius": "10px",
                    "borderLeft": f"5px solid {"#E74C3C"}", # Liseré de couleur sur le côté
                    "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
                    "marginBottom": "10px"
                }
            ), width = 4
        )
    ], className = 'mb-5'),
    
    # Les graphiques 
    # Profil
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H4("Profil des malades selon le sexe et la durée d'exposition", className = "mb-0 text-center")
                ),
                dbc.CardBody([
                    dcc.Graph(id = 'graph-profil')
                ])
            ], className="shadow border-0 mt-4")
        )
    ], className = "mb-4"),
    
    # Fréquentes
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H4("Top des maladies les plus fréquentes", className = "mb-0 text-center")
                ),
                dbc.CardBody(dcc.Graph(id = 'graph-frequence'))
            ], className="shadow border-0 mt-4"), 
            width = 12
        )
    ], className = "mb-4"),
    
    # Incapacitantes
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H4("Analyse de la gravité (Maladies incapacitantes)", className = "mb-0 text-center")
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id = 'graph-ip-bar'), width = 12),
                        dbc.Col(dcc.Graph(id = 'graph-ip-scatter'), width = 12)
                    ])
                ])
            ], className="shadow border-0 mt-4"), 
            width = 12
        )
    ], className = "mb-4"),
    
    # Mortelles
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(
                    html.H4("Focus sur la mortalité en milieu professionnel", className = "mb-0 text-center"),
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("Maladies ayant causé au moins un décès", className="mb-3 text-muted"),
                            dash_table.DataTable(
                                id = 'table-deces',
                                columns = [
                                    {'name': "Maladie / Syndrome", 'id': "Libellé tableau de MP"},
                                    {'name': "Nombre de décès", 'id': "Nombre de décès"}
                                ],
                                style_header={
                                    'backgroundColor': '#f8f9fa',
                                    'fontWeight': 'bold',
                                    'border' : 'none'
                                },
                                style_cell={
                                    'textAlign': 'left',
                                    'padding': '12px',
                                    'fontFamily': 'Segoe UI',
                                    'border' : 'none',
                                    'borderBottom' : '1px solid #eee'
                                },
                                style_data_conditional = [{
                                    'if' : {'column_id' : 'Libellé tableau de MP'},
                                    'color' : '#2C3E50',
                                    'fontWeight' : '500'
                                }],
                                page_size=5, # Affiche un maximum de 5 lignes pour rester compact
                                style_table={'overflowX': 'auto', 'overflowY' : 'auto'}
                            )
                        ], width = 12),
                        dbc.Col([
                            html.H5("Profils les plus exposés (nombre de décès)", className="mb-3 text-muted"),
                            dcc.Graph(id='graph-heatmap-deces')
                        ], width = 12, style = {'padding' : '20px'})
                    ])
                ])
            ], className="shadow border-0 mt-4")
        )
    ])
], style = {'padding' : '2rem'})


app.layout = html.Div([
    # Les filtres
    html.Div(
        dbc.Container(
            filtres,
            fluid = True
        ),
        style = {
            "position": "sticky",
            "top": "0",
            "zIndex": "1020",
            "backgroundColor": "#ffffff",
            "borderBottom": "2px solid #18BC9C",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        }
    ),
    
    # Le titre
    dbc.Container(
       dbc.Row(titre),
       fluid = True
    ),
    
    # Le contenu
    dbc.Container(
        dbc.Row([dbc.Col(contenu)]),
        fluid = True, className = "mt-4"
    )
])



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
    
    df_filtre['Maladie'] = df_filtre['Libellé tableau de MP'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=50)))
    df_groupe = df_filtre.groupby('Maladie')['Nombre de MP en premier règlement'].sum().reset_index()
    
    df_top10 = df_groupe.sort_values(by='Nombre de MP en premier règlement', ascending=False).head(10) # Les 10 premiers
    
    df_top10 = df_top10.sort_values(by='Nombre de MP en premier règlement', ascending=True) # Pour inverser l'ordre des barres avant le dessin 
    
    df_top10 = df_top10[df_top10['Nombre de MP en premier règlement'] > 0]
    
    fig = px.bar(
        df_top10,
        x='Nombre de MP en premier règlement',
        y='Maladie',
        orientation='h', # C'est cette option qui met les barres à l'horizontale
        labels={
            'Nombre de MP en premier règlement': 'Nombre de nouveaux cas',
            'Maladie': '' # On vide ce titre car les noms parlent d'eux-mêmes
        },
        color_discrete_sequence=["#4682B4"] # Une couleur sobre et pro (bleu nuit)
    )
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'), # Une grille légère verticale pour lire les montants
        yaxis=dict(showgrid=False), # Pas de grille horizontale pour ne pas surcharger
        plot_bgcolor='rgba(0,0,0,0)', # Fond transparent pour s'intégrer parfaitement à ton thème
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=200, r=20, t=50, b=0) # On ajuste les marges pour que le graphique respire
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
    
    df_ip['Maladie'] = df_ip['Libellé tableau de MP'].apply(lambda x: "<br>".join(textwrap.wrap(x, width=50)))
    
    df_ip['Taux moyen IP (%)'] = df_ip['Somme des taux d\'IP'] / df_ip['Nombre de nouvelles IP']
    
    # On garde les 10 maladies les plus invalidantes (et on trie pour l'affichage de bas en haut)
    df_top_ip = df_ip.sort_values(by='Taux moyen IP (%)', ascending=True).tail(10)
    
    fig = px.bar(
        df_top_ip,
        x='Taux moyen IP (%)',
        y='Maladie',
        orientation='h',
        title="Top des maladies les plus invalidantes (Taux moyen d'IP)",
        labels={
            'Taux moyen IP (%)': 'Taux d\'incapacité (%)',
            'Maladie': 'Maladie'
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
        color = 'Nombre de journées perdues',
        color_continuous_scale = 'Reds'
    )
    
    fig_scatter.update_traces(marker=dict(size = 10, opacity=0.8, line=dict(width=1, color='Black')))
    fig_scatter.update_layout(template = "plotly_white", coloraxis_showscale = False)
    
    fig_scatter.update_xaxes(showgrid = False, zeroline = True, zerolinecolor = 'lightgray')
    fig_scatter.update_yaxes(showgrid = True, gridcolor = 'whitesmoke')
    
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

    # Création du graphique en barres groupées
    fig = px.bar(
        df_profil,
        x='Libellé durée d\'exposition',
        y='Nombre de MP en premier règlement',
        color='libellé sexe',
        barmode='group', # L'option clé pour mettre les barres côte à côte
        labels={
            'Nombre de MP en premier règlement': 'Nombre de cas',
            'Libellé durée d\'exposition': 'Durée d\'exposition',
            'libellé sexe': 'Sexe'
        },
        # On définit des couleurs claires pour différencier facilement
        color_discrete_map={
            'Masculin': '#5dade2',
            'Féminin': '#18BC9C',
            'Non précisé': '#BDC3C7' # Gris pour les valeurs vides/inconnues
        }
    )
    
    # Ajustements esthétiques
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
    
    ordre_duree = ["Moins de six mois", "Six mois à un an", "Un à cinq ans", 
                "Cinq à dix ans", "Plus de dix ans", "Non précisé"]

    fig.update_xaxes(categoryorder='array', categoryarray=ordre_duree)
    
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
        
    df_mort = df_filtre[df_filtre['Nombre de décès'] > 0]
    df_deces = df_filtre
    
    if df_mort.empty:
        fig_vide = px.density_heatmap(title="Aucun décès recensé pour cette sélection")
        fig_vide.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig_vide
    
    fig = px.density_heatmap(
        df_deces,
        x="Libellé durée d'exposition",
        y="libellé tranche d\'age",
        z="Nombre de décès",
        histfunc="sum", # C'est ici qu'on dit à Plotly d'additionner les décès par case
        labels={
            "Libellé durée d'exposition": "Durée d'exposition",
            "libellé tranche d\'age": "Tranche d'âge",
            "Nombre de décès": "Décès"
        },
        color_continuous_scale=[[0, '#ffffff'], [0.1, '#fee5d9'], [1, '#a50f15']], # Une échelle de couleur rouge pour l'alerte
        text_auto=False, # Affiche le nombre de décès directement au centre de chaque case 
        category_orders={
            "Libellé durée d'exposition": ["Moins de six mois", "Six mois à un an", "Un à cinq ans", "Cinq à dix ans", "Plus de dix ans", "Non précisé"],
            "libellé tranche d\'age": ["Moins de 20 ans", "de 20 à 24 ans", "de 25 à 29 ans", "de 30 à 34 ans", "de 35 à 39 ans", "de 40 à 49 ans", "de 50 à 59 ans", "de 60 à 64 ans", "65 ans et plus"]
        }
    )
    
    # Finitions
    fig.update_layout(
        plot_bgcolor='white',
        coloraxis_showscale=False, # On cache la barre de couleur à côté car les chiffres sont dans les cases
        xaxis_title = None,
        yaxis_title = None,
        margin = dict(l = 10, r = 10, t = 10, b = 10),
        height = 350
    )
    
    fig.update_xaxes(showgrid = False)
    fig.update_yaxes(showgrid = False)

    return fig
    
if __name__ == '__main__':
    app.run(debug = True)
