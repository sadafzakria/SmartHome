import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc
from Freenove_DHT import DHT  # Import the DHT class from Freenove_DHT module
import yagmail  # Import yagmail for sending emails
import imaplib
import email
from email.header import decode_header
import datetime
import RPi.GPIO as GPIO
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import paho.mqtt.client as mqtt
from dash_daq import Gauge


# MQTT setup
mqtt_server = "10.0.0.167"
# mqtt_topic = "light_intensity"
# client = mqtt.Client()

global current_light_intensity
current_light_intensity = 500

mqttc = mqtt.Client()
mqttc.connect(mqtt_server, 1883, 60)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    mqttc.subscribe("light_intensity")

def on_message(client, userdata, msg):
    global current_light_intensity
    current_light_intensity = msg.payload.decode()

mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.loop_start()

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Set GPIO mode to BCM mode
LED_PIN = 20
DHT_PIN = 17  # Pin connected to DHT11 sensor
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(DHT_PIN, GPIO.OUT)  # Set up DHT11 pin as outputz

# Initialize yagmail SMTP connection
yag = yagmail.SMTP('szakria03@gmail.com', 'eniwgbsodjybyoae')

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MORPH])

# Define layout of the dashboard
app.layout = dbc.Container(fluid=True, children=[
    html.H1("IoT Dashboard", className='text-center text-primary-emphasis mb-4'),

    dbc.Row([
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Date and Time
                    html.H1(datetime.datetime.now().strftime("%H:%M"), className='text-center text-secondary-emphasis mb-4', style={'font-family': 'Courier New'}),
                    html.H3(datetime.datetime.now().strftime("%A"), className='text-center text-secondary-emphasis mb-0', style={'font-family': 'Courier New'}),
                    html.H3(datetime.datetime.now().strftime("%B %d, %Y"), className='text-center text-secondary-emphasismt-0', style={'font-family': 'Courier New'}),
                ])
            ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New', 'margin-bottom': '20px'}),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            # LED Status and Light Intensity
                            html.H2("Light Status", className="text-center text-secondary-emphasis mb-4"),
                            html.Div([
                                html.Img(id='led-image', src='/assets/light_off.png', style={'width': '50px', 'height': '50px', 'margin-bottom': '10px'}),
                                daq.Slider(
                                    id='light-slider',
                                    min=0,
                                    max=1000,
                                    step=1,
                                    value=500,
                                    marks={0: '0', 400: '400', 800: '800', 1000: '1000'},
                                ),
                                html.Div(id='slider-tooltip', className='text-center text-secondary-emphasis', style={'margin-top': '25px'}),
                            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
                        ]),
                    ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New', 'margin-bottom': '20px', 'align-items': 'center'}),
                ], width=7),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H2("Fan Status", className="text-center text-secondary-emphasis mb-4"),
                            html.Div([
                                html.Img(id='fan-image', src='/assets/fan_off.jpg', style={'width': '100px', 'height': '100px'}),
                                html.Div(id='fan-status', className='text-center text-secondary-emphasis', style={'font-family': 'Courier New', 'margin-top': '20px'}),
                            ],style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
                        ])
                    ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New', 'margin-bottom': '20px'}),
                ], width=5),
            ])

            
        ], width=4),
        
        
        # dbc.Col([
        #     dbc.Card([
        #         dbc.CardBody([
        #             html.H2("Fan Status", className="text-center text-secondary-emphasis mb-4"),
        #             html.Div([
        #                 html.Img(id='fan-image', src='/assets/fan_off.jpg', style={'width': '100px', 'height': '100px'}),
        #                 html.Div(id='fan-status', className='text-center text-secondary-emphasis', style={'font-family': 'Courier New', 'margin-top': '20px'}),
        #             ],style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}),
        #         ])
        #     ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New', 'margin-bottom': '20px'}),
            
            
        # ], width = 4),
        # Temperature and Humidity Column 
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        html.Div([
                            html.H2("Temperature", className="text-center text-secondary-emphasis"),
                            daq.Gauge(
                                id='temperature-gauge',
                                showCurrentValue=True,
                                units="°C",
                                label='Temperature',
                                max=40,
                                min=0,
                                value=20,
                                size=200,
                                color="#00008B",
                            ),
                        ], className='six columns'),

                        html.Div([
                            html.H2("Humidity", className="text-center text-secondary-emphasis"),
                            daq.Gauge(
                                id='humidity-gauge',
                                showCurrentValue=True,
                                units="%",
                                label='Humidity',
                                max=100,
                                min=0,
                                value=50,
                                size=200,
                                color="#00008B",
                            ),
                        ], className='six columns'),
                    ]),
                ])
            ], style={'background-color': 'rgba(255, 255, 255, 0.2)', 'width': '100%', 'font-family': 'Courier New'}),
        ], width=4),
        
    ]),
    html.Div([
        dbc.Row([
            dbc.Col([
                # html.Div(id='light-intensity', className='text-center text-secondary-emphasis mb-4', style={'font-size': '24px'}),
                html.Div(id='names', children="2024- Sadaf Zakria & Amirezza Saeidi", className='text-center text-secondary-emphasis', style={'font-family': 'Courier New'}),
            ], width=12)
        ], style={'position': 'fixed', 'bottom': '0', 'width': '100%', 'padding': '10px', 'background-color': '#333333'})
    ]),  # Fan status display
    

    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
])

