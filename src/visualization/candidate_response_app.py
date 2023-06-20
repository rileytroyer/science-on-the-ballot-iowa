import json

from dash import Dash, dcc, html, dash_table, ctx
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import numpy as np
import plotly.express as px
import pandas as pd

# Start App
app = Dash(__name__)

# Define styles
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Read in all json files
map_dir = 'data/processed/map-files/'
with open(map_dir + 'congress.json') as geofile:
    congress_map = json.load(geofile)
with open(map_dir + 'house.json') as geofile:
    house_map = json.load(geofile)
with open(map_dir + 'senate.json') as geofile:
    senate_map = json.load(geofile)
with open(map_dir + 'us-senate.json') as geofile:
    us_senate_map = json.load(geofile)
with open(map_dir + 'gov.json') as geofile:
    gov_map = json.load(geofile)
with open(map_dir + 'sec-ag.json') as geofile:
    sec_ag_map = json.load(geofile)
with open(map_dir + 'sec-state.json') as geofile:
    sec_state_map = json.load(geofile)

# Create dictionary to store and reference all maps
maps = {'United States Representative' : congress_map,
        'Iowa State Representative' : house_map,
        'Iowa State Senate' : senate_map,
        'Governor' : gov_map,
        'United States Senate': us_senate_map,
        'Secretary of Agriculture and Land Stewardship' : sec_ag_map,
        'Secretary of State' : sec_state_map}

# Read in response file
def parse_qualtrics(filepathname):
    # Read in excel file with Qualtrics responses
    qualtrics = pd.read_excel(filepathname)

    # Clean up the DataFrame
    # Drop unused columns
    drop_columns = ['StartDate', 'EndDate', 'Status', 'IPAddress',
                    'Progress', 'Duration (in seconds)', 'Finished',
                    'RecordedDate', 'ResponseId',
                    'RecipientLastName', 'RecipientFirstName',
                    'RecipientEmail', 'ExternalReference',
                    'LocationLatitude', 'LocationLongitude',
                    'DistributionChannel', 'UserLanguage',
                    'Q_RecaptchaScore']
    qualtrics = qualtrics.drop(columns=drop_columns)

    # Switch column label row
    qualtrics = qualtrics.rename(columns=qualtrics.iloc[0])
    qualtrics = qualtrics.drop(qualtrics.index[0])

    # Drop rows that are all NaN
    qualtrics = qualtrics.dropna(how='all')

    # Rename name and district number columns

    rename = {'What is your name?' : 'Name',
              'What office are you running for?' : 'Office',
              'What is your congressional district number?' : 'District'}
    qualtrics = qualtrics.rename(columns=rename)

    # Create a new column which is full name of race
    races = []

    for n, i in enumerate(qualtrics.index):

        office = qualtrics.loc[i, 'Office']
        district = qualtrics.loc[i, 'District']

        # If district doesn't apply done include in race
        if np.isnan(district):
            races.append(office)

        else:
            races.append(office + ' District ' + str(district))

    races = np.array(races)

    # Write to Dataframe
    qualtrics.loc[:, 'Race'] = races

    # Pivot dataframe based on questions and responses
    id_vars = ['Name', 'Office', 'District', 'Race']
    qualtrics = qualtrics.melt(id_vars = id_vars,
                               var_name = 'Questions',
                               value_name = 'Responses')

    return qualtrics

# Read in and drop rows with no responses
response_filename = 'data/raw/responses/responses-qualtrics-latest.xlsx'
qualtrics = parse_qualtrics(response_filename).dropna(subset='Responses')

# Create a dataframe for each race and store in dictionary
responses_by_race = {}

# Loop through each unique race
for race in qualtrics['Race'].unique():

    # Filter to just race
    qualtrics_race = qualtrics[qualtrics['Race'] == race]

    race_df = qualtrics_race.pivot(index='Questions',
                                   columns='Name',
                                   values='Responses').rename_axis(columns = None)

    responses_by_race[race] = race_df

# Read in file with candidate contact info
contact_filename = 'data/processed/candidate-information/candidate-contact.xlsx'
contact_df = pd.read_excel(contact_filename)

# Add in contact
contact_df['Contact'] =  contact_df['Email'] + ';\n' + contact_df['Phone']

# Create dataframe with data to help with plotting
names = []
values = []
for key in maps.keys():

    race_map = maps[key]
    name_list = [f['id'] for f in race_map['features']]
    names.extend(name_list)

    for name in name_list:

        if name not in responses_by_race.keys():
            values.extend([0])
            continue

        values.extend([len(responses_by_race[name].columns)])

mapping_df = pd.DataFrame({'Name' : names,
                   'Value' : values})

