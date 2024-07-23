from flask import Flask, render_template, jsonify, send_from_directory, url_for, request
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
from weather_function import origin_fcstfn, origin_fcstfn_2, precip_fn #importing function from separate file
from plane_function import aircraft_age
from flask_cors import CORS
import json
import re
from datetime import date, datetime
from api_key import openweather_api
import pandas as pd
import tensorflow as tf
import os
import psycopg2
import joblib
import pickle

app = Flask(__name__)

# Function to check if a database exists
def database_exists(engine, database_name):
    try:
        # Use a Connection to execute the query
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
model = joblib.load("trained_modules/tf_1.0.pkl")
scaler = joblib.load("trained_modules/standard_scaler.pkl")
encoder = joblib.load("trained_modules/label_encoder.pkl")

# Returns the current local date
today = date.today()

# Setting up homepage that displays the API routes
@app.route("/")
def homepage():
    """List all available API routes."""
    available_routes =  [
        {"url": "/predict", "name": "Predict Flight Delays"},
        {"url": "/visuals", "name": "Visualizations"},
        {"url": "/data", "name": "View Data"}
    ]

    return render_template('index.html', available_routes=available_routes)


# Kevin's notes below
    # # if POST
    # # run python function itself and return dictionary
    # #date = connect user input here
    # #origination = connect user input here
    # #weather_result = origin_fcstfn(date, origination)
    # request.form # get everything else
    # # data needs to look like this: 
    # # input=[X, X, X, X, X]
    # # combine all the input data
    # result=model.predict(input)
    # return render_template('index.html', available_routes=available_routes, result=result)
    # # if GET
    # return render_template('index.html', available_routes=available_routes)

    # step 1 - get data from form
    # step 2 - get data from DB
    # step 3 - combine data + preprocess data for ML
    # step 4 - model.predict(input)
    # return result

# helper functions
def split_airport_string(airport_string):
# Find the position of the opening parenthesis
    open_paren_pos = airport_string.find('(')
            
    # Find the position of the closing parenthesis
    close_paren_pos = airport_string.find(')')
            
    if open_paren_pos != -1 and close_paren_pos != -1:
        # Extract the name and code using slicing
        name = airport_string[:open_paren_pos].strip()
        code = airport_string[open_paren_pos + 1:close_paren_pos].strip()
        return name, code
    else:
        return None, None

