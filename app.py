import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialisation de l'application 
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.FLATLY])

def charger_fusionner_et_nettoyer(fichier_2021, fichier_2023):
    """
    Docstring pour charger_et_nettoyer
    Cette fonction va charger les données depuis les deux fichiers Excel, les fusionner et les nettoyer.
    
    :param chemin: Le chemin vers le fichier excel
    """
    
    # On sélectionne uniquement les colonnes qui nous seront utiles lors du chargement
    colonnes_utiles = [
        'libellé profession', 
        'libellé tranche d\'age', 
        'libellé sexe', 
        'Libellé durée d\'exposition', 
        'Libellé syndrome/ CIM 10',
        'Nombre de MP en premier règlement', 
        'Nombre de nouvelles IP', 
        'dont IP avec taux < 10%',
        'dont IP avec taux >= 10%',
        'Nombre de décès', 
        'Nombre de journées perdues', 
        'Somme des taux d\'IP'
    ]
    df_21 = pd.read_excel(fichier_2021, usecols = colonnes_utiles, engine = 'openpyxl')
    df_23 = pd.read_excel(fichier_2023, usecols = colonnes_utiles, engine = 'openpyxl')
    
    # On ajoute une colonne "Année" à chacun d'eux avant la fusion
    df_21['Année'] = 2021
    df_23['Année'] = 2023
    
    # La fameuse fusion
    df = pd.concat([df_21, df_23], ignore_index = True)
    
    # On force le format numérique pour les colonnes de calcul et on remplace les vides par des 0
    colonnes_num = [
        'Nombre de MP en premier règlement', 
        'Nombre de nouvelles IP', 
        'dont IP avec taux < 10%', 
        'dont IP avec taux >= 10%', 
        'Nombre de décès', 
        'Nombre de journées perdues', 
        'Somme des taux d\'IP'
    ]
    for col in colonnes_num:
        df[col] = pd.to_numeric(df[col], errors = 'coerce').fillna(0)
        
    # On s'occupe ensuite des vaelurs textuelles vides
    colonnes_texte = [
        'libellé profession', 
        'libellé tranche d\'age', 
        'libellé sexe', 
        'Libellé durée d\'exposition', 
        'Libellé syndrome/ CIM 10'
    ]
    for col in colonnes_texte:
        df[col] = df[col].fillna('Non renseigné')
        
    return df

df_final = charger_fusionner_et_nettoyer("mp2021.xlsx", "mp2023.xlsx")


# Les listes déroulantes
professions_uniques = df_final["libellé profession"].unique()

ages_uniques = [
    "Moins de 20 ans", 
    "20 à 24 ans", 
    "25 à 29 ans", 
    "30 à 34 ans", 
    "35 à 39 ans", 
    "40 à 49 ans", 
    "50 à 59 ans", 
    "60 à 64 ans", 
    "65ans et plus"
]

# Disposition de la page

filtres = html.Div([
        # La profession
        dbc.Row([
            dbc.Label("Profession", className = 'fw-bold'),
            dbc.Col([
                dcc.Dropdown(id='dropdown-profession', 
                             placeholder = "Rechercher une profession", 
                             options = [{'label' : prof, 'value' : prof} for prof in professions_uniques],
                             value = professions_uniques[1],
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
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Total des cas", className = 'card-title'), html.H2(id = 'kpi-cas', className = 'text-info')]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Journées perdues", className = 'card-title'), html.H2(id = 'kpi-jours', className = 'text-warning')]))),
        dbc.Col(dbc.Card(dbc.CardBody([html.H5("Gravité moyenne", className = 'card-title'), html.H2(id = 'kpi-gravite', className = 'text-danger')])))
    ], className = 'mb-5'),
    
    # Les graphiques 
    # Fréquentes
    dbc.Row([
        dbc.Col([
            html.H3("Maladies fréquentes (Nouveaux cas)"),
            dcc.Graph(id = 'graph-frequence')
        ], width = 12, className = "mb-4")
    ]),
    
    # Incapacitantes
    dbc.Row([
        dbc.Col([
            html.H3("Maladies responsables d'incapacités permanentes (IP)"),
            dcc.Graph(id = 'graph-ip')
        ], width = 12, className = "mb-4")
    ]),
    
    # Mortelles
    dbc.Row([
        dbc.Col([
            html.H3("Maladies mortelles (décès)"),
            dcc.Graph(id = 'graph-morts')
        ], width = 12, className = "mb-4")
        ])
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
    cas = df_filtre['Nombre de MP en premier règlement'].sum(numeric_only=True)
    jours = df_filtre['Nombre de journées perdues'].sum()
    gravite = 5
     
    return cas, jours, gravite

@app.callback(
    [Output('graph-frequence', 'figure'),
     Output('graph-ip', 'figure'),
     Output('graph-morts', 'figure')],
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value')]
)
def update_graphe(profession, annee, age):
    return {}, {}, {}


if __name__ == '__main__':
    app.run(debug = True)