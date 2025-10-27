# neighborly_dash_local_fixed.py
import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
import json

# --- In-memory "database" for local testing ---
ADS_DB = [
    {
        "id": 1,
        "title": "Gardening Service",
        "city": "Sydney",
        "description": "I can help with your garden.",
        "email": "gardener@example.com",
        "imgUrl": "",
        "price": "50"
    },
    {
        "id": 2,
        "title": "Yoga Classes",
        "city": "Melbourne",
        "description": "Weekly online yoga sessions.",
        "email": "yoga@example.com",
        "imgUrl": "",
        "price": "30"
    }
]
NEXT_ID = 3

# --- Initialize app ---
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server

# --- Helpers to build UI fragments ---
def build_ads_cards():
    """Return a list of Card components based on ADS_DB."""
    cards = []
    if not ADS_DB:
        cards.append(html.P("No advertisements yet."))

    for ad in ADS_DB:
        card_children = []
        if ad.get('imgUrl'):
            card_children.append(dbc.CardImg(src=ad['imgUrl'], top=True))
        card_children.append(
            dbc.CardBody([
                html.H4(ad.get('title', 'No title')),
                html.P(ad.get('description', '')),
                html.P(f"City: {ad.get('city', '')} | Price: {ad.get('price', '')}"),
                dbc.Button("Edit", color="warning", href=f"/edit/{ad.get('id')}"),
                dbc.Button(
                    "Delete",
                    color="danger",
                    id={'type': 'delete-btn', 'index': ad.get('id')},
                    className='ms-2'
                )
            ])
        )
        cards.append(dbc.Card(card_children, className='mb-3'))

    return cards

def generate_home_layout():
    return dbc.Container([
        html.H2("Advertisements"),
        html.Div(build_ads_cards(), id='ads-list'),
        html.Br(),
        dbc.Button("Add Advertisement", id='add-ad-btn', href='/add', color='primary')
    ])

def make_add_layout():
    return dbc.Container([
        html.H2("Add New Advertisement"),
        dbc.Form([
            dbc.Label("Title"), dbc.Input(id='new-title', type='text'),
            dbc.Label("City"), dbc.Input(id='new-city', type='text'),
            dbc.Label("Description"), dbc.Textarea(id='new-description'),
            dbc.Label("Email"), dbc.Input(id='new-email', type='email'),
            dbc.Label("Image URL"), dbc.Input(id='new-imgurl', type='text'),
            dbc.Label("Price"), dbc.Input(id='new-price', type='text'),
            html.Br(),
            dbc.Button("Submit", id='submit-new-ad', color='success')
        ]),
        html.Br(),
        dcc.Link("Back to Home", href='/')
    ])

def make_edit_layout(ad):
    # ad is a dict; prefill values
    return dbc.Container([
        html.H2("Edit Advertisement"),
        dbc.Form([
            dbc.Label("Title"), dbc.Input(id='edit-title', type='text', value=ad.get('title', '')),
            dbc.Label("City"), dbc.Input(id='edit-city', type='text', value=ad.get('city', '')),
            dbc.Label("Description"), dbc.Textarea(id='edit-description', value=ad.get('description', '')),
            dbc.Label("Email"), dbc.Input(id='edit-email', type='email', value=ad.get('email', '')),
            dbc.Label("Image URL"), dbc.Input(id='edit-imgurl', type='text', value=ad.get('imgUrl', '')),
            dbc.Label("Price"), dbc.Input(id='edit-price', type='text', value=ad.get('price', '')),
            html.Br(),
            dbc.Button("Save Changes", id='save-edit', color='success')
        ]),
        html.Br(),
        dcc.Link("Back to Home", href='/')
    ])

# --- Main layout with URL routing ---
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
], fluid=True)

# --- Validation layout (declares all possible IDs to silence "nonexistent" warnings) ---
app.validation_layout = html.Div([
    dcc.Location(id='url'),
    html.Div(id='page-content'),
    # Home skeleton
    html.Div([
        html.Div(id='ads-list'),
        dbc.Button("Add Advertisement", id='add-ad-btn')
    ]),
    # Add page skeleton
    html.Div([
        dbc.Input(id='new-title'),
        dbc.Input(id='new-city'),
        dbc.Textarea(id='new-description'),
        dbc.Input(id='new-email'),
        dbc.Input(id='new-imgurl'),
        dbc.Input(id='new-price'),
        dbc.Button(id='submit-new-ad')
    ]),
    # Edit page skeleton
    html.Div([
        dbc.Input(id='edit-title'),
        dbc.Input(id='edit-city'),
        dbc.Textarea(id='edit-description'),
        dbc.Input(id='edit-email'),
        dbc.Input(id='edit-imgurl'),
        dbc.Input(id='edit-price'),
        dbc.Button(id='save-edit')
    ])
])

# --- Page routing (renders appropriate layout) ---
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/add':
        return make_add_layout()
    elif pathname and pathname.startswith('/edit/'):
        # parse id
        try:
            ad_id = int(pathname.split('/')[-1])
        except Exception:
            return html.P("Invalid ad id in URL.")
        ad = next((a for a in ADS_DB if a['id'] == ad_id), None)
        if not ad:
            return html.P("Advertisement not found.")
        return make_edit_layout(ad)
    else:
        return generate_home_layout()

# --- Add callback (only references NEW inputs) ---
@app.callback(
    Output('url', 'href', allow_duplicate=True),
    Input('submit-new-ad', 'n_clicks'),
    State('new-title', 'value'),
    State('new-city', 'value'),
    State('new-description', 'value'),
    State('new-email', 'value'),
    State('new-imgurl', 'value'),
    State('new-price', 'value'),
    prevent_initial_call=True
)
def create_ad(n, title, city, desc, email, img, price):
    if not n:
        return no_update
    global NEXT_ID
    ADS_DB.append({
        'id': NEXT_ID,
        'title': title or "",
        'city': city or "",
        'description': desc or "",
        'email': email or "",
        'imgUrl': img or "",
        'price': price or ""
    })
    NEXT_ID += 1
    return '/'  # navigate home

# --- Edit callback (only references EDIT inputs) ---
@app.callback(
    Output('url', 'href', allow_duplicate=True),
    Input('save-edit', 'n_clicks'),
    State('url', 'pathname'),
    State('edit-title', 'value'),
    State('edit-city', 'value'),
    State('edit-description', 'value'),
    State('edit-email', 'value'),
    State('edit-imgurl', 'value'),
    State('edit-price', 'value'),
    prevent_initial_call=True
)
def save_ad(n, pathname, title, city, desc, email, img, price):
    if not n:
        return no_update
    try:
        ad_id = int(pathname.split('/')[-1])
    except Exception:
        return '/'  # invalid URL; just go home
    for ad in ADS_DB:
        if ad['id'] == ad_id:
            ad.update({
                'title': title or "",
                'city': city or "",
                'description': desc or "",
                'email': email or "",
                'imgUrl': img or "",
                'price': price or ""
            })
            break
    return '/'  # navigate home

# --- Delete ad callback (pattern-matching for dynamic delete buttons) ---
@app.callback(
    Output('ads-list', 'children'),
    Input({'type': 'delete-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def delete_ad(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    # which delete button was pressed
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        ad_id = json.loads(button_id)['index']
    except Exception:
        return no_update

    global ADS_DB
    ADS_DB = [ad for ad in ADS_DB if ad['id'] != ad_id]
    return build_ads_cards()

# --- Run app ---
if __name__ == '__main__':
    app.run(debug=True, port=8051)