# Initialize email_sent + light_email_sent variable
email_sent = False
light_email_sent = False

# Send email
def send_email(subject, body, to_email):
    global email_sent  # Access the global email_sent variable
    try:
        yag.send(to=to_email, subject=subject, contents=body)
        print("Light email sent successfully!")
        if subject == "Temperature Alert":
            print("Temperature email sent successfully!")
            email_sent = True
        elif subject == "Led Update":
            print("Light email sent successfully!")
            light_email_sent = True
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

# @app.callback(
#    [Output('switch-status', 'children'),
#      Output('led-image', 'src')],
#     [Input('toggle-switch', 'on')],
#     allow_duplicate=True
# )
# def update_switch_and_led_status(on):
#     switch_status = 'ON' if on else 'OFF'
#     img_src = "/assets/light_on.png" if on else "/assets/light_off.png"
#     GPIO.output(LED_PIN, on)  # Turn LED on/off based on the switch's state
#     return f'LED is {switch_status}', img_src

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
# light intensity
@app.callback(
    [Output('light-slider', 'value'),
     Output('led-image', 'src')],
    [Input('interval-component', 'n_intervals')],
    prevent_initial_call=True,
    allow_duplicate=True
)
def update_thing(n_intervals):
    try:
        global light_email_sent
        light_intensity = float(current_light_intensity)
        print("Current light intensity:", light_intensity)  # Debug print statement
        if light_intensity < 400 and not light_email_sent:
            GPIO.output(LED_PIN, GPIO.HIGH)
            img_src = '/assets/light_on.png'
            currentTime = datetime.datetime.now().strftime("%H:%M:%S")
            body = f"The Light is On at {currentTime}"
            send_email(f"Led Update", body, "zakriasadaf9@gmail.com")
        elif light_intensity >= 400 and not light_email_sent:
            GPIO.output(LED_PIN, GPIO.LOW)
            img_src = '/assets/light_off.png'
            light_email_sent = True  # Set light_email_sent to True after deciding not to turn on the LED
        elif light_email_sent:
            GPIO.output(LED_PIN, GPIO.HIGH)
            img_src = '/assets/light_on.png'
        
        return [light_intensity, img_src]
    except ValueError:
        print("Invalid value for light intensity:", current_light_intensity)
        # Return a default value or handle the error accordingly
        return [0, '/assets/light_off.png']




# Callback to update slider tooltip
@app.callback(
    Output('slider-tooltip', 'children'),
    [Input('light-slider', 'value')]
)
def update_slider_tooltip(value):
    return f"Light Intensity: {value}"


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='10.0.0.167', port='5000')