# Start of app layout
app.layout = html.Div(children=[

    # HTML element for dropdown to select race
    html.Div(children=[
        html.Label('Select a Race'),
        dcc.Dropdown(
            list(maps.keys()),
            'Iowa State Representative',
            id='race-selector',
            style={'font_family': 'Times New Roman'}
        )
    ], style= {'width':'80%'}),

    html.Div([
        dcc.Markdown('**Candidates in Your District**'),
        html.Pre(id='click-data2',
                 style={'font_family': 'Times New Roman'}),

        # Table for candidate contact info
        dash_table.DataTable(id='contact',
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'overflowY': 'scroll',
                    'overflowX': 'scroll',
                    'textAlign': 'left',
                    'vertical-align': 'top',
                    'border': '1px solid black',
                    'font_family': 'Times New Roman'
                },
                style_header={'textAlign': 'left',
                              'font_family': 'Times New Roman',
                              'font-weight': 'bold'}
        )

    ], style={'width':'80%', 'margin-bottom':'10px'}),

    # HTML element to hold information
    html.Div(className='row', children=[

        # HTML element to hold map
        html.Div(children=[

            dcc.Graph(id='map')

        ], style={'width':'80%'}),

    ], style={'display':'flex'}),

    # HTML element to hold table
    html.Div([
        dcc.Markdown('**Responses**',
                     style={'font_family': 'Times New Roman'}),
        html.Pre(id='click-data',
                 style={'font_family': 'Times New Roman'}),
        dash_table.DataTable(id='responses',
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'overflowY': 'scroll',
                    'overflowX': 'scroll',
                    'textAlign': 'left',
                    'vertical-align': 'top',
                    'border': '1px solid black',
                    'font_family': 'Times New Roman'
                },
                style_header={'textAlign': 'left',
                              'font_family': 'Times New Roman'},
                style_cell_conditional=[{
                        'if': {'column_id': 'Questions'},
                        'font-weight': 'bold'
                }]
        )

    ], style={'width':'100%'})
])

# Callback to update which race is clicked on
@app.callback(
    Output('click-data2', 'children'),
    Input('map', 'clickData'),
    Input('race-selector', 'value'))

def display_click_data(clickData, race_map_name):

    # Clear district if new race is selected
    if ctx.triggered_id == 'race-selector':
        return 'Please select a location on the map.'

    if clickData:
        return str(clickData['points'][0]['location'])

    return 'Please select a location on the map.'

# Callback to update contact info
@app.callback(
    [Output('contact', 'data'), Output('contact', 'columns')],
    Input('map', 'clickData'),
    Input('race-selector', 'value')
)
def update_contact(clickData, race_map_name):

    # Clear contact if new race is selected
    if ctx.triggered_id == 'race-selector':
        return [None, None]

    if clickData:
        race_contact_df = contact_df[contact_df['For the Office Of...']
                                                == str(clickData['points'][0]['location'])]

        race_contact_df = race_contact_df.loc[:, ['Ballot Name(s)', 'Party', 'Contact']]

        data=race_contact_df.to_dict('records')
        columns=[{'id': c, 'name': c} for c in race_contact_df.columns]

        return [data, columns]

    raise PreventUpdate

# Callback to update map based on race selected
@app.callback(
    Output('map', 'figure'),
    Input('race-selector', 'value'))

def update_map(race_map_name):
    # Create map figure
    fig = px.choropleth_mapbox(mapping_df, geojson=maps[race_map_name],
                        locations='Name',
                        mapbox_style='open-street-map',
                        zoom=5.5, center={'lat':41.8780, 'lon':-93.0977},
                        color='Value', color_continuous_scale="Agsunset",
                        range_color=(0, 3),
                        opacity=0.3)

    fig.update_traces(hoverinfo='none', hovertemplate=None)
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    fig.update_layout(margin={'r':0, 't':0, 'l':0, 'b':0})

    fig.update_layout(clickmode='event+select')

    fig.data[0].update(selected = dict(marker=dict(opacity=0.5)),
                       unselected=dict(marker=dict(opacity=0.3)))

    return fig

# Callback to update responses table based on map click
@app.callback(
    [Output('responses', 'data'), Output('responses', 'columns')],
    Input('map', 'clickData'),
    Input('race-selector', 'value')
)

def update_table(clickData, race_map_name):

    # Clear responses if new race is selected
    if ctx.triggered_id == 'race-selector':
        return [None, None]

    if clickData:
        try:
            race_df = responses_by_race[str(clickData['points'][0]['location'])].reset_index()
            data=race_df.to_dict('records')
            columns=[{'id': c, 'name': c} for c in race_df.columns]
        except:

            data = [{'Info': 'No candidates have filled out our survey for this district'}]
            columns=[{'id': 'Info', 'name': 'Info'}]

            return [data, columns]

        return [data, columns]

    raise PreventUpdate

# Callback to update which race is clicked on
@app.callback(
    Output('click-data', 'children'),
    Input('map', 'clickData'),
    Input('race-selector', 'value'))

def display_click_data(clickData, race_map_name):

    # Clear district if new race is selected
    if ctx.triggered_id == 'race-selector':
        return 'Please select a location on the map.'

    if clickData:
        return str(clickData['points'][0]['location'])

    return 'Please select a location on the map.'

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
