from flask import Flask, render_template, jsonify, send_from_directory, url_for, request
from sqlalchemy import create_engine, text, inspect
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


app = Flask(__name__)
engine=create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict_sample', echo=True)
CORS(app)


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

@app.route('/predict', methods = ['GET', 'POST'])
def get_flight_predict():
    
    if request.method == 'POST':
        response = request.get_data()
        decoded_string = response.decode('utf-8')

        # #Parse the JSON string into a Python dictionary
        #example: {'origin': 'Air Force Plant Nr 42 Palmdale (PMD)', 'destination': 'Akron Canton Regional Airport (CAK)', 'airline': 'Delta', 'departureTime': '2024-07-24T00:08'}
        data = json.loads(decoded_string)

        #getting airport
        o_airport_string = data['origin']
        d_airport_string = data['destination']
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
            
        # get origin
        origin_airport, origination  = split_airport_string(o_airport_string)
        # get destination
        departing_airport, depart_code = split_airport_string(d_airport_string)

        #get flight_date and convert departure time to datetime and extract features
        flight_date_time = data['departureTime']
        flight_date = datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').date()
        month = flight_date.month
        day_of_week = flight_date.weekday() + 1 # Monday is 0 in Python, but 1 in our feature
        dep_time_blk = get_dep_time_block(datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').hour)

        #get airline
        carrier_name = data['airline']

        #get precipitation
        #example: {'precipitation': 0}
        precipitation_data = precip_fn(flight_date, origin_airport)
        prcp = precipitation_data['precipitation']

        #get tmax, awnd, and % precipitation
        #example: {'max_temp': 107, 'max_wind_speed': 20, 'chance_of_precipitation': '0%', 'day_time_forecast': 'Sunny, with a high near 107.', 'night_time_forecast': 'Mostly clear, with a low around 77.'}
        forecast_data = origin_fcstfn(flight_date, origination)
        tmax = forecast_data['max_temp']
        awnd = forecast_data['max_wind_speed']

        #check resulting variables by printing
        results_dict = {'origin_airport': origin_airport,
                        'origination': origination,
                        'departing_airport': departing_airport,
                        'flight_date': flight_date,
                        'month': month,
                        'day_of_week': day_of_week,
                        'dep_time_blk': dep_time_blk,
                        'carrier_name': carrier_name,
                        'prcp': prcp,
                        'tmax': tmax,
                        'awnd': awnd
                        }
        print(results_dict)
        return render_template('dashboard.html', result = results_dict)
    else: 
        return render_template('dashboard.html')

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
    

# @app.route('/features')
# def show_features():


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

# @app.route('/data_test/<int:offset>')
# def geo_data(offset):
#     offset = offset * 100000
#     conn = psycopg2.connect(
#         dbname="flightpredict",
#         user="postgres",
#         password="postgres",
#         host="localhost",
#         port="5432"
#     )
#     with conn.cursor() as cur:
#         query = '''
#                 SELECT "DEP_DEL15", "CARRIER_NAME", "PLANE_AGE", "DEPARTING_AIRPORT", "LATITUDE", "LONGITUDE"
#                 FROM flight
#                 LIMIT 100000 
#                 OFFSET %s
#                 '''
#         cur.execute(query, (offset,))
#         data = cur.fetchall()
#         columns = [desc[0] for desc in cur.description]
#         data_kv = [dict(zip(columns, row)) for row in data]
#     return jsonify(data_kv)

@app.route('/test/<int:offset>')
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


@app.route('/plane/<flight_date>/<flight_num>/')
def plane(flight_date, flight_num):
    #example date 2024-07-17; example flight_num wn658
    plane_data = aircraft_age(flight_date, flight_num)

    return jsonify(plane_data)

if __name__ == '__main__':
    app.run(debug=True)