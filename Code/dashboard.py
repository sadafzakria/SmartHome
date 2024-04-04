import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc, Input, Output
import RPi.GPIO as GPIO
from Freenove_DHT import DHT  # Import the DHT class from Freenove_DHT module
import yagmail  # Import yagmail for sending emails
import imaplib
import email
from email.header import decode_header
import datetime

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BCM mode
LED_PIN = 20
DHT_PIN = 17  # Pin connected to DHT11 sensor
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(DHT_PIN, GPIO.OUT)  # Set up DHT11 pin as output

# Initialize yagmail SMTP connection
yag = yagmail.SMTP('szakria03@gmail.com', 'eniwgbsodjybyoae')

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
                    #date time here
                    html.H1(datetime.datetime.now().strftime("%H:%M"), className='text-center text-white mb-4', style={'font-family': 'Courier New'}),
                    html.H3(datetime.datetime.now().strftime("%A"), className='text-center text-white mb-0', style={'font-family': 'Courier New'}),
                    html.H3(datetime.datetime.now().strftime("%B %d, %Y"), className='text-center text-white mt-0', style={'font-family': 'Courier New'}),
                ])
            ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New', 'margin-bottom': '20px'}),

            dbc.Card([
                dbc.CardBody([
                    html.H2("LED Status", className="text-center text-white mb-4"),
                    html.Div([
                        html.Img(id='led-image', src='/assets/light_off.png', style={'width': '50px', 'height': '50px'}),
                        daq.BooleanSwitch(id='toggle-switch', on=False, style={'transform': 'scale(2)', 'margin-top': '40px', 'margin-bottom': '20px'}),
                        html.Div(id='switch-status', className='text-center text-white', style={'font-family': 'Courier New', 'margin-top': '20px'}),
                    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
                ]),
                dbc.CardBody([
                    html.H2("______________________", className="text-center text-white mb-4"),
                    html.Div([
                        html.Div(id='line', className='text-center text-white', style={'font-family': 'Courier New', 'margin-top': '20px'}),
                    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
                ]),
                dbc.CardBody([
                    html.H2("Fan Status", className="text-center text-white mb-4"),
                    html.Div([
                        html.Img(id='fan-image', src='/assets/fan_off.jpg', style={'width': '100px', 'height': '100px'}),
                        html.Div(id='fan-status', className='text-center text-white', style={'font-family': 'Courier New', 'margin-top': '20px'}),
                    ],style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
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
                                color={"gradient": True, "ranges": {"blue": [0, 25], "purple": [25, 35], "pink": [35, 40]}},
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
                                color={"gradient": True, "ranges": {"blue": [0, 60], "purple": [60, 80], "pink": [80, 100]}},
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
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Div(id='names', children="2024- Sadaf Zakria & Amirezza Saeidi", className='text-center text-white', style={'font-family': 'Courier New'}),
            ], width=12)
        ], style={'position': 'fixed', 'bottom': '0', 'width': '100%', 'padding': '10px', 'background-color': '#333333'})
    ]),  # Fan status display

    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
])

# Initialize email_sent variable
email_sent = False

# Send email
def send_email(subject, body, to_email):
    try:
        yag.send(to=to_email, subject=subject, contents=body)
        print("Email sent successfully!")
        email_sent = True
    except Exception as e:
        print("Failed to send email:", str(e))

# Check for email response and control fan accordingly
fan_turned_on = False
fan_status = 'Fan is off'

# Check for email response and control fan accordingly
def check_email_response(email_address, password):
    global fan_turned_on
    global email_sent

    # Stop checking email if fan is turned on
    if fan_turned_on and email_sent:
        return "Fan is on"

    imap_server = 'imap.gmail.com'  # Change this to your email provider's IMAP server

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_address, password)
    mail.select('inbox')  # Select the mailbox you want to access

    # Search for unseen emails in the inbox
    status, data = mail.search(None, 'UNSEEN')
    if status == 'OK':
        email_ids = data[0].split()
        if email_ids:  # Check if there are unseen emails
            latest_email_id = email_ids[-1]  # Get the ID of the most recent unseen email
            status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
            if status == 'OK':
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        content = get_email_content(msg)
                        if "yes turn on" in content.lower() and fan_turned_on:
                            mail.store(latest_email_id, '+FLAGS', '\Seen')  # Mark the email as read
                            print("Fan is on!")
                            fan_turned_on = True
                            return "Fan is on"  # Return fan status
                        elif "yes turn on" in content.lower() and not fan_turned_on:
                            mail.store(latest_email_id, '+FLAGS', '\Seen')  # Mark the email as read
                            fan_turned_on = True
                            print("Fan is on!")
                            return "Fan is on"  # Return fan status
                        else:
                            mail.store(latest_email_id, '+FLAGS', '\Seen')  # Mark the email as read
                            return "Fan is off"  # Return fan status
        #else:
            #print("No unseen emails found")
    else:
        print("Failed to search for unseen emails")

    mail.logout()


def get_email_content(msg):
    # Extract content from email
    content = ''
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                payload = part.get_payload(decode=True)
                try:
                    content += payload.decode('utf-8')
                except UnicodeDecodeError:
                    # If decoding with utf-8 fails, try decoding with latin-1
                    content += payload.decode('latin-1')
    else:
        payload = msg.get_payload(decode=True)
        try:
            content += payload.decode('utf-8')
        except UnicodeDecodeError:
            # If decoding with utf-8 fails, try decoding with latin-1
            content += payload.decode('latin-1')
    return content


# Callback to update temperature and humidity readings
@app.callback(
    [Output('temperature-gauge', 'value'),
     Output('humidity-gauge', 'value')],
    [Input('interval-component', 'n_intervals')]
)
def update_data(n):
    global email_sent  # Access the global email_sent variable
    # Create DHT object
    dht = DHT(DHT_PIN)
    # Read temperature and humidity from DHT11 sensor
    chk = dht.readDHT11()
    if chk == dht.DHTLIB_OK:
        # Check if temperature exceeds 24 degrees and email has not been sent
        if dht.temperature > 24 and not email_sent:
            # Send email notification
            email_subject = "Temperature Alert"
            email_body = f"The current temperature is {dht.temperature}°C. Would you like to turn on the fan?"
            send_email(email_subject, email_body, "zakriasadaf9@gmail.com")
            email_sent = True  # Set email_sent flag to True
        elif dht.temperature <= 24:
            email_sent = False  # Reset email_sent flag if temperature falls below 24 degrees
        return dht.temperature, dht.humidity
    else:
        # Return default values in case of error
        return 20, 50  # Default temperature and humidity values

# Callback to update switch status and control the LED
@app.callback(
    [Output('switch-status', 'children'),
     Output('led-image', 'src')],
    [Input('toggle-switch', 'on')]
)
def update_switch_and_led_status(on):
    switch_status = 'ON' if on else 'OFF'
    img_src = "/assets/light_on.png" if on else "/assets/light_off.png"
    GPIO.output(LED_PIN, on)  # Turn LED on/off based on the switch's state
    return f'LED is {switch_status}', img_src

# Callback to update fan status
@app.callback(
    [Output('fan-status', 'children'),
     Output('fan-image', 'src')],
    [Input('interval-component', 'n_intervals')]
)
def update_fan_status(n):
    global fan_status
    new_fan_status = check_email_response("szakria03@gmail.com", "eniwgbsodjybyoae")
    if new_fan_status is not None:
        fan_status = new_fan_status
    img_src = "/assets/fan_on1.gif" if fan_status.lower() == "fan is on" else "/assets/fan_off.jpg"
    return fan_status, img_src

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
