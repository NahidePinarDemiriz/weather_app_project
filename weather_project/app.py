from flask import Flask, render_template # Flask: a web framework for Python
from flask_socketio import SocketIO # SocketIO: a library for handling WebSocket connections
import requests  # requests: to make HTTP requests
from flask_apscheduler import APScheduler # to schedule jobs inside your Flask application
import json # for handling JSON data

app = Flask(__name__) # initializes the Flask application
socketio = SocketIO(app)
app.config['SECRET_KEY'] = "secret" # sets a secret key
scheduler = APScheduler()
API_KEY = "b97bbd67792caf7332388f75f169cb51"
city = ''
@app.route('/') # sets the default route by which the user can access the web app
def index():
    return render_template('index.html')

@socketio.on('set_city')  # listens for a 'get_weather' event from the client and triggers the get_weather()
def get_weather(data): # receives a 'get_weather' event from the client and emits a 'weather_data' event with the weather information back to the client
    global city
    city = data['city']


@scheduler.task('interval', id='get_weather_data', seconds=2)  # defines function get_weather_data scheduled to run at an interval of 2 seconds (seconds=2)
def get_weather_data(): 
    if city == '':
        return

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    location = get_lat_lon(city) # retrieves latitude and longitude coordinates for a given city
    params = {
        "lat": location['lat'],
        "lon": location['lon'],
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params, verify=True)
    if response.status_code == 200:
        parsedData = response.json()
        data = parsedData
        result = {"temp" : data['main']['temp'], "humidity": data['main']['humidity'], "name" : data['name']}
        socketio.emit('weather_data', result)
    else:
        return None

def get_lat_lon(city): # for fetching latitude and longitude coordinates for a given city by making an API request to OpenWeatherMap's Geo API
    API_KEY = "b97bbd67792caf7332388f75f169cb51"
    geo_base_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city,
        "appid": API_KEY,
    }
    response = requests.get(geo_base_url, params=params, verify=True)
    if response.status_code == 200:
        data = response.json()
        loc = {"lat": data[0]['lat'], "lon": data[0]['lon']}
        return loc
    else:
        return None

@socketio.on('message') # listens for a 'message' event from the client
def handle_message(data):  # handles incoming 'message' events from the client by printing the message
    print('received message: ' + data)

@socketio.on('connect')  # listens for a connection event from the client
def test_connect(auth): # sends a 'my response' event back to the client upon connection
    socketio.emit('my response', {'data': 'Connected'})

@socketio.on('disconnect') # listens for a disconnection event from the client
def test_disconnect(): # prints a message when a client disconnects
    print('Client disconnected')


if __name__ == '__main__': # starts the Flask application on port 8080
    scheduler.init_app(app)
    scheduler.start()
    app.run(port=8080, debug=True)
    socketio.run(app, port=8080, debug=True)