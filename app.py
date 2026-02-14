import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Initialisation de l'application 
app = dash.Dash(__name__)
server = app.server # Pour le déploiement

df = pd.DataFrame({
    "Fruit": ["Pommes", "Oranges", "Bananes"],
    "Quantité": [4, 1, 2]
})

fig = px.bar(df, x="Fruit", y="Quantité", title="Mon dashboard de qualité")

app.layout = html.Div([
    html.H1("Risques professionnels"),
    dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run(debug = True)