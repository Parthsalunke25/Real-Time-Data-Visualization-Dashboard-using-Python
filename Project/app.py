import dash
# Importing some tools from Dash to help build layout and connect data.
from dash import html, dcc
from dash.dependencies import Output, Input
import requests #weather info from the internet.
from datetime import datetime #latest d&t
import dash_bootstrap_components as dbc #nice and clean

API_KEY = 'c25971dcf2f54aefa66131535252404'  
CITY = 'Mumbai'  

# Main Shuruuuuu
metaTags = [{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]  # fit on phones.
app = dash.Dash(__name__, meta_tags=metaTags, external_stylesheets=[dbc.themes.BOOTSTRAP])  #set theme.
server = app.server  # needed for internet

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f0f2f5', 'padding': '20px'}, children=[

#updating speed
    dcc.Interval(id='update_interval', interval=15* 1000, n_intervals=0),

#Board ka top
    html.Div([
        html.H1("Real Time Weather Dashboard", style={'textAlign': 'center', 'color': '#003366'}),
        html.H4("Sensor Location:", style={'textAlign': 'center'}),
        html.H3("Mumbai, India", style={'textAlign': 'center', 'color': '#007bff'}),
        dbc.Spinner(html.H4(id='last_update', style={'textAlign': 'center', 'color': '#0d47a1'})),  # Shows last update time
    ], style={
        'backgroundColor': '#d4edda',
        'padding': '30px',
        'borderRadius': '16px',
        'marginBottom': '30px',
        'width': '100%',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'
    }),

    #Box interface
    html.Div([
        html.Div(id='temp', className='metric-card'),  
        html.Div(id='hum', className='metric-card'),  
        html.Div(id='wind', className='metric-card'),  
        html.Div(id='uv', className='metric-card'),  
     #college    
        html.Div([
            html.A(
                html.Img(src=app.get_asset_url('college.png'), style={'width': '70px', 'height': '70px'}),  # College logo
                href='https://slrtce.in/',  # Link to college website
                target='_blank'
            )
        ], className='metric-card'),

    ], style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'flexWrap': 'wrap',
        'gap': '20px',
        'marginBottom': '30px'
    }),

#change graph tab info
    html.Div([
        dcc.Tabs(id='weather_tabs', value='temp_tab', children=[
            dcc.Tab(label='Temperature Chart', value='temp_tab'),
            dcc.Tab(label='Humidity Chart', value='hum_tab'),
            dcc.Tab(label='Wind Speed Chart', value='wind_tab'),
            dcc.Tab(label='UV Index Chart', value='uv_tab')
        ]),
        html.Div(id='tab_content')  # selected graph
    ], style={'backgroundColor': '#ffffff', 'borderRadius': '12px', 'padding': '10px'})
])

# API upadte every time
@app.callback(Output('last_update', 'children'), Input('update_interval', 'n_intervals'))
def update_time(n):
    response = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}')
    last_updated = response.json()['current']['last_updated']
    return f"Last Updated: {last_updated}"

# updates tem
@app.callback(Output('temp', 'children'), Input('update_interval', 'n_intervals'))
def update_temp(n):
    temp_c = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}').json()['current']['temp_c']
    return [
        html.Img(src=app.get_asset_url('t.png'), style={'width': '40px', 'marginBottom': '10px'}),
        html.H3(f"{temp_c:.1f}"),  # Show temp
        html.P("Temperature"),
        html.P("\u00b0C", style={'fontSize': '12px', 'color': 'gray'})  
    ]

# updates hum
@app.callback(Output('hum', 'children'), Input('update_interval', 'n_intervals'))
def update_humidity(n):
    humidity = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}').json()['current']['humidity']
    return [
        html.Img(src=app.get_asset_url('humidity.png'), style={'width': '40px', 'marginBottom': '10px'}),
        html.H3(f"{humidity:.1f}"),
        html.P("Humidity"),
        html.P("%", style={'fontSize': '12px', 'color': 'gray'})
    ]

# updates wind speed
@app.callback(Output('wind', 'children'), Input('update_interval', 'n_intervals'))
def update_wind(n):
    wind_kph = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}').json()['current']['wind_kph']
    return [
        html.Img(src=app.get_asset_url('wind.png'), style={'width': '40px', 'marginBottom': '10px'}),
        html.H3(f"{wind_kph:.1f}"),
        html.P("Wind Speed"),
        html.P("kph", style={'fontSize': '12px', 'color': 'gray'})
    ]

# updates UV index
@app.callback(Output('uv', 'children'), Input('update_interval', 'n_intervals'))
def update_uv(n):
    uv_index = requests.get(f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}').json()['current']['uv']
    return [
        html.Img(src=app.get_asset_url('uv.png'), style={'width': '40px', 'marginBottom': '10px'}),
        html.H3(f"{uv_index:.1f}"),
        html.P("UV Index")
    ]

#update chart
@app.callback(
    Output('tab_content', 'children'),
    Input('weather_tabs', 'value'),
    Input('update_interval', 'n_intervals')
)
def update_graph(tab, n):
    try:
        # Get past 24-hour weather data
        response = requests.get(f'http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={CITY}&dt={datetime.now().strftime("%Y-%m-%d")}')
        data = response.json()
        forecast_day = data.get('forecast', {}).get('forecastday', [])

        if not forecast_day:
            return html.Div("No historical data available. Please check your API plan or try again later.", style={'color': 'red', 'textAlign': 'center'})

        # Collect hourly data
        hourly_data = forecast_day[0]['hour']
        times = [entry['time'] for entry in hourly_data]
        temps = [entry['temp_c'] for entry in hourly_data]
        hums = [entry['humidity'] for entry in hourly_data]
        winds = [entry['wind_kph'] for entry in hourly_data]
        uvs = [entry['uv'] for entry in hourly_data]

        # Decide data to saw graph
        if tab == 'temp_tab':
            ydata, label, color = temps, 'Temperature (\u00b0C)', 'red'
        elif tab == 'hum_tab':
            ydata, label, color = hums, 'Humidity (%)', 'blue'
        elif tab == 'wind_tab':
            ydata, label, color = winds, 'Wind Speed (kph)', 'green'
        else:
            ydata, label, color = uvs, 'UV Index', 'orange'

        # Make the graph
        fig = {
            'data': [{
                'x': times,
                'y': ydata,
                'type': 'line',
                'mode': 'lines+markers',
                'marker': {'color': color},
                'name': label
            }],
            'layout': {
                'title': {'text': f'{label} Over Past 24 Hours', 'x': 0.5},
                'xaxis': {'title': 'Time'},
                'yaxis': {'title': label},
                'plot_bgcolor': '#f9f9f9',
                'paper_bgcolor': '#f9f9f9'
            }
        }
        return dcc.Graph(figure=fig)

    except Exception as e:
        return html.Div(f"Error fetching data: {str(e)}", style={'color': 'red', 'textAlign': 'center'})

# Executed....................!!!
if __name__ == '__main__':
    app.run_server(debug=True)  #start with link
