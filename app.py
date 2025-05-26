from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from datetime import datetime, timedelta
import random
import os
import json
import gspread
from google.oauth2 import service_account
import base64
from googleapiclient.discovery import build


# Define scopes required for Sheets API access (READ ONLY)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Decode base64 credentials and initialize Google service credentials
try:
    creds_b64 = os.environ.get('GOOGLE_CREDENTIALS_B64')
    print(f"✅ GOOGLE_CREDENTIALS_B64 present? {creds_b64 is not None}")
    if not creds_b64:
        raise Exception("Missing GOOGLE_CREDENTIALS_B64 environment variable")
    
    creds_json = base64.b64decode(creds_b64).decode('utf-8')
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    print("✅ Google credentials loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load credentials: {e}")
    creds = None


app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management


# Simulated weather data from Google Sheets
def get_weather_data():
    try:
        client = gspread.authorize(creds)

        # Open the sheet
        sheet = client.open("filtered sensor data").sheet1

        # Debug logs
        print("✅ Connected to Google Sheet.")

        temperature = float(sheet.acell('B1').value)
        humidity = float(sheet.acell('C1').value)
        pressure = float(sheet.acell('E1').value)
        hindex = float(sheet.acell('D1').value)
        datetime_val = sheet.acell('A1').value

        print(f"📊 Read data: {temperature}°C, {humidity}%, {pressure} hPa")

        return {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
            'hindex': hindex,
            'datetime': datetime_val,
            'unit': 'celsius'
        }

    except Exception as e:
        print("❌ Error fetching from Google Sheets:", e)
        return {
            'temperature': 0,
            'humidity': 0,
            'pressure': 0,
            'hindex': 0,
            'datetime': 'N/A',
            'unit': 'celsius'
        }


def get_condition(temp, humidity, pressure):
    if pressure < 1005 and humidity > 75:
        return 'rain'
    elif pressure < 1000 and humidity > 80:
        return 'thunderstorm'
    elif pressure > 1015 and humidity < 50:
        return 'sunny'
    elif humidity > 85:
        return 'cloudy'
    else:
        return 'partly-cloudy'

def get_forecast(current_temp, humidity, pressure):
    times = ['6:00 AM', '9:00 AM', '12:00 PM', '3:00 PM', '6:00 PM', '9:00 PM']
    temps = [
        current_temp - 1,
        current_temp + 1,
        current_temp + 4,
        current_temp + 2,
        current_temp,
        current_temp - 1
    ]
    condition = get_condition(current_temp, humidity, pressure)

    return [{
        'time': time,
        'temperature': round(temp, 1),
        'condition': condition
    } for time, temp in zip(times, temps)]

def get_weekly_forecast():
    try:
        # Get current sensor values
        weather_data = get_weather_data()
        base_temp = weather_data['temperature']
        humidity = weather_data['humidity']
        pressure = weather_data['pressure']
    except:
        # Fallback in case live data fails
        base_temp = 28
        humidity = 75
        pressure = 1010

    now = datetime.now()
    forecast = []

    for i in range(7):
        day = 'Today' if i == 0 else (now + timedelta(days=i)).strftime('%A')
        date = (now + timedelta(days=i)).strftime('%b %d')

        # Generate highs and lows based on base temp with variation
        high = round(base_temp + random.uniform(1, 3), 1)
        low = round(base_temp - random.uniform(1.5, 3), 1)

        # Use your get_condition logic to simulate a weekly condition
        simulated_temp = base_temp + random.uniform(-2, 2)
        condition = get_condition(simulated_temp, humidity, pressure)

        forecast.append({
            'day': day,
            'date': date,
            'low': low,
            'high': high,
            'condition': condition
        })

    return forecast


def generate_sensor_data(parameter):
    now = datetime.now()
    dates = [(now - timedelta(days=6-i)).strftime('%B %d, %Y') for i in range(7)]

    if parameter == 'temperature':
        base, variation, unit = 25, 8, '°C'
    elif parameter == 'humidity':
        base, variation, unit = 80, 20, '%'
    else:
        base, variation, unit = 1013, 25, 'hPa'

    values = []
    for _ in range(7):
        values.extend([round(base + random.uniform(-variation, variation), 1) for _ in range(24)])

    return {
        'labels': dates,
        'values': values,
        'parameter': f'{parameter.title()} ({unit})'
    }

