import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import plotly.graph_objects as go
from pathlib import Path
import os
import json
import pandas as pd
import frontend.bubblegraph
import frontend.linegraph
import frontend.mapgraph
import time

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

folder_preprocessed_data = Path(os.getcwd()) / 'data' / 'preprocessed'
df_ausgaben = pd.read_csv(folder_preprocessed_data / 'df_ausgaben_all_merged.csv', index_col=0)
df_ausgaben_infl = pd.read_csv(folder_preprocessed_data / 'df_ausgaben_all_infl_merged.csv', index_col=0)

# df_einnahmen = pd.read_csv(folder_preprocessed_data / 'df_einnahmen_all.csv', index_col=0)

with open(folder_preprocessed_data / 'funkt_id_map.json', 'r') as file:
    funkt_id_map = json.load(file)
with open(folder_preprocessed_data / 'iso_canton_map.json', 'r') as file:
    iso_canton_map = json.load(file)
with open(folder_preprocessed_data / 'population_id_map.json', 'r') as file:
    population_id_map = json.load(file)
with open(folder_preprocessed_data / 'canton_borders.json', 'r') as file:
    canton_borders = json.load(file)
with open(folder_preprocessed_data / 'canton_borders_xy.json', 'r') as file:
    canton_borders_xy = json.load(file)
with open(folder_preprocessed_data / 'inflation_rate.json', 'r') as file:
    inflation_rate = json.load(file)
with open(Path(os.getcwd()) / 'frontend' / 'assets' / 'modal_text.md', 'r') as file:
    modal_text = file.read()
disabled_cat_ausgaben = ['03', '08', '13', '18', '26', '27', '28', '38', '48', '58', '64', '68', '76', '78', '86', '88',
                         '91', '92', '93', '94', '95', '97', '99']

min_year = df_ausgaben['year'].min()
max_year = df_ausgaben['year'].max()
year_ticks = {str(y): str(y) for y in df_ausgaben['year'].unique()}
init_year = 1991
cantons = df_ausgaben['canton'].unique()
cantons.sort()  # needed so that legend is alphabetical

external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css']

gradient_start_color = [20, 70, 180, 0.7]
gradient_end_color = [169, 69, 66, 0.9]

# gradient_start_color = [0, 0, 255,0.7]
# gradient_end_color = [255, 0, 0,0.7]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# because we use tabs,
# there will be callbacks specified to elements that are not initially in
# app.layout (if there are callbacks present in the other pages or tabs). that's why we set:
app.config.suppress_callback_exceptions = True
server = app.server

app.title = 'PrettyFin'


def year_tick_formater(year_ticks):
    slider_ticks = {}
    for year in year_ticks:
        if int(year) % 2 == 0:
            slider_ticks[year] = ''
        else:
            slider_ticks[year] = year
    return slider_ticks


