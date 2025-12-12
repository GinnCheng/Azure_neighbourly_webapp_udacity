# neighborly_dash_api.py
import os
import json
import requests
import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# =========================
# API configuration
# =========================

load_dotenv()
API_BASE_URL = os.getenv(
    "API_BASE_URL"
)

if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL not set")

# =========================
# API helper functions
# =========================
def api_get_ads():
    r = requests.get(f"{API_BASE_URL}/getadvertisements")
    r.raise_for_status()
    return r.json()

def api_get_ad(ad_id):
    r = requests.get(f"{API_BASE_URL}/getadvertisement/{ad_id}")
    r.raise_for_status()
    return r.json()

def api_create_ad(payload):
    r = requests.post(
        f"{API_BASE_URL}/createadvertisement",
        json=payload
    )
    r.raise_for_status()

def api_update_ad(ad_id, payload):
    r = requests.put(
        f"{API_BASE_URL}/updateadvertisement/{ad_id}",
        json=payload
    )
    r.raise_for_status()

def api_delete_ad(ad_id):
    r = requests.delete(
        f"{API_BASE_URL}/deleteadvertisement/{ad_id}"
    )
    r.raise_for_status()

# =========================
# Dash app init
# =========================
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

# =========================
# UI builders
# =========================
def build_ads_cards():
    try:
        ads = api_get_ads()
    except Exception as e:
        return [html.P(f"Error loading ads: {e}")]

    if not ads:
        return [html.P("No advertisements yet.")]

    cards = []

    for ad in ads:
        ad_id = ad["_id"]
        card_children = []

        if ad.get("imgUrl"):
            card_children.append(dbc.CardImg(src=ad["imgUrl"], top=True))

        card_children.append(
            dbc.CardBody([
                html.H4(ad.get("title", "No title")),
                html.P(ad.get("description", "")),
                html.P(f"City: {ad.get('city', '')} | Price: {ad.get('price', '')}"),
                dbc.Button("Edit", color="warning", href=f"/edit/{ad_id}"),
                dbc.Button(
                    "Delete",
                    color="danger",
                    id={"type": "delete-btn", "index": ad_id},
                    className="ms-2"
                )
            ])
        )

        cards.append(dbc.Card(card_children, className="mb-3"))

    return cards

def generate_home_layout():
    return dbc.Container([
        html.H2("Advertisements"),
        html.Div(build_ads_cards(), id="ads-list"),
        html.Br(),
        dbc.Button("Add Advertisement", href="/add", color="primary")
    ])

def make_add_layout():
    return dbc.Container([
        dbc.Alert(id="action-feedback", is_open=False),
        html.H2("Add New Advertisement"),
        dbc.Form([
            dbc.Label("Title"), dbc.Input(id="new-title"),
            dbc.Label("City"), dbc.Input(id="new-city"),
            dbc.Label("Description"), dbc.Textarea(id="new-description"),
            dbc.Label("Email"), dbc.Input(id="new-email"),
            dbc.Label("Image URL"), dbc.Input(id="new-imgurl"),
            dbc.Label("Price"), dbc.Input(id="new-price"),
            html.Br(),
            dbc.Button("Submit", id="submit-new-ad", color="success")
        ]),
        html.Br(),
        dcc.Link("Back to Home", href="/")
    ])

def make_edit_layout(ad):
    return dbc.Container([
        dbc.Alert(id="action-feedback", is_open=False),
        html.H2("Edit Advertisement"),
        dbc.Form([
            dbc.Label("Title"), dbc.Input(id="edit-title", value=ad.get("title", "")),
            dbc.Label("City"), dbc.Input(id="edit-city", value=ad.get("city", "")),
            dbc.Label("Description"), dbc.Textarea(id="edit-description", value=ad.get("description", "")),
            dbc.Label("Email"), dbc.Input(id="edit-email", value=ad.get("email", "")),
            dbc.Label("Image URL"), dbc.Input(id="edit-imgurl", value=ad.get("imgUrl", "")),
            dbc.Label("Price"), dbc.Input(id="edit-price", value=ad.get("price", "")),
            html.Br(),
            dbc.Button("Save Changes", id="save-edit", color="success")
        ]),
        html.Br(),
        dcc.Link("Back to Home", href="/")
    ])

# =========================
# App layout
# =========================
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
], fluid=True)

# =========================
# Routing
# =========================
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/add":
        return make_add_layout()

    if pathname and pathname.startswith("/edit/"):
        ad_id = pathname.split("/")[-1]
        try:
            ad = api_get_ad(ad_id)
        except Exception:
            return html.P("Advertisement not found.")
        return make_edit_layout(ad)

    return generate_home_layout()

# =========================
# Create ad
# =========================
@app.callback(
    Output("action-feedback", "is_open", allow_duplicate=True),
    Output("action-feedback", "children", allow_duplicate=True),
    Output("action-feedback", "color", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("submit-new-ad", "n_clicks"),
    State("new-title", "value"),
    State("new-city", "value"),
    State("new-description", "value"),
    State("new-email", "value"),
    State("new-imgurl", "value"),
    State("new-price", "value"),
    prevent_initial_call=True
)
def create_ad(n, title, city, desc, email, img, price):
    if not n:
        raise dash.exceptions.PreventUpdate

    resp = requests.post(
        f"{API_BASE_URL}/createadvertisement",
        json={
            "title": title,
            "city": city,
            "description": desc,
            "email": email,
            "imgUrl": img,
            "price": price,
        }
    )

    if resp.status_code == 201:
        return True, "Advertisement created successfully!", "success", "/"

    return True, f"Error: {resp.text}", "danger", dash.no_update


# =========================
# Update ad
# =========================
@app.callback(
    Output("action-feedback", "is_open", allow_duplicate=True),
    Output("action-feedback", "children", allow_duplicate=True),
    Output("action-feedback", "color", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("save-edit", "n_clicks"),
    State("url", "pathname"),
    State("edit-title", "value"),
    State("edit-city", "value"),
    State("edit-description", "value"),
    State("edit-email", "value"),
    State("edit-imgurl", "value"),
    State("edit-price", "value"),
    prevent_initial_call=True
)
def save_edit(n, pathname, title, city, desc, email, img, price):
    if not n:
        raise dash.exceptions.PreventUpdate

    ad_id = pathname.split("/")[-1]

    resp = requests.put(
        f"{API_BASE_URL}/updateadvertisement/{ad_id}",
        json={
            "title": title,
            "city": city,
            "description": desc,
            "email": email,
            "imgUrl": img,
            "price": price,
        }
    )

    if resp.status_code == 200:
        return True, "Changes saved successfully!", "success", "/"

    return True, f"Error: {resp.text}", "danger", dash.no_update


# =========================
# Delete ad
# =========================
@app.callback(
    Output("ads-list", "children"),
    Input({"type": "delete-btn", "index": dash.dependencies.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def delete_ad(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    ad_id = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])["index"]
    api_delete_ad(ad_id)

    return build_ads_cards()

# =========================
# Run
# =========================
if __name__ == "__main__":
    app.run(debug=True, port=8051)