USERS = {"admin": "password123"}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    weather_data = get_weather_data()
    current_temp = weather_data['temperature']
    humidity = weather_data['humidity']
    pressure = weather_data['pressure']

    forecast = get_forecast(current_temp, humidity, pressure)
    weekly = get_weekly_forecast()

    return render_template('index.html',
                           weather=weather_data,
                           forecast=forecast,
                           weekly=weekly,
                           logged_in='username' in session)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    current_date = datetime.now().strftime('%b %d, %Y')

    am_forecast = [{'time': f'{i:02}:00', 'condition': 'partly-cloudy-sun', 'temp': '25'} for i in range(0, 12)]
    pm_forecast = [{'time': f'{i:02}:00', 'condition': 'partly-cloudy', 'temp': str(33 - i % 5)} for i in range(12, 24)]

    now = datetime.now()
    weekly_forecast = [{
        'day': 'Today' if i == 0 else (now + timedelta(days=i)).strftime('%A'),
        'date': (now + timedelta(days=i)).strftime('%b %d'),
        'condition': 'partly-cloudy',
        'low': '25',
        'high': '31'
    } for i in range(7)]

    return render_template('dashboard.html',
                           current_date=current_date,
                           am_forecast=am_forecast,
                           pm_forecast=pm_forecast,
                           weekly_forecast=weekly_forecast)

@app.route('/sensor')
def sensor():
    return render_template('sensor.html', logged_in='username' in session)

@app.route('/api/sensor-data/<parameter>')
def sensor_data(parameter):
    return jsonify(generate_sensor_data(parameter))

@app.route('/api/weather')
def get_weather():
    return jsonify(get_weather_data())

@app.route('/request')
def request_page():
    return render_template('request.html', logged_in='username' in session)

@app.route('/api/submit-request', methods=['POST'])
def submit_request():
    data = request.json
    print("Received request:", data)
    return jsonify({"status": "success"})

@app.route('/login')
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in USERS and USERS[username] == password:
        session['username'] = username
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))

    weather_data = get_weather_data()
    forecast = get_forecast(weather_data['temperature'], weather_data['humidity'], weather_data['pressure'])
    weekly = get_weekly_forecast()

    return render_template('admin.html',
                           weather=weather_data,
                           forecast=forecast,
                           weekly=weekly,
                           logged_in=True)

# Sensor pages
@app.route('/air-temperature')
def air_temperature():
    if 'username' not in session:
        return redirect(url_for('login'))

    sensors = [
        {'id': 1, 'name': 'Sensor A', 'location': 'Building 1'},
        {'id': 2, 'name': 'Sensor B', 'location': 'Building 2'},
        {'id': 3, 'name': 'Sensor C', 'location': 'Building 3'}
    ]
    current_sensor_id = request.args.get('sensor', '1')
    current_sensor = next((s for s in sensors if str(s['id']) == current_sensor_id), sensors[0])

    return render_template('air_temperature.html', sensors=sensors, current_sensor=current_sensor)

@app.route('/relative-humidity')
def relative_humidity():
    if 'username' not in session:
        return redirect(url_for('login'))

    sensors = [
        {'id': 1, 'name': 'Sensor A', 'location': 'Building 1'},
        {'id': 2, 'name': 'Sensor B', 'location': 'Building 2'},
        {'id': 3, 'name': 'Sensor C', 'location': 'Building 3'}
    ]
    current_sensor_id = request.args.get('sensor', '1')
    current_sensor = next((s for s in sensors if str(s['id']) == current_sensor_id), sensors[0])

    return render_template('relative_humidity.html', sensors=sensors, current_sensor=current_sensor)

@app.route('/barometric-pressure')
def barometric_pressure():
    if 'username' not in session:
        return redirect(url_for('login'))

    sensors = [
        {'id': 1, 'name': 'Sensor A', 'location': 'Building 1'},
        {'id': 2, 'name': 'Sensor B', 'location': 'Building 2'},
        {'id': 3, 'name': 'Sensor C', 'location': 'Building 3'}
    ]
    current_sensor_id = request.args.get('sensor', '1')
    current_sensor = next((s for s in sensors if str(s['id']) == current_sensor_id), sensors[0])

    return render_template('barometric_pressure.html', sensors=sensors, current_sensor=current_sensor)


@app.route('/test-sheets')
def test_sheets():
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId='1CxS4NrxiNc_XOSLd2850O1kSkdh_CFJGQov-Juu8hh4',
            range='Sheet1!A1:E1'
        ).execute()
        values = result.get('values', [])
        return jsonify(values)
    except Exception as e:
        return f"Error fetching from Google Sheets: {e}", 500



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)