app.layout = html.Div([
    html.Div(
        [html.H1('PrettyFin'),
         html.Div(
             [
                 # [html.Button(html.P('Play', id='start-button-text', style={}), id='start-button')],x
                 html.Button(html.P('Info'), id='open'),
                 # dbc.Button("Help", id="open"),
                 dbc.Modal(
                     [
                         # dbc.ModalHeader('Info'),
                         html.Div([
                             dcc.Markdown(modal_text),
                         ], style={'margin': '10px 10px 10px 10px'}),

                         # dbc.ModalBody("""
                         # Prettyfin
                         # """),
                         dbc.ModalFooter(
                             # dbc.Button("Close", id="close", className="ml-auto")
                             html.Button(html.P('Close'), id='close', className='ml-auto'),
                         ),
                     ],
                     id="modal",
                     centered=True,
                     size='xl',
                     # scrollable=True,
                     tag='html'
                 ),
             ]
         )], style={'display': 'flex', 'justify-content': 'space-between',
                    'align-items': 'center', 'margin': '0px 10px 0px 0px'})
    ,
    dcc.Tabs(id="tabs", value='tab-map', children=[
        dcc.Tab(label='Bubble Graph', value='tab-graph'),
        dcc.Tab(label='Line Graph', value='tab-line'),
        dcc.Tab(label='Map', value='tab-map')
    ]),
    html.Div(id='tabs-content'),
    html.Div([
        html.Div(
            [html.Button(html.P('Play', id='start-button-text', style={}), id='start-button')],
            style={}),
        html.Div([
            dcc.Slider(
                id='year-slider',
                min=min_year,
                max=max_year,
                value=init_year,
                marks=year_tick_formater(year_ticks),
                # marks=year_ticks,
                updatemode='drag',
                step=None
            )], style={'width': '100%', 'margin': '5px 0px 0px 0px'})],
        style={'align-content': 'stretch'}, id='timeline-div'),
    html.Div([html.P(['Copyright © 2020 by ', html.A('aiger', href='https://www.aiger.ch/')])],
             style={'text-align': 'center', 'margin-top': '25px'}),
    # html.Div([html.A('Copyright © 2020 by aiger',href='https://www.aiger.ch/')], style={'text-align': 'center', 'margin-top':'25px'}),
    dcc.Interval(id='interval', disabled=True, interval=1200),
])


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback([Output('tabs-content', 'children'), Output('timeline-div', 'style')],
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-graph':
        return frontend.bubblegraph.get_bubblegraph_tab_layout(funkt_id_map, disabled_cat_ausgaben,
                                                               population_id_map), {'display': 'flex'}
    elif tab == 'tab-line':
        return frontend.linegraph.get_linegraph_tab_layout(funkt_id_map, disabled_cat_ausgaben), {'display': 'none'}
    elif tab == 'tab-map':
        return frontend.mapgraph.get_map_tab_layout(funkt_id_map, disabled_cat_ausgaben), {'display': 'flex'}


@app.callback(Output('start-button-text', 'children'), [Input('interval', 'disabled')])
def change_button_text(disabled):
    if disabled:
        return 'Play'
    else:
        return 'Stop'


@app.callback([Output('year-slider', 'value'), Output('interval', 'disabled')],
              [Input('interval', 'n_intervals'), Input('start-button', 'n_clicks')],
              [State('year-slider', 'value'),
               State('interval', 'disabled')])
def slide_adjust(n_intervals, n_clicks, slider_year, disabled):
    ctx = dash.callback_context

    if ctx.triggered[0]['prop_id'] == 'interval.n_intervals':
        print('interval')
        if disabled is not None:
            if not disabled:
                slider_year += 1
            print(slider_year)
            if slider_year > max_year:
                return dash.no_update, True
            else:
                return slider_year, dash.no_update
        else:
            return dash.no_update, dash.no_update

    if ctx.triggered[0]['prop_id'] == 'start-button.n_clicks':
        print('button')
        if n_clicks:
            interval_status = not disabled
        else:
            return dash.no_update, dash.no_update

        return dash.no_update, interval_status


@app.callback(
    Output('graph-bubbles', 'figure'),
    [Input('x-axis-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('size-dropdown', 'value'),
     Input('normalize-checkbox-bubble', 'value'),
     Input('inflation-checkbox-bubble', 'value'),
     Input('year-slider', 'value')]
)
def update_bubble(x_axis, y_axis, bubble_size_dropdown, normalize, inflation_cleaned, selected_year):
    print('update_bubble')

    if inflation_cleaned:
        df_aus = df_ausgaben_infl
    else:
        df_aus = df_ausgaben

    df_filtered = df_aus[df_aus.year == selected_year]
    traces = []
    for canton in cantons:
        df_canton = df_filtered[df_filtered['canton'] == canton]

        if normalize == ['normalized']:

            x_vals = min_max_normalize('one_canton_one_cat_all_years', df_canton[x_axis],
                                       df_aus, x_axis, canton,
                                       None)
            y_vals = min_max_normalize('one_canton_one_cat_all_years', df_canton[y_axis],
                                       df_aus, y_axis, canton,
                                       None)
            # x_vals = min_max_normalization_one_canton_all_cat(df_canton, df_ausgaben, x_axis, canton)
            # y_vals = min_max_normalization_one_canton_all_cat(df_canton, df_ausgaben, y_axis, canton)
        else:
            x_vals = df_canton[x_axis]
            y_vals = df_canton[y_axis]

        traces.append(dict(
            x=x_vals,
            y=y_vals,
            # x=df_canton[x_axis],
            # y=df_canton[y_axis],
            text=df_canton['canton'].apply(lambda x: iso_canton_map[x]),
            mode='markers',
            opacity=0.7,
            marker={
                'size': df_canton[bubble_size_dropdown] / df_aus[bubble_size_dropdown].max() * 200,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=iso_canton_map[canton]
        ))

    # factor to show some margin, because bubbles span over the edges
    extra_space_graph = 0.05
    if normalize == ['normalized']:
        x_range = [-extra_space_graph, 1 + extra_space_graph]
        y_range = [-extra_space_graph, 1 + extra_space_graph]
    else:
        x_range = [
            df_aus[x_axis].min() - extra_space_graph * (df_aus[x_axis].max() - df_aus[x_axis].min()),
            df_aus[x_axis].max() + extra_space_graph * (df_aus[x_axis].max() - df_aus[x_axis].min())]
        y_range = [
            df_aus[y_axis].min() - extra_space_graph * (df_aus[y_axis].max() - df_aus[y_axis].min()),
            df_aus[y_axis].max() + extra_space_graph * (df_aus[y_axis].max() - df_aus[y_axis].min())]
    fig = {
        'data': traces,
        'layout': dict(
            xaxis={'title': {'text': funkt_id_map[x_axis], 'font': {'size': 16}, 'standoff': 5},
                   'range': x_range, 'fixedrange': True},
            yaxis={'title': {'text': funkt_id_map[y_axis], 'font': {'size': 16}},
                   'range': y_range, 'fixedrange': True},
            margin={'l': 60, 'b': 200, 't': 10, 'r': 20},
            legend={'y': 0, 'orientation': 'h', 'yanchor': 'top', 'borderwidth': 35, 'bordercolor': '#00000000',
                    'font': {'size': 13}},
            # legend={'x': 1, 'y': 1, 'font': {'size': 13}},
            hovermode='closest',
            transition={'duration': 1000},
        )}

    return fig


@app.callback(
    Output('line-graph', 'figure'),
    [Input('y-axis-dropdown', 'value'),
     Input('normalize-checkbox-line', 'value'),
     Input('inflation-checkbox-line', 'value')]
)
def update_line(y_axis, normalize, inflation_cleaned):
    print('update_line')

    traces = []
    if inflation_cleaned:
        df_aus = df_ausgaben_infl
    else:
        df_aus = df_ausgaben

    for canton in cantons:
        df_canton = df_aus[df_aus['canton'] == canton]

        if normalize == ['normalized']:
            y_vals = min_max_normalize('one_canton_one_cat_all_years', df_canton[y_axis],
                                       df_aus, y_axis, canton,
                                       None)
        else:
            y_vals = df_canton[y_axis]

        traces.append(dict(
            x=df_canton['year'],
            y=y_vals,
            text=df_canton['canton'].apply(lambda x: iso_canton_map[x]),
            mode='lines+markers',
            opacity=0.7,
            marker={
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=iso_canton_map[canton]
        ))

    fig = {
        'data': traces,
        'layout': dict(
            xaxis={'fixedrange': True},
            yaxis={'title': {'text': funkt_id_map[y_axis], 'font': {'size': 16}},
                   'fixedrange': True},
            margin={'l': 60, 'b': 200, 't': 10, 'r': 20},
            legend={'y': 0, 'orientation': 'h', 'yanchor': 'top', 'borderwidth': 35, 'bordercolor': '#00000000',
                    'font': {'size': 13}},
            # legend={'x': 1, 'y': 1, 'font': {'size': 13}},
            hovermode='closest',
            transition={'duration': 1800},
        )}

    return fig


@app.callback(
    Output('graph-map', 'figure'),
    [Input('map-value-dropdown', 'value'),
     Input('year-slider', 'value'),
     Input('normalize-radio-map', 'value'),
     Input('inflation-checkbox-map', 'value')
     ], [State('graph-map', 'figure')])
def update_map(category, year, normalization, inflation_cleaned, fig):
    # TODO further speedup with clientside function
    # https://community.plot.ly/t/is-it-possible-to-update-just-layout-not-whole-figure-of-graph-in-callback/8300/12
    if fig is None:
        fig = go.Figure()

        canton_shapes = []
        for canton in cantons:
            canton_shape = canton_borders[canton.upper()]
            canton_shapes.append(go.layout.Shape(type='path', path=canton_shape,
                                                 line_color='rgba(25,25,25,0.1)', name=f'shape_{canton}'))
            id = 0
            for subarea in canton_borders_xy[canton.upper()]:
                fig.add_trace(
                    go.Scatter(
                        x=subarea[0],
                        y=subarea[1],
                        hoverinfo="text",
                        hoveron="fills",
                        fill="toself",
                        fillcolor='rgba(25,25,25,0.1)',
                        opacity=0,
                        name=f'hover_{canton}_{id}'
                    ))
                id += 1

        fig.update_layout(shapes=canton_shapes)

        fig.add_trace(
            go.Scatter(
                x=[0, 0],
                y=[1, 1],
                opacity=0,
                marker=dict(size=16, colorscale=[
                    [0, f'rgb({gradient_start_color[0]},{gradient_start_color[1]},{gradient_start_color[2]})'],
                    [1, f'rgb({gradient_end_color[0]},{gradient_end_color[1]},{gradient_end_color[2]})']],
                            showscale=True, cmax=1, cmin=0)
            ))
    else:
        fig = go.Figure(fig)

    if inflation_cleaned:
        df_aus = df_ausgaben_infl
    else:
        df_aus = df_ausgaben

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                      margin=go.layout.Margin(l=0, r=0, b=0, t=0, pad=0), showlegend=False)
    # Update axes properties
    fig.update_xaxes(
        range=[35, 1050],  # 85
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        fixedrange=True
    )

    fig.update_yaxes(
        range=[665, 0],  # 606
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        fixedrange=True
    )

    # canton_shapes = []
    df_filtered = df_aus[df_aus.year == year]
    for canton in cantons:
        df_canton = df_filtered[df_filtered['canton'] == canton]
        display_value_absolute = df_canton[category].values[0]

        if normalization == 'per_canton':
            display_value_normalized_scaled = min_max_normalize('one_canton_one_cat_all_years', display_value_absolute,
                                                                df_aus, category, canton,
                                                                year)
        elif normalization == 'per_year':
            display_value_normalized_scaled = min_max_normalize('all_canton_one_cat_one_year', display_value_absolute,
                                                                df_aus, category, canton,
                                                                year)
        else:
            display_value_normalized_scaled = min_max_normalize('all_canton_one_cat_all_years', display_value_absolute,
                                                                df_aus, category, canton,
                                                                year)

        display_color = value_to_heat_color(display_value_normalized_scaled)

        for trace in fig.data:
            if trace.name and trace.name.startswith(f'hover_{canton}'):
                trace.text = f'<span style="font-size:20;font-weight:bold;">{iso_canton_map[canton]}</span><br />' \
                             + f'CHF {display_value_absolute:,.{0}f}<br />' \
                             + f'{display_value_normalized_scaled * 100:.{2}f}%</span>'
        for shape in fig.layout.shapes:
            if shape.name == f'shape_{canton}':
                shape.fillcolor = display_color
    return fig


def min_max_normalize(normalize_type, display_value, df, category, canton=None, year=None):
    if normalize_type == 'one_canton_one_cat_all_years':
        scale_column = df[df['canton'] == canton][category]
    elif normalize_type == 'all_canton_one_cat_one_year':
        scale_column = df[df['year'] == year][category]
    elif normalize_type == 'all_canton_one_cat_all_years':
        scale_column = df[category]
    else:
        scale_column = None

    x = (display_value - scale_column.min()) / (
            scale_column.max() - scale_column.min())
    return x


def inflation_correction(amount, year_from, year_to=2018):
    for i in range(year_from, year_to + 1):
        amount = amount * inflation_rate[str(i)]
    return amount


def value_to_heat_color(value):
    if value is None:
        return 'rgb(0,0,0)'
    else:
        r = value * gradient_end_color[0] + (1 - value) * gradient_start_color[0]
        g = value * gradient_end_color[1] + (1 - value) * gradient_start_color[1]
        b = value * gradient_end_color[2] + (1 - value) * gradient_start_color[2]
        a = value * gradient_end_color[3] + (1 - value) * gradient_start_color[3]
        return f'rgba({round(r):.{0}f},{round(g):.{0}f},{round(b):.{0}f},{a})'


if __name__ == '__main__':
    app.run_server(debug=True)
