# neighborly_dash_local_fixed.py
import dash
from dash import html, dcc, Input, Output, State, callback_context
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
                dbc.Button("Delete", color="danger",
                           id={'type': 'delete-btn', 'index': ad.get('id')},
                           className='ms-2')
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


# --- Combined Add / Edit callback
# This single callback handles both creating a new ad and saving an edited ad.
# It is the ONLY callback that writes to 'url.href' (so no duplicate-output problems).
@app.callback(
    Output('url', 'href'),
    Input('submit-new-ad', 'n_clicks'),
    Input('save-edit', 'n_clicks'),
    State('url', 'pathname'),
    State('new-title', 'value'),
    State('new-city', 'value'),
    State('new-description', 'value'),
    State('new-email', 'value'),
    State('new-imgurl', 'value'),
    State('new-price', 'value'),
    State('edit-title', 'value'),
    State('edit-city', 'value'),
    State('edit-description', 'value'),
    State('edit-email', 'value'),
    State('edit-imgurl', 'value'),
    State('edit-price', 'value'),
    prevent_initial_call=True
)
def handle_add_or_edit(
    new_click, save_click, pathname,
    new_title, new_city, new_desc, new_email, new_img, new_price,
    edit_title, edit_city, edit_desc, edit_email, edit_img, edit_price
):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    global NEXT_ID

    if trigger_id == 'submit-new-ad':
        # create new ad
        ADS_DB.append({
            'id': NEXT_ID,
            'title': new_title or "",
            'city': new_city or "",
            'description': new_desc or "",
            'email': new_email or "",
            'imgUrl': new_img or "",
            'price': new_price or ""
        })
        NEXT_ID += 1

    elif trigger_id == 'save-edit':
        # save edits - pathname contains /edit/<id>
        try:
            ad_id = int(pathname.split('/')[-1])
        except Exception:
            # invalid id — just go home
            return '/'
        for ad in ADS_DB:
            if ad['id'] == ad_id:
                ad.update({
                    'title': edit_title or "",
                    'city': edit_city or "",
                    'description': edit_desc or "",
                    'email': edit_email or "",
                    'imgUrl': edit_img or "",
                    'price': edit_price or ""
                })
                break

    # After add/edit, navigate back to home (update Location.href)
    return '/'


# --- Delete ad callback ---
# This updates the ads-list children directly (no effect on url)
@app.callback(
    Output('ads-list', 'children'),
    Input({'type': 'delete-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def delete_ad(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # which delete button was pressed
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        ad_id = json.loads(button_id)['index']
    except Exception:
        raise dash.exceptions.PreventUpdate

    # remove ad
    global ADS_DB
    ADS_DB = [ad for ad in ADS_DB if ad['id'] != ad_id]

    # return fresh children for ads-list
    return build_ads_cards()


# --- Run app ---
if __name__ == '__main__':
    app.run(debug=True, port=8051)
