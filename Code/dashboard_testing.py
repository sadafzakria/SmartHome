import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc, Input, Output
import plotly.graph_objs as go
import random
#import RPi.GPIO as GPIO

# GPIO setup
#GPIO.setwarnings(False)
#LED_PIN = 17
#GPIO.setmode(GPIO.BCM)  
#GPIO.setup(LED_PIN, GPIO.OUT)

# Simulating temperature and humidity data
def generate_data():
    temperature = random.uniform(20, 30)  # Random temperature between 20 and 30 Celsius
    humidity = random.uniform(40, 60)     # Random humidity between 40% and 60%
    return temperature, humidity

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Define layout of the dashboard
app.layout = dbc.Container(fluid=True, children=[
    html.H1("IoT Dashboard", className='text-center text-primary mb-4'),

    dbc.Row([
        # LED Column
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H2("LED Status", className="text-center text-white mb-4"),
                    html.Div([
                        html.Img(id='led-image', src='/assets/light_off.png', style={'width': '50px', 'height': '50px'}),
                        daq.BooleanSwitch(id='toggle-switch', on=False, style={'transform': 'scale(2)', 'margin-top': '20px'}),
                        html.Div(id='switch-status', className='text-center text-white', style={'font-family': 'Courier New', 'margin-top': '20px'}),
                    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
                ])
            ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New'}),  # Adjusted width to fill the container
        ], width=6),

        # Temperature and Humidity Column
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        html.Div([
                            html.H2("Temperature", className="text-center text-white"),
                            daq.Gauge(
                                id='temperature-gauge',
                                max=40,
                                min=0,
                                value=20,
                                showCurrentValue=True,
                                units="°C",
                                color={"gradient":True,"ranges":{"green":[0,25],"yellow":[25,35],"red":[35,40]}},
                                label='Temperature',
                                labelPosition='bottom',
                                size=200
                            ),
                        ], className='six columns'),
                        html.Div([
                            html.H2("Humidity", className="text-center text-white"),
                            daq.Gauge(
                                id='humidity-gauge',
                                max=100,
                                min=0,
                                value=50,
                                showCurrentValue=True,
                                units="%",
                                color={"gradient":True,"ranges":{"green":[0,60],"yellow":[60,80],"red":[80,100]}},
                                label='Humidity',
                                labelPosition='bottom',
                                size=200
                            ),
                        ], className='six columns'),
                    ]),
                ])
            ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New'}),
        ], width=6),
    ]),
    
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
])

# Callback to update data, gauges, and fan status
@app.callback(
    [Output('temperature-gauge', 'value'),
     Output('humidity-gauge', 'value')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    temperature, humidity = generate_data()
    return temperature, humidity

# Callback to update switch status and control the LED
@app.callback(
    [Output('switch-status', 'children'),
     Output('led-image', 'src')],
    [Input('toggle-switch', 'on')]
)
def update_switch_and_led_status(on):
    switch_status = 'ON' if on else 'OFF'
    img_src = "/assets/light_on.png" if on else "/assets/light_off.png"
    #GPIO.output(LED_PIN, on)  # Turn LED on/off based on the switch's state
    return f'LED is {switch_status}', img_src

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
