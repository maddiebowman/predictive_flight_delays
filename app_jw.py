from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, text
from weather_function import origin_fcstfn, precip_fn  # Ensure these functions are defined
from plane_function import aircraft_age  # Ensure this function is defined
from flask_cors import CORS
from datetime import date, datetime
import pandas as pd
import joblib
import psycopg2

app = Flask(__name__)
engine = create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict', echo=True)
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
    available_routes = [
        {"url": "/predict", "name": "Predict Flight Delays"},
        {"url": "/visuals", "name": "Visualizations"},
        {"url": "/data", "name": "View Data"}
    ]
    return render_template('index.html', available_routes=available_routes)

@app.route('/predict', methods=['GET', 'POST'])
def get_flight_predict():
    if request.method == 'POST':
        response = request.get_data()
        decoded_string = response.decode('utf-8')

        try:
            data = json.loads(decoded_string)
        except json.JSONDecodeError as e:
            return jsonify({'error': 'Invalid JSON'}), 400

        # Extract data from parsed JSON
        o_airport_string = data['origin']
        d_airport_string = data['destination']
        carrier_name = data['airline']
        flight_date_time = data['departureTime']

        origin_airport, origination = split_airport_string(o_airport_string)
        destination_airport, dest_code = split_airport_string(d_airport_string)

        # Convert departure time to datetime and extract features
        flight_date = datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').date()
        month = flight_date.month
        day_of_week = flight_date.weekday() + 1
        dep_time_blk = get_dep_time_block(datetime.strptime(flight_date_time, '%Y-%m-%dT%H:%M').hour)

        # Get precipitation
        precipitation_data = precip_fn(flight_date, origin_airport)
        prcp = precipitation_data['precipitation']

        # Get tmax, awnd, and % precipitation
        forecast_data = origin_fcstfn(flight_date, origination)
        tmax = forecast_data['max_temp']
        awnd = forecast_data['max_wind_speed']

        # Get month data
        airport_flights_month, airline_flights_month, airline_airport_flights_month = query_monthly_stats(origin_airport, month, carrier_name)

        # Prepare the input data for prediction
        features = ['MONTH', 'DAY_OF_WEEK', 'TMAX', 'AWND', 'AIRPORT_FLIGHTS_MONTH',
                    'AIRLINE_FLIGHTS_MONTH', 'AIRLINE_AIRPORT_FLIGHTS_MONTH', 'PRCP', 'ENCODED_DEP_TIME_BLK']

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

        # Data preparation for prediction
        def dataprep(user_data):
            user_data["ENCODED_DEP_TIME_BLK"] = encoder.transform(user_data["ENCODED_DEP_TIME_BLK"])
            user_data = scaler.transform(user_data)
            return user_data

        prepped_data = dataprep(input_data)
        prediction_result = model.predict(prepped_data) * 100
        delay_percentage = prediction_result[0][0]  # Get the percentage value

        result = f"The likelihood of flight delay is {delay_percentage:.2f}%"
        
        return render_template('dashboard.html', template_result={"prediction": result})

    return render_template('dashboard.html')

# Helper functions
def split_airport_string(airport_string):
    open_paren_pos = airport_string.find('(')
    close_paren_pos = airport_string.find(')')
    if open_paren_pos != -1 and close_paren_pos != -1:
        name = airport_string[:open_paren_pos].strip()
        code = airport_string[open_paren_pos + 1:close_paren_pos].strip()
        return name, code
    return None, None

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
            FROM flight
            LIMIT 100000 
            OFFSET %s
        '''
        cur.execute(query, (offset,))
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        data_kv = [dict(zip(columns, row)) for row in data]
    return jsonify(data_kv)

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

@app.route('/precip/<flight_date>/<origin_airport>/')
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
