# Import libraries
from distutils.fancy_getopt import wrap_text
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.express as px

# Load the datasets
deaths_df = pd.read_csv('who_all_cause_deaths.csv')
pop_df = pd.read_csv('who_population.csv')
rate_df = pd.read_csv('who_ac_deaths_per_1000.csv')


def select_dataset(selected_stat):
    df_map = {
        'deaths': deaths_df,
        'pop': pop_df,
        'rate': rate_df
    }
    return df_map[selected_stat]


# Create the Dash app
app = Dash(title="WHO All Cause Mortality Dashboard",
           external_stylesheets=[dbc.themes.LUX])
load_figure_template('LUX')


# Callback inputs
stat_dropdown = dcc.Dropdown(
    options=[
        {'label': 'Total Deaths in Age Group', 'value': 'deaths'},
        {'label': 'Population', 'value': 'pop'},
        {'label': 'Deaths per 1000 People', 'value': 'rate'}
    ], value='deaths', style={'width': 400})
age_dropdown = dcc.Dropdown(
    options=deaths_df.columns[3:], value=deaths_df.columns[3], style={'width': 195})
sex_dropdown = dcc.Dropdown(
    options=deaths_df['Sex'].unique(), value='All', style={'width': 195})
country_dropdown = dcc.Dropdown(options=sorted(deaths_df['Country'].unique()),
                                value=['United States of America'], multi=True,
                                style={'width': 400, 'overflow': 'wrap'})

year_min = int(deaths_df['Year'].min())
year_max = int(deaths_df['Year'].max())
year_slider = dcc.Slider(min=year_min, max=year_max, step=1, value=2000,
                         marks={year_min: str(year_min),
                                year_max: str(year_max)},
                         tooltip={"placement": "bottom", "always_visible": True})
graph_mode_radio = dcc.RadioItems(options=[
    {'label': 'Graph over years', 'value': 'Years'},
    {'label': 'Graph over age groups', 'value': 'Age'}
], value='Years', labelStyle={"margin-right": "20px"}, inputStyle={"margin-right": "5px"})


# Layout
app.layout = html.Div(children=[
    html.H1(children='WHO All Cause Mortality',
            style={'text-align': 'center'}),
    html.Div([
        html.Div([
            html.Div([
                html.Div([html.Label("Statstic: "), stat_dropdown],
                    style={'padding': 5}),
                html.Div([
                    html.Div([html.Label("Age Group: "), age_dropdown],
                    style={'padding': 5}),
                    html.Div([html.Label("Sex: "), sex_dropdown],
                    style={'padding': 5}),
                ], style={'display': 'flex', 'flex-direction': 'row'}),
                html.Div([
                    html.Label("Year: "),
                    html.Div(year_slider, style={'flex': 1})
                ], style={'padding': 5}),
                html.Div([
                    html.Label("Countries:", style={'flex': 0, 'padding': 5}),
                    html.Div(country_dropdown, style={'flex': 1})
                ], style={'padding': 5}),
                html.Div(graph_mode_radio, style={'padding': 5, 'display': 'flex', 'flex': 2, 'align-items': 'flex-end'})
            ], style={'padding': 10, 'display': 'flex', 'flex-direction': 'column', 
                       'justify-content': 'space-between'}),
            html.Div([
                dcc.Graph(id='mortality-map',
                          style={'width': '800px', 'height': '400px'})
            ], style={'padding': 10, 'flex': 1}),
        ], style={'display': 'flex', 'flex-direction': 'row'}),
        html.Div([dcc.Graph(id='mortality-graph')], style={'padding': 10, 'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'column', 'width': '1200px', 'margin-left': 'auto', 'margin-right': 'auto'}),

])

# Map Callback function


@app.callback(
    Output(component_id='mortality-map', component_property='figure'),
    Input(component_id=stat_dropdown, component_property='value'),
    Input(component_id=age_dropdown, component_property='value'),
    Input(component_id=sex_dropdown, component_property='value'),
    Input(component_id=year_slider, component_property='value'),
)
def update_map(selected_stat, selected_age, selected_sex, selected_year):
    stat_df = select_dataset(selected_stat)
    sex_msk = stat_df['Sex'] == selected_sex
    year_msk = stat_df['Year'] == selected_year
    fig = px.choropleth(stat_df[year_msk & sex_msk], locations="Country",
                        locationmode="country names",
                        color=selected_age,
                        color_continuous_scale=px.colors.sequential.GnBu)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


# Graph Callback function
@app.callback(
    Output(component_id='mortality-graph', component_property='figure'),
    Input(component_id=graph_mode_radio, component_property='value'),
    Input(component_id=stat_dropdown, component_property='value'),
    Input(component_id=age_dropdown, component_property='value'),
    Input(component_id=country_dropdown, component_property='value'),
    Input(component_id=sex_dropdown, component_property='value'),
    Input(component_id=year_slider, component_property='value'),
)
def update_graph(graph_mode, selected_stat, selected_age, selected_countries, selected_sex, selected_year):
    stat_df = select_dataset(selected_stat)
    country_msk = stat_df['Country'].isin(selected_countries)
    sex_msk = stat_df['Sex'] == selected_sex
    year_msk = stat_df['Year'] == selected_year
    fig = None
    if graph_mode == 'Years':
        fig = px.line(stat_df[country_msk & sex_msk],
                      x='Year', y=selected_age, color='Country', markers=True)
    elif graph_mode == 'Age':
        age_columns = stat_df.columns[4:-2]
        selection = stat_df[country_msk & sex_msk &
                            year_msk].set_index('Country')
        transpose_df = selection[age_columns].transpose().reset_index()
        fig = px.line(transpose_df, x='index',
                      y=selected_countries, markers=True)
        fig.update_layout(legend_title="Country")
    fig.update_layout(yaxis={'title': None, 'visible': True, 'showticklabels': True},
                          xaxis={'title': None, 'visible': True, 'showticklabels': True})                      
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=350)
    return fig


# Run local server
if __name__ == '__main__':
    app.run_server(debug=True)
