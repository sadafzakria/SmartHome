import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc, Input, Output, State
import atexit
import RPi.GPIO as GPIO

# GPIO setup
GPIO.setwarnings(False)
LED_PIN = 17
GPIO.setmode(GPIO.BCM)  
GPIO.setup(LED_PIN, GPIO.OUT)

# Creating a Dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Layout of the app
app.layout = dbc.Container(fluid=True, children=[
    html.H1('IoT Dashboard', style={'font-family': 'Courier New'}, className='text-center text-primary mb-4'),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Phase 1", className="text-center text-white"),
                    html.H6("LED Status", className="text-center text-white mb-4"),
                    daq.BooleanSwitch(id='toggle-switch', on=False, style={'transform': 'scale(2)'}),
                    html.Div(id='switch-status', className='text-center text-white', style={'font-family': 'Courier New', 'margin-top': '20px'})
                ])
            ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '50%', 'margin': '0 auto'}), # Transparent white card, centered with width set
        ], width=12)
    ])
])

# Defining a callback to update switch status and control the LED on the Raspberry Pi
@app.callback(
    [Output('switch-status', 'children'),
     Output('toggle-switch', 'on')],
    [Input('toggle-switch', 'on')]
)
def update_switch_and_led_status(on):
    switch_status = 'ON' if on else 'OFF'
    GPIO.output(LED_PIN, on)  # Turn LED on/off based on the switch's state
    return f'LED is {switch_status}', on

# Clean up GPIO when the app closes
@app.server.before_first_request
def cleanup():
    @atexit.register
    def clean_gpio():
        GPIO.cleanup()

# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)
