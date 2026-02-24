import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Initialisation de l'application 
app = dash.Dash(__name__)
server = app.server # Pour le déploiement

# Chargement des données
# df = ...

# Disposition de la page
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Risques Professionnels en France", className = "text-center mt-3"))
    ]),
    
    html.Div([
        # La profession
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='dropdown-profession', placeholder = "Rechercher une profession", searchable = True)
            ], width = 12, className = "mb-3")
        ]),
        
        # Les filtres
        dbc.Row([
            dbc.Col([
                html.Label("Année"),
                dcc.Dropdown(id='dropdown-annee', options = [2021, 2023], value = 2023)
            ], width = 4),
            dbc.Col([
                html.Label("Tranche d'âge"),
                dcc.Dropdown(id='dropdown-age', options = ["Moins de 20 ans", "20 à 24 ans", "25 à 29 ans", "30 à 34 ans", "35 à 39 ans", "40 à 49 ans", "50 à 59 ans", "60 à 64 ans", "65ans et plus"], value = "20 à 24 ans")
            ], width = 4),
            dbc.Col([
                html.Label("Durée d'exposition"),
                dcc.Dropdown(id='dropdown-expo', options = ["Indifférent", "Moins de six mois", "Six mois à un an", "Un à cinq ans", "Cinq à dix ans", "Plus de 10 ans"], value = "Indifférent")
            ], width = 4),
            dbc.Col([
                html.Label("Sexe"),
                dcc.Dropdown(id='dropdown-sexe', options = ["Masculin", "Féminin"], value = "Féminin")
            ], width = 4)
        ], className = "mb-4")
    ], style = {'backgroundColor': '#222', 'padding': '20px', 'borderRadius': '10px'}),
    
    # Les graphiques 
    dbc.Row([
        dbc.Col([
            html.H3("Maladies fréquentes (Nouveaux cas)"),
            dcc.Graph(id = 'graph-frequence')
        ], width = 12, className = "mb-4")
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Maladies responsables d'incapacités permanentes (IP)"),
            dcc.Graph(id = 'graph-ip')
        ], width = 12, className = "mb-4")
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H3("Maladies mortelles (décès)"),
            dcc.Graph(id = 'graph-morts')
        ], width = 12, className = "mb-4")
        ])
], fluid = True)

# Les callbacks
@app.callback(
    [Output('graph-frequence', 'figure'),
     Output('graph-ip', 'figure'),
     Output('graph-morts', 'figure')],
    [Input('dropdown-profession', 'value'),
     Input('dropdown-annee', 'value'),
     Input('dropdown-age', 'value'),
     Input('dropdown-expo', 'value'),
     Input('dropdown-sexe', 'value')]
)
def update_graphe(profession, annee, age, expo, sexe):
    return {}, {}, {}


if __name__ == '__main__':
    app.run(debug = True)