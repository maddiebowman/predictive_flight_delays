from flask import Flask, render_template, jsonify, request, send_from_directory
from sqlalchemy import create_engine, text
from weather_function import origin_fcstfn, precip_fn
from plane_function import aircraft_age
from flask_cors import CORS
from datetime import date, datetime
from api_key import openweather_api
import os
import pandas as pd
import tensorflow as tf

app = Flask(__name__)
engine = create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict', echo=True)
CORS(app)

# Load the machine learning model from the H5 file
model = tf.keras.models.load_model('model.h5')

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

@app.route('/predict')
def get_prediction_user_input():
    return render_template('dashboard.html')

@app.route('/predictions', methods=['POST'])
def get_flight_predict():
    # Get data from form
    data = request.form

    # Extract individual data points from the form
    origin = data.get('origin')
    destination = data.get('destination')
    departure_time_str = data.get('departureTime')
    tmax = float(data.get('tmax'))
    awnd = float(data.get('awnd'))
    prcp = float(data.get('prcp'))
    
    # Convert departure time to datetime and extract features
    departure_time = datetime.strptime(departure_time_str, '%Y-%m-%dT%H:%M')
    month = departure_time.month
    day_of_week = departure_time.weekday() + 1  # Monday is 0 in Python, but 1 in our feature
    dep_time_blk = get_dep_time_block(departure_time.hour)
    
    # Query the database for monthly statistics
    airport_flights_month, airline_flights_month, airline_airport_flights_month = query_monthly_stats(origin, month)

    # Prepare features for prediction
    features = [
        month,
        day_of_week,
        dep_time_blk,
        tmax,
        awnd,
        prcp,
        airport_flights_month,
        airline_flights_month,
        airline_airport_flights_month
    ]

    # Convert to DataFrame
    feature_names = ['MONTH', 'DAY_OF_WEEK', 'DEP_TIME_BLK', 'TMAX', 'AWND', 'PRCP',
                     'AIRPORT_FLIGHTS_MONTH', 'AIRLINE_FLIGHTS_MONTH', 'AIRLINE_AIRPORT_FLIGHTS_MONTH']
    features_df = pd.DataFrame([features], columns=feature_names)

    # Make prediction
    prediction = model.predict(features_df)

    # Get the output
    output = 'Yes' if prediction[0] == 1 else 'No'

    return render_template('dashboard.html', prediction_text=f'Will the flight be delayed? {output}')

def get_dep_time_block(hour):
    if 0 <= hour < 6:
        return '0001-0559'
    elif 6 <= hour < 12:
        return '0600-1159'
    elif 12 <= hour < 18:
        return '1200-1759'
    else:
        return '1800-2359'

def query_monthly_stats(departing_airport, month, carrier_name):
    # Query for AIRPORT_FLIGHTS_MONTH
    query_airport_flights = text('''
        SELECT 
            AVG("AIRPORT_FLIGHTS_MONTH") as AIRPORT_FLIGHTS_MONTH
        FROM flight
        WHERE 
            "DEPARTING_AIRPORT" = :departing_airport AND
            "MONTH" = :month
    ''')
    
    # Query for AIRLINE_FLIGHTS_MONTH
    query_airline_flights = text('''
        SELECT 
            AVG("AIRLINE_FLIGHTS_MONTH") as AIRLINE_FLIGHTS_MONTH
        FROM flight
        WHERE 
            "CARRIER_NAME" = :carrier_name AND
            "MONTH" = :month
    ''')
    
    # Query for AIRLINE_AIRPORT_FLIGHTS_MONTH
    query_airline_airport_flights = text('''
        SELECT 
            AVG("AIRLINE_AIRPORT_FLIGHTS_MONTH") as AIRLINE_AIRPORT_FLIGHTS_MONTH
        FROM flight
        WHERE 
            "DEPARTING_AIRPORT" = :departing_airport AND
            "CARRIER_NAME" = :carrier_name AND
            "MONTH" = :month
    ''')
    
    conn = engine.connect()
    
    # Execute queries
    result_airport_flights = conn.execute(query_airport_flights, departing_airport=departing_airport, month=month).fetchone()
    result_airline_flights = conn.execute(query_airline_flights, carrier_name=carrier_name, month=month).fetchone()
    result_airline_airport_flights = conn.execute(query_airline_airport_flights, departing_airport=departing_airport, carrier_name=carrier_name, month=month).fetchone()
    
    conn.close()

    return (
        result_airport_flights['AIRPORT_FLIGHTS_MONTH'], 
        result_airline_flights['AIRLINE_FLIGHTS_MONTH'], 
        result_airline_airport_flights['AIRLINE_AIRPORT_FLIGHTS_MONTH']
    )

@app.route('/unique_airline_flights_month')
def get_unique_airline_flights_month():
    # Example parameters for testing
    departing_airport = 'Orange County'
    month = 1
    carrier_name = 'American Airlines Inc.'

    airport_flights_month, airline_flights_month, airline_airport_flights_month = query_monthly_stats(departing_airport, month, carrier_name)
    
    result = {
        "AIRPORT_FLIGHTS_MONTH": airport_flights_month,
        "AIRLINE_FLIGHTS_MONTH": airline_flights_month,
        "AIRLINE_AIRPORT_FLIGHTS_MONTH": airline_airport_flights_month
    }
    return jsonify(result)


@app.route('/visuals')
def show_visuals():
    return render_template('visual.html')

@app.route('/data')
def get_data():
    query = text('SELECT * FROM flight')
    conn = engine.connect()
    results = conn.execute(query)
    conn.close()
    results = [tuple(row[1:]) for row in results]
    return jsonify(results)

@app.route('/data_test/<int:offset>')
def geo_data(offset):
    offset = offset * 100000
    conn = psycopg2.connect(
        dbname="flightpredict",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    with conn.cursor() as cur:
        query = '''
            SELECT "DEP_DEL15", "CARRIER_NAME", "PLANE_AGE", "DEPARTING_AIRPORT", "LATITUDE", "LONGITUDE"
            FROM flights
            LIMIT 100000 
            OFFSET %s
        '''
        cur.execute(query, (offset,))
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]
    return jsonify(data_kv)

@app.route('/visualize')
def show_visuals_2():
    return render_template('visualize.html')

@app.route('/weather/<flight_date>/<origination>/')
def weather(flight_date, origination):
    try:
        flight_date_obj = datetime.strptime(flight_date, "%Y-%m-%d").date()
    except ValueError:
        return 'Invalid date format. Please use YYYY-MM-DD.', 400

    if (flight_date_obj < today):
        return 'Date is in the past. Please enter a date within a 7-day range.', 400
    else:
        forecast_data = origin_fcstfn(flight_date, origination)
        return jsonify(forecast_data)

@app.route('/precip/<flight_date>/<origin_airport>/')
def precipitation(flight_date, origin_airport):
    try:
        flight_date_obj = datetime.strptime(flight_date, "%Y-%m-%d").date()
    except ValueError:
        return 'Invalid date format. Please use YYYY-MM-DD.', 400

    if (flight_date_obj < today):
        return 'Date is in the past. Please enter a date within a 7-day range.', 400
    else:
        precipitation_data = precip_fn(flight_date, origin_airport)
        return jsonify(precipitation_data)

@app.route('/plane/<flight_date>/<flight_num>/')
def plane(flight_date, flight_num):
    plane_data = aircraft_age(flight_date, flight_num)
    return jsonify(plane_data)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'images'), filename)

if __name__ == '__main__':
    app.run(debug=True)
