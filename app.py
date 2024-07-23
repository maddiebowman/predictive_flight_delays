from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from weather_function import origin_fcstfn, precip_fn
from plane_function import aircraft_age
from flask_cors import CORS
import json
from datetime import date, datetime
import pandas as pd
import joblib

app = Flask(__name__)

# Function to check if a database exists
def database_exists(engine, database_name):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'"))
            return result.fetchone() is not None
    except OperationalError:
        return False

# Create an engine for the primary database
primary_engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)

# Check if the primary database exists and set the database_name accordingly
if database_exists(primary_engine, 'flightpredict'):
    database_name = 'flightpredict'
else:
    database_name = 'flightpredict_sample'

# Create the engine using the determined database name
engine = create_engine(f'postgresql://postgres:postgres@localhost:5432/{database_name}', echo=True)

CORS(app)

# Load the pre-trained model, scaler, and encoder
model = joblib.load("trained_modules_R/random_forest_model.pkl")
scaler = joblib.load("trained_modules_R/standard_scaler.pkl")
label_encoders = joblib.load("trained_modules_R/label_encoder.pkl")

# Returns the current local date
today = date.today()

# Setting up homepage that displays the API routes
@app.route("/")
def homepage():
    available_routes = [
        {"url": "/predict", "name": "Predict Flight Delays"},
        {"url": "/visuals", "name": "Visualizations"},
        {"url": "/data", "name": "View Data"}
    ]
    return render_template('index.html', available_routes=available_routes)

# Helper functions
def split_airport_string(airport_string):
    open_paren_pos = airport_string.find('(')
    close_paren_pos = airport_string.find(')')
    if open_paren_pos != -1 and close_paren_pos != -1:
        name = airport_string[:open_paren_pos].strip()
        code = airport_string[open_paren_pos + 1:close_paren_pos].strip()
        return name, code
    else:
        return None, None

