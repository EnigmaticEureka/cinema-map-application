import pandas as pd
import plotly.express as px
import dash, re
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# --- Load Data ---
df = pd.read_csv("Mail-Adressen-rapidmail-with-coordinates.csv", encoding="ISO-8859-1")
df = df.dropna(subset=["Latitude", "Longitude"])
df["status"] = df["status"].astype(str).str.strip()

# Hover text
df["hovertext"] = (
    "❓ <b>Status:</b> " + df["status"] + "<br>" +
    "📬 <b>Email:</b> " + df["email"] + "<br>" +
    "🎬 <b>Kino:</b> " + df["Kino"] + "<br>" +
    "📍 <b>Ort:</b> " + df["Ort"] + "<br>" +
    "🌍 <b>Lat:</b> " + df["Latitude"].astype(str) + "<br>" +
    "🌍 <b>Lon:</b> " + df["Longitude"].astype(str)
)

# Color map
color_map = {
    "active": "#ff5c00",
    "bounced": "#ffff00",
    "deleted": "#ff0000",
    "deleted (unsubscribed)": "#ff0000",
}

# App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Kino Map"

# Base figure
fig = px.scatter_map(
    df, lat="Latitude", lon="Longitude", color="status",
    hover_name="hovertext",
    hover_data={"Latitude": False, "Longitude": False, "email": False, "status": False, "Kino": False, "Ort": False},
    zoom=5, height=700, color_discrete_map=color_map
)
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    hoverlabel=dict(bgcolor="white", font=dict(family="Arial", size=13, color="black"), bordercolor="black"),
    uirevision="constant"
)
fig.update_traces(marker=dict(size=10, opacity=1), customdata=df[["email", "Kino", "Ort", "status"]].values)

# Layout
app.layout = dbc.Container(fluid=True, children=[
    dbc.Row([
        dbc.Col([
            html.H3("🎬 CineMap"),
            html.Label("🔍 Suche Kino, Ort oder Email:"),
            dcc.Input(
                id="search-input", type="text",
                placeholder="z.B. Cineplex, Berlin, info@...",
                style={"width": "100%", "padding": "8px", "marginBottom": "15px"}
            ),
            html.Div(id="info-box", style={
                "marginBottom": "15px", "padding": "10px",
                "border": "1px solid #ccc", "borderRadius": "10px",
                "backgroundColor": "#f9f9f9", "fontSize": "12px",
                "lineHeight": "1.6", "whiteSpace": "pre-wrap"
            }),
            html.Div(id="copy-target", style={"display": "none"}),
            dcc.Clipboard(target_id="copy-target", title="Email kopieren")
        ], xs=12, md=3),

        dbc.Col([
            dcc.Graph(id="map", figure=fig, style={"height": "100vh"})
        ], xs=12, md=9)
    ])
])

# Callbacks
@app.callback(
    [Output("info-box", "children"), Output("copy-target", "children")],
    Input("map", "clickData")
)
def display_click_info(clickData):
    if clickData:
        hover = clickData['points'][0].get('hovertext', '')
        email_match = re.search(r'📬 <b>Email:</b> ([^<]+)', hover)
        kino_match = re.search(r'🎬 <b>Kino:</b> ([^<]+)', hover)
        ort_match = re.search(r'📍 <b>Ort:</b> ([^<]+)', hover)
        status_match = re.search(r'❓ <b>Status:</b> ([^<]+)', hover)

        email = email_match.group(1) if email_match else "?"
        kino = kino_match.group(1) if kino_match else "?"
        ort = ort_match.group(1) if ort_match else "?"
        status = status_match.group(1) if status_match else "?"

        info = f"📬 Email: {email}\n🎬 Kino: {kino}\n📍 Ort: {ort}\n❓ Status: {status}"
        return info, email
    return "🖱️ Klicken Sie auf einen Punkt, um Details zu sehen.", ""


@app.callback(
    Output("map", "figure"),
    Input("search-input", "value")
)
def update_map(search_text):
    if not search_text:
        return fig
    filtered = df[df.apply(lambda row:
        search_text.lower() in str(row["Kino"]).lower() or
        search_text.lower() in str(row["Ort"]).lower() or
        search_text.lower() in str(row["email"]).lower() or
        search_text.lower() in str(row["status"]).lower(),
        axis=1
    )]
    new_fig = px.scatter_map(
        filtered, lat="Latitude", lon="Longitude", color="status",
        hover_name="hovertext", zoom=5, height=700,
        title=f"Kinos gefiltert nach: '{search_text}'",
        hover_data={"Latitude": False, "Longitude": False, "email": False, "status": False, "Kino": False, "Ort": False},
        color_discrete_map=color_map,
    )
    new_fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        hoverlabel=dict(bgcolor="white", font=dict(family="Arial", size=13, color="black"), bordercolor="black"),
        uirevision="search"
    )
    new_fig.update_traces(marker=dict(size=10, opacity=1), customdata=filtered[["email", "Kino", "Ort", "status"]].values)
    return new_fig

# Run
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
