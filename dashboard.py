import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc, Input, Output, State

# Creating a Dash application here
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Define the layout of the app., note: it is being used like HTML (little different)
# Feel free to change the layout/colors/fonts, this was just to test the code
app.layout = dbc.Container(fluid=True, children=[
    html.H1('IoT Dashboard', style={'font-family': 'Courier New'}, className='text-center text-primary mb-4'),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H3('Switch to Control LED', style={'font-family': 'Courier New'}),
                daq.BooleanSwitch(id='toggle-switch', on=False, style={'transform': 'scale(2)'}),
                html.Div(id='switch-status', className='text-center text-white', style={'font-family': 'Courier New', 'margin-top': '20px'}),
                html.Div(id='led-status', className='text-center text-white', style={'font-family': 'Courier New', 'margin-top': '20px'})
            ], className='p-3 bg-dark text-white')
        ], width=12)
    ])
])

# Defining a callback to update switch status and the LED visual rep. on the dashboard
# Code is a bit incomplete as it is not attached to the LED right now and is missing the code for the LED itself
@app.callback(
    [Output('switch-status', 'children'),
     Output('toggle-switch', 'on')],
    [Input('toggle-switch', 'on')]
)
def update_switch_and_led_status(on):
    switch_status = 'ON' if on else 'OFF'
    # The BooleanSwitch 'on' property is already bound to the switch status, so it will represent the LED status.
    # Here we need to add code to communicate with the Raspberry Pi to actually turn the LED on or off.
    return f'LED is {switch_status}', on

# Running 
if __name__ == '__main__':
    app.run_server(debug=True)