def get_flight_data(): 
    response = request.get_data()
    decoded_string = response.decode('utf-8')

    # #Parse the JSON string into a Python dictionary
    #example: {'origin': 'Air Force Plant Nr 42 Palmdale (PMD)', 'destination': 'Akron Canton Regional Airport (CAK)', 'airline': 'Delta', 'departureTime': '2024-07-24T00:08'}
    try:
        data = json.loads(decoded_string)
    except json.JSONDecodeError as e:
        return jsonify({'error': 'Invalid JSON'}), 400
        
    #extract data from parsed JSON
    o_airport_string = data['origin']
    d_airport_string = data['destination']
    carrier_name = data['airline']
    flight_date_time = data['departureTime']

    # get origin
    origin_airport, origination  = split_airport_string(o_airport_string)
    # get destination
    destination_airport, dest_code = split_airport_string(d_airport_string)

    #convert departure time to datetime and extract features
    flight_date = datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').date()
    month = flight_date.month
    day_of_week = flight_date.weekday() + 1 # Monday is 0 in Python, but 1 in our feature
    dep_time_blk = get_dep_time_block(datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').hour)

    #get precipitation
    #example: {'precipitation': 0}
    precipitation_data = precip_fn(flight_date, origin_airport)
    prcp = precipitation_data['precipitation']

    #get tmax, awnd, and % precipitation
     #example: {'max_temp': 107, 'max_wind_speed': 20, 'chance_of_precipitation': '0%', 'day_time_forecast': 'Sunny, with a high near 107.', 'night_time_forecast': 'Mostly clear, with a low around 77.'}
    forecast_data = origin_fcstfn(flight_date, origination)
    tmax = forecast_data['max_temp']
    awnd = forecast_data['max_wind_speed']

    input_dict = {'origin_airport': origin_airport,
                    'origination': origination,
                    'destination_airport': destination_airport,
                    'flight_date': flight_date,
                    'month': month,
                    'day_of_week': day_of_week,
                    'dep_time_blk': dep_time_blk,
                    'carrier_name': carrier_name,
                    'prcp': prcp,
                    'tmax': tmax,
                    'awnd': awnd,
                        }

    return input_dict 

# Data preparation for prediction
def dataprep(user_data):
    user_data['ENCODED_DEP_TIME_BLK'] = encoder.transform(user_data['ENCODED_DEP_TIME_BLK'])
    user_data = scaler.transform(user_data)
    return user_data

#query database for monthly statistics
def query_monthly_stats(origin_airport, month, carrier_name):

    # Extract the first two words from the departing airport string
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
    result_airport_flights = conn.execute(query_airport_flights, {'departing_airport': f'%{origin_airport_words}%', 'month':month}).fetchone()
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
    
@app.route('/predict', methods = ['GET', 'POST'])
def get_flight_predict():
    
    if request.method == 'POST':
        #get input data from function
        flight_data = get_flight_data()
        origin_airport = flight_data['origin_airport']
        month = flight_data['month']
        carrier_name = flight_data['carrier_name']
        day_of_week = flight_data['day_of_week']
        tmax = flight_data['tmax']
        awnd = flight_data['awnd']
        prcp = flight_data['prcp']
        dep_time_blk = flight_data['dep_time_blk']

        #query monthly data from database
        airport_flights_month, airline_flights_month, airline_airport_flights_month = query_monthly_stats(origin_airport, month, carrier_name)


        # Prepare the input data for prediction
        features = ['MONTH', 'DAY_OF_WEEK', 'TMAX', 'AWND', 'AIRPORT_FLIGHTS_MONTH',
       'AIRLINE_FLIGHTS_MONTH', 'AIRLINE_AIRPORT_FLIGHTS_MONTH', 'PRCP',
       'ENCODED_DEP_TIME_BLK']

        input_data = pd.DataFrame([[
            month,
            day_of_week,
            tmax,
            awnd,
            airport_flights_month,
            airline_flights_month,
            airline_airport_flights_month,
            prcp,
            dep_time_blk
        ]], columns=features)


        prepped_data = dataprep(input_data)
        prediction_result = model.predict(prepped_data) * 100
        delay_percentage = prediction_result[0][0]  # Get the percentage value

        result = f"The likelihood of flight delay is {delay_percentage:.2f}%"

        return jsonify({'result': result})

    else: 
        return render_template('dashboard.html')
    


@app.route('/visuals')
def show_visuals():
    return render_template('visual.html')

@app.route('/data')
def get_data(): 
    query=text('''
               SELECT * 
               FROM flight
               ''')
    conn=engine.connect()
    results=conn.execute(query)
    conn.close()
    results=[tuple(row[1:]) for row in results]
    return jsonify(results)

#BH Test. determine which columns we need to query
#delay y/n, airport code, lat, long, airline


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
                SELECT "DEPARTING_AIRPORT", "LATITUDE", "LONGITUDE", 
                SUM("DEP_DEL15")::INTEGER AS TOT_DELAYS, 
                COUNT("DEP_DEL15") AS TOTAL_FLIGHTS, 
                ROUND(100 * (SUM("DEP_DEL15")::NUMERIC / COUNT("DEP_DEL15")::NUMERIC), 2)::FLOAT AS DELAY_RATE
                FROM flight
                GROUP BY "DEPARTING_AIRPORT", "LATITUDE", "LONGITUDE"
                LIMIT 100000 
                OFFSET %s
                '''
        cur.execute(query, (offset,))
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]
    return jsonify(data_kv)

@app.route('/chart/<int:offset>')
def chart_data(offset):
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
                SELECT "DAY_OF_WEEK", "DEP_TIME_BLK",
                SUM("DEP_DEL15")::INTEGER AS TOT_DELAYS, 
                COUNT("DEP_DEL15") AS TOTAL_FLIGHTS 
                FROM flight
                GROUP BY "DAY_OF_WEEK", "DEP_TIME_BLK"
                LIMIT 100000 
                OFFSET %s
                '''
        cur.execute(query, (offset,))
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]

    return jsonify(data_kv)
