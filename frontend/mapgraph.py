import dash_core_components as dcc
import dash_html_components as html


def get_map_tab_layout(funkt_id_map, disabled_cat_ausgaben):
    return html.Div([
        html.Div([
            html.Div([html.H3('Swiss Cantons'),
                      html.Div([dcc.RadioItems(
                          id='normalize-radio-map',
                          options=[
                              {'label': ' Absolute', 'value': 'absolute'},
                              {'label': ' Per Canton', 'value': 'per_canton'},
                              {'label': ' Per Year', 'value': 'per_year'}
                          ],
                          value='per_canton', labelStyle={'display': 'inline', 'margin': '5px', 'white-space': 'nowrap'}
                      )], className='normalize_radio'),
                      # html.Div([dcc.Checklist(
                      #     id='normalize-checkbox-map',
                      #     options=[
                      #         {'label': 'Normalized', 'value': 'normalized'}
                      #     ],
                      #     value=['normalized']
                      # )], className='normalize_checkbox'),
                      html.Div([dcc.Checklist(
                          id='inflation-checkbox-map',
                          options=[
                              {'label': ' Correct for inflation', 'value': 'inflation_corrected'}
                          ], value=[], style={'margin-right':'15px'}
                      ),
                          dcc.Dropdown(
                          id='map-value-dropdown',
                          options=[{'label': f'{cat[0]} - {cat[1]}', 'value': cat[0],
                                    'disabled': cat[0] in disabled_cat_ausgaben} for cat in funkt_id_map.items()],
                          value='Total', multi=False, style={'width': '300px', 'margin': '0px 0px 0px 0px'}),
                      ], className='inflation_checkbox',style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'})],
                     style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'},
                     ),
            html.Div([
                html.Div([dcc.Graph(id='graph-map', style={'margin': '0 auto', 'width': '97vw', 'height': '59.1vw',
                                                           # 63.5vw
                                                           'max-width': '100vh', 'max-height': '65.5vh',
                                                           'display': 'inline-block'}
                                    )], style={'width': '100%', 'text-align': 'center'}),
            ]),
        ],
            style={'display': 'block'}
        ),
    ])
