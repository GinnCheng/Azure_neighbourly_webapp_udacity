import os
import json
import requests
import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")

if not API_BASE_URL.startswith("https://"):
    raise RuntimeError("API_BASE_URL must start with https://")

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
    r = requests.post(f"{API_BASE_URL}/createadvertisement", json=payload)
    r.raise_for_status()

def api_update_ad(ad_id, payload):
    r = requests.put(f"{API_BASE_URL}/updateadvertisement/{ad_id}", json=payload)
    r.raise_for_status()

def api_delete_ad(ad_id):
    r = requests.delete(f"{API_BASE_URL}/deleteadvertisement/{ad_id}")
    r.raise_for_status()

def api_get_posts():
    r = requests.get(f"{API_BASE_URL}/getposts")
    r.raise_for_status()
    return r.json()

def api_get_post(post_id):
    r = requests.get(f"{API_BASE_URL}/getpost/{post_id}")
    r.raise_for_status()
    return r.json()

# =========================
# Dash app init
# =========================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

sidebar = dbc.Col([
    html.H2("My Neighborhood", className="display-6"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Marketplace", href="/", active="exact"),
        dbc.NavLink("News", href="/posts", active="exact"),
    ], vertical=True, pills=True),
], width=2)

content = dbc.Col(html.Div(id="page-content"), width=10)

app.layout = dbc.Container([
    dcc.Location(id="url"),
    dbc.Row([sidebar, content])
], fluid=True)

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
        cards.append(dbc.Card([
            dbc.CardBody([
                html.H4(ad.get("title", "No title")),
                html.P(ad.get("description", "")),
                html.P(f"City: {ad.get('city', '')} | Price: {ad.get('price', '')}"),
                dbc.Button("Edit", color="warning", href=f"/edit/{ad_id}"),
                dbc.Button("Delete", color="danger", id={"type": "delete-btn", "index": ad_id}, className="ms-2")
            ])
        ], className="mb-3"))
    return cards

def build_post_cards():
    try:
        posts = api_get_posts()
    except Exception as e:
        return [html.P(f"Error loading posts: {e}")]

    if not posts:
        return [html.P("No posts found.")]

    cards = []
    for post in posts:
        post_id = post["_id"]
        cards.append(dbc.Card([
            dbc.CardBody([
                html.H5(post.get("title", "Untitled")),
                html.P(post.get("content", "")[:100] + "..."),
                html.P(f"Author: {post.get('author', 'Unknown')} | Category: {post.get('category', '')}"),
                dbc.Button("View Details", href=f"/post/{post_id}", color="primary", size="sm")
            ])
        ], className="mb-3"))
    return cards

def make_post_detail_layout(post):
    return dbc.Container([
        html.H2(post.get("title", "")),
        html.P(post.get("content", "")),
        html.P(f"Author: {post.get('author', '')}"),
        html.P(f"Date: {post.get('date', '')}"),
        html.Br(),
        dcc.Link("Back to News", href="/posts")
    ])

def layout_ads():
    return dbc.Container([
        html.H2("Advertisements"),
        dbc.Button("Add Advertisement", href="/add", color="primary"),
        html.Div(build_ads_cards(), id="ads-list")
    ])

def layout_add_ad():
    return dbc.Container([
        dbc.Alert(id="action-feedback", is_open=False),
        html.H2("Add New Advertisement"),
        dbc.Form([
            dbc.Label("Title"), dbc.Input(id="new-title"),
            dbc.Label("City"), dbc.Input(id="new-city"),
            dbc.Label("Description"), dbc.Textarea(id="new-description"),
            dbc.Label("Price"), dbc.Input(id="new-price"),
            html.Br(),
            dbc.Button("Submit", id="submit-new-ad", color="success")
        ])
    ])

def layout_edit_ad(ad):
    return dbc.Container([
        dbc.Alert(id="action-feedback", is_open=False),
        html.H2("Edit Advertisement"),
        dbc.Form([
            dbc.Label("Title"), dbc.Input(id="edit-title", value=ad.get("title", "")),
            dbc.Label("City"), dbc.Input(id="edit-city", value=ad.get("city", "")),
            dbc.Label("Description"), dbc.Textarea(id="edit-description", value=ad.get("description", "")),
            dbc.Label("Price"), dbc.Input(id="edit-price", value=ad.get("price", "")),
            html.Br(),
            dbc.Button("Save Changes", id="save-edit", color="success")
        ])
    ])

def layout_posts():
    return dbc.Container([
        html.H2("Community Posts"),
        html.Div(build_post_cards())
    ])

# =========================
# Routing
# =========================

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/add":
        return layout_add_ad()
    if pathname and pathname.startswith("/edit/"):
        ad_id = pathname.split("/")[-1]
        try:
            ad = api_get_ad(ad_id)
            return layout_edit_ad(ad)
        except:
            return html.P("Ad not found.")
    if pathname == "/posts":
        return layout_posts()
    if pathname and pathname.startswith("/post/"):
        post_id = pathname.split("/")[-1]
        try:
            post = api_get_post(post_id)
            return make_post_detail_layout(post)
        except:
            return html.P("Post not found.")
    return layout_ads()

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
    State("new-price", "value"),
    prevent_initial_call=True
)
def create_ad(n, title, city, desc, price):
    if not n:
        raise dash.exceptions.PreventUpdate

    payload = {
        "title": (title or "").strip(),
        "city": (city or "").strip(),
        "description": (desc or "").strip(),
        "price": (price or "").strip(),
    }

    try:
        resp = requests.post(f"{API_BASE_URL}/createadvertisement", json=payload)
        if resp.status_code == 201:
            return True, "Advertisement created successfully!", "success", "/"
        return True, f"Error: {resp.text}", "danger", dash.no_update
    except Exception as e:
        return True, f"Network error: {e}", "danger", dash.no_update

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
    State("edit-price", "value"),
    prevent_initial_call=True
)
def save_edit(n, pathname, title, city, desc, price):
    if not n:
        raise dash.exceptions.PreventUpdate
    try:
        ad_id = pathname.split("/")[-1]
    except:
        return True, "Invalid ID.", "danger", dash.no_update

    payload = {
        "title": (title or "").strip(),
        "city": (city or "").strip(),
        "description": (desc or "").strip(),
        "price": (price or "").strip(),
    }

    if not any(payload.values()):
        return True, "Please update at least one field.", "warning", dash.no_update

    try:
        resp = requests.put(f"{API_BASE_URL}/updateadvertisement/{ad_id}", json=payload)
        if resp.status_code == 200:
            return True, "Changes saved successfully!", "success", "/"
        if resp.status_code == 404:
            return True, "Ad not found.", "warning", dash.no_update
        return True, f"Error: {resp.text}", "danger", dash.no_update
    except Exception as e:
        return True, f"Network error: {e}", "danger", dash.no_update

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

if __name__ == "__main__":
    app.run(debug=True, port=8051)