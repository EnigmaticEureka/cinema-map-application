import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# --- Load Data ---
df = pd.read_csv("Mail-Adressen-rapidmail-with-coordinates.csv", encoding="ISO-8859-1")
df = df.dropna(subset=["Latitude", "Longitude"])

# Clean status
df["status"] = df["status"].astype(str).str.strip()

# Custom hovertext
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

# --- Dash App ---
app = dash.Dash(__name__)
app.title = "Kino Map"

# Create figure
fig = px.scatter_map(
    df,
    lat="Latitude",
    lon="Longitude",
    color="status",
    hover_name="hovertext",
    hover_data={"Latitude": False, "Longitude": False, "email": False, "status": False, "Kino": False, "Ort": False},
    zoom=5,
    height=700,
    color_discrete_map=color_map,
)
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    uirevision='constant'
)
fig.update_traces(marker=dict(size=10, opacity=1), customdata=df[["email", "Kino", "Ort", "status"]].values)

# Layout
app.layout = html.Div([
    html.H1("🎬 Interaktive Kino-Karte"),
    html.Div([
        dcc.Graph(id="map", figure=fig, style={"flex": "3"}),
        html.Div(id="info-box", style={
            "flex": "1",
            "margin": "20px",
            "padding": "15px",
            "border": "1px solid #ccc",
            "borderRadius": "10px",
            "backgroundColor": "#f9f9f9",
            "fontFamily": "monospace",
            "whiteSpace": "pre-wrap",
            "height": "fit-content"
        })
    ], style={"display": "flex", "flexDirection": "row"})
])

# Callback to update info box on click
@app.callback(
    Output("info-box", "children"),
    Input("map", "clickData")
)
def display_click_info(clickData):
    if clickData:
        point = clickData['points'][0]['customdata']
        email, kino, ort, status = point
        return f"📬 Email: {email}\n🎬 Kino: {kino}\n📍 Ort: {ort}\n❓ Status: {status}"
    return "🖱️ Klicken Sie auf einen Punkt, um Details zu sehen."

# Run app
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