def get_flight_data():
    response = request.get_data()
    decoded_string = response.decode('utf-8')
    try:
        data = json.loads(decoded_string)
    except json.JSONDecodeError as e:
        return jsonify({'error': 'Invalid JSON'}), 400

    o_airport_string = data['origin']
    d_airport_string = data['destination']
    carrier_name = data['airline']
    flight_date_time = data['departureTime']

    origin_airport, origination = split_airport_string(o_airport_string)
    destination_airport, dest_code = split_airport_string(d_airport_string)

    flight_date = datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').date()
    month = flight_date.month
    day_of_week = flight_date.weekday() + 1
    dep_time_blk = get_dep_time_block(datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').hour)

    precipitation_data = precip_fn(flight_date, origin_airport)
    prcp = precipitation_data['precipitation']

    forecast_data = origin_fcstfn(flight_date, origination)
    tmax = forecast_data['max_temp']
    awnd = forecast_data['max_wind_speed']

    input_dict = {
        'MONTH': month,
        'DAY_OF_WEEK': day_of_week,
        'TMAX': tmax,
        'AWND': awnd,
        'AIRPORT_FLIGHTS_MONTH': 0,  # Placeholder
        'AIRLINE_FLIGHTS_MONTH': 0,  # Placeholder
        'AIRLINE_AIRPORT_FLIGHTS_MONTH': 0,  # Placeholder
        'PRCP': prcp,
        'DEP_TIME_BLK': dep_time_blk,
        'origin_airport': origin_airport,
        'carrier_name': carrier_name
    }

    return input_dict

def dataprep(user_data):
    user_data_df = pd.DataFrame([user_data])
    for feature, le in label_encoders.items():
        user_data_df[feature] = le.transform(user_data_df[feature])
    user_data_df = user_data_df.drop(columns=['origin_airport', 'carrier_name'])  # Drop non-numeric columns
    user_data_scaled = scaler.transform(user_data_df)
    return user_data_scaled

def query_monthly_stats(origin_airport, month, carrier_name):
    origin_airport_words = ' '.join(origin_airport.split()[:2])
    airline_word = ' '.join(carrier_name.split()[:1])

    query_airport_flights = text('''
        SELECT AVG("AIRPORT_FLIGHTS_MONTH") as AIRPORT_FLIGHTS_MONTH
        FROM flight
        WHERE "DEPARTING_AIRPORT" LIKE :departing_airport AND "MONTH" = :month
    ''')

    query_airline_flights = text('''
        SELECT AVG("AIRLINE_FLIGHTS_MONTH") as AIRLINE_FLIGHTS_MONTH
        FROM flight
        WHERE "CARRIER_NAME" LIKE :carrier_name AND "MONTH" = :month
    ''')

    query_airline_airport_flights = text('''
        SELECT AVG("AIRLINE_AIRPORT_FLIGHTS_MONTH") as AIRLINE_AIRPORT_FLIGHTS_MONTH
        FROM flight
        WHERE "DEPARTING_AIRPORT" LIKE :departing_airport AND "CARRIER_NAME" LIKE :carrier_name AND "MONTH" = :month
    ''')

    conn = engine.connect()
    result_airport_flights = conn.execute(query_airport_flights, {'departing_airport': f'%{origin_airport_words}%', 'month': month}).fetchone()
    result_airline_flights = conn.execute(query_airline_flights, {'carrier_name': f'%{airline_word}%', 'month': month}).fetchone()
    result_airline_airport_flights = conn.execute(query_airline_airport_flights, {'departing_airport': f'%{origin_airport_words}%', 'carrier_name': f'%{airline_word}%', 'month': month}).fetchone()
    conn.close()

    return (
        result_airport_flights[0],
        result_airline_flights[0],
        result_airline_airport_flights[0]
    )

def get_dep_time_block(hour):
    if 0 <= hour < 6:
        return '0001-0559'
    elif 6 <= hour < 7:
        return '0600-0659'
    elif 7 <= hour < 8:
        return '0700-0759'
    elif 8 <= hour < 9:
        return '0800-0859'
    elif 9 <= hour < 10:
        return '0900-0959'
    elif 10 <= hour < 11:
        return '1000-1059'
    elif 11 <= hour < 12:
        return '1100-1159'
    elif 12 <= hour < 13:
        return '1200-1259'
    elif 13 <= hour < 14:
        return '1300-1359'
    elif 14 <= hour < 15:
        return '1400-1459'
    elif 15 <= hour < 16:
        return '1500-1559'
    elif 16 <= hour < 17:
        return '1600-1659'
    elif 17 <= hour < 18:
        return '1700-1759'
    elif 18 <= hour < 19:
        return '1800-1859'
    elif 19 <= hour < 20:
        return '1900-1959'
    elif 20 <= hour < 21:
        return '2000-2059'
    elif 21 <= hour < 22:
        return '2100-2159'
    elif 22 <= hour < 23:
        return '2200-2259'
    else:
        return '2300-2359'

@app.route('/predict', methods=['GET', 'POST'])
def get_flight_predict():
    if request.method == 'POST':
        flight_data = get_flight_data()
        origin_airport = flight_data['origin_airport']
        month = flight_data['MONTH']
        carrier_name = flight_data['carrier_name']

        airport_flights_month, airline_flights_month, airline_airport_flights_month = query_monthly_stats(origin_airport, month, carrier_name)

        flight_data['AIRPORT_FLIGHTS_MONTH'] = airport_flights_month
        flight_data['AIRLINE_FLIGHTS_MONTH'] = airline_flights_month
        flight_data['AIRLINE_AIRPORT_FLIGHTS_MONTH'] = airline_airport_flights_month

        prepped_data = dataprep(flight_data)
        prediction_result = model.predict_proba(prepped_data) * 100
        delay_percentage = prediction_result[0][1]  # Probability of class 1 (delay)
        result = f"The likelihood of flight delay is {delay_percentage:.2f}%"

        return jsonify({'result': result})

    else:
        return render_template('dashboard.html')

@app.route('/visuals')
def show_visuals():
    return render_template('visual.html')

@app.route('/data')
def get_data():
    query = text('''
               SELECT * 
               FROM flight
               ''')
    conn = engine.connect()
    results = conn.execute(query)
    conn.close()
    results = [tuple(row[1:]) for row in results]
    return jsonify(results)

@app.route('/chart/<int:offset>')
def geo_data(offset):
    offset = offset * 100000
    conn = psycopg2.connect(
        dbname=database_name,
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    with conn.cursor() as cur:
        query = '''
                SELECT "LATITUDE", "LONGITUDE", "DEP_DEL15", "CARRIER_NAME", "DEP_TIME_BLK", "DAY_OF_WEEK", "MONTH"
                FROM flight
                LIMIT 100000 
                OFFSET %s
                '''
        cur.execute(query, (offset,))
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]
    return jsonify(data_kv)

@app.route('/weather_stats')
def weather_stats():
    return render_template('weather_stats.html')

@app.route('/weather/<flight_date>/<origination>/')
def weather(flight_date, origination):
    try:
        flight_date_obj = datetime.strptime(flight_date, "%Y-%m-%d").date()
    except ValueError:
        return 'Invalid date format. Please use YYYY-MM-DD.', 400

    if flight_date_obj < today:
        return 'Date is in the past. Please enter a date within a 7-day range.', 400
    else:
        forecast_data = origin_fcstfn(flight_date, origination)
        return jsonify(forecast_data)

@app.route('/precip/flight_date/<origin_airport>/')
def precipitation(flight_date, origin_airport):
    try:
        flight_date_obj = datetime.strptime(flight_date, "%Y-%m-%d").date()
    except ValueError:
        return 'Invalid date format. Please use YYYY-MM-DD.', 400

    if flight_date_obj < today:
        return 'Date is in the past. Please enter a date within a 7-day range.', 400
    else:
        precipitation_data = precip_fn(flight_date, origin_airport)
        return jsonify(precipitation_data)

@app.route('/plane/<flight_date>/<flight_num>/')
def plane(flight_date, flight_num):
    plane_data = aircraft_age(flight_date, flight_num)
    return jsonify(plane_data)

if __name__ == '__main__':
    app.run(debug=True)
