from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine, text, inspect
from weather_function import origin_fcstfn, destination_fcstfn #importing function from separate file
from plane_function import aircraft_age
from flask_cors import CORS
from datetime import date, datetime

app = Flask(__name__)
engine=create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict', echo=True)
CORS(app)

today = date.today()

# Setting up homepage that displays the API routes
@app.route("/")
def homepage():
    """List all available API routes."""
    available_routes =  [
    ("/predict"),
    ("/data"),
    ("/visualize")
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

@app.route('/predict')
def get_flight_predict(): 
    query=text('''
               SELECT * 
               FROM [enter text]
               ''')
    conn=engine.connect()
    results=conn.execute(query)
    conn.close()
    results=[tuple(row[1:]) for row in results]
    return jsonify(results)

@app.route('/data')
def get_data(): 
    query=text('''
               SELECT * 
               FROM [enter text]
               ''')
    conn=engine.connect()
    results=conn.execute(query)
    conn.close()
    results=[tuple(row[1:]) for row in results]
    return jsonify(results)

#BH Test. determine which columns we need to query
#delay y/n, airport code, lat, long, airline

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
def show_visuals():
    return render_template('visualize.html')

#weather at origination
@app.route('/weather/<flight_date>/<origination>/')
# Returns the current local date


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


@app.route('/plane/<flight_date>/<flight_num>/')
def plane(flight_date, flight_num):
    #example date 2024-07-17; example flight_num wn658
    plane_data = aircraft_age(flight_date, flight_num)

    return jsonify(plane_data)

if __name__ == '__main__':
    app.run(debug=True)