#endpoints for sql queries: 2019 delays per weather condition
@app.route('/2019_delay_tmax')
def hist_tmax_delays():
    conn = psycopg2.connect(
        dbname=database_name,
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    with conn.cursor() as cur:
        query = '''
    WITH total_counts AS (
        SELECT COUNT("DEP_DEL15") AS total
        FROM flight
    ),
    bucketed_data AS (
        SELECT 
            -- Bucket temperatures into 10-degree ranges
            CONCAT(
                CAST(FLOOR("TMAX" / 10) * 10 AS TEXT),
                '–',
                CAST(FLOOR("TMAX" / 10) * 10 + 10 AS TEXT)
            ) AS temperature_bucket,
            COUNT("DEP_DEL15") AS count_of_delays,
            ROUND((COUNT("DEP_DEL15")::numeric / (SELECT total FROM total_counts)) * 100, 2) AS percentage_of_total_delays
        FROM 
            flight
        GROUP BY 
            temperature_bucket
    )
    SELECT 
        temperature_bucket,
        SUM(count_of_delays) AS total_count_of_delays,
        SUM(percentage_of_total_delays) AS total_percentage_of_total_delays
    FROM 
        bucketed_data
    GROUP BY 
        temperature_bucket
    ORDER BY 
        MIN(CAST(SPLIT_PART(temperature_bucket, '–', 1) AS INTEGER));
        '''
        cur.execute(query)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]
    return jsonify(data_kv)

@app.route('/2019_delay_awnd')
def hist_awnd_delays():
    conn = psycopg2.connect(
        dbname=database_name,
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    with conn.cursor() as cur:
        query = ''' 
    SELECT 
        CONCAT(FLOOR("AWND" / 5) * 5, '–', FLOOR("AWND" / 5) * 5 + 5) AS wind_speed_bucket,
        COUNT("DEP_DEL15") AS count_of_delays,
        ROUND((COUNT("DEP_DEL15")::numeric / total_count.total) * 100, 2) AS percentage_of_total_delays
    FROM 
        flight
    CROSS JOIN 
        (SELECT COUNT("DEP_DEL15") AS total FROM flight) AS total_count
    GROUP BY 
        wind_speed_bucket, total_count.total
    ORDER BY 
        wind_speed_bucket;
        '''
        cur.execute(query)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]
    return jsonify(data_kv)

@app.route('/2019_delay_prcp')
def hist_prcp_delays():
    conn = psycopg2.connect(
        dbname=database_name,
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    with conn.cursor() as cur:
        query = '''
    SELECT 
        (FLOOR("PRCP" / 0.5) * 0.5) AS precipitation_bucket,
        COUNT("DEP_DEL15") AS count_of_delays,
        ROUND((COUNT("DEP_DEL15")::numeric / total_count.total) * 100, 2) AS percentage_of_total_delays
    FROM 
        flight
    CROSS JOIN 
        (SELECT COUNT("DEP_DEL15") AS total FROM flight) AS total_count
    GROUP BY 
        (FLOOR("PRCP" / 0.5) * 0.5), total_count.total
    ORDER BY 
        (FLOOR("PRCP" / 0.5) * 0.5);
        '''
        cur.execute(query)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]
    return jsonify(data_kv)

#weather stats historical visualizations - test only. Will incorporate into visuals later
@app.route('/weather_stats')
def weather_stats():
    return render_template('weather_stats.html')

#weather at origination
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

#precipitation at origination
@app.route('/precip/flight_date>/<origin_airport>/')
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

#live flight data endpoint - not currently in use
@app.route('/plane/<flight_date>/<flight_num>/')
def plane(flight_date, flight_num):
    #example date 2024-07-17; example flight_num wn658
    plane_data = aircraft_age(flight_date, flight_num)

    return jsonify(plane_data)

if __name__ == '__main__':
    app.run(debug=True)