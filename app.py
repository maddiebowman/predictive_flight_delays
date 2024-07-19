from flask import Flask, render_template, jsonify, send_from_directory, url_for
from sqlalchemy import create_engine, text, inspect
from weather_function import origin_fcstfn #importing function from separate file
from plane_function import aircraft_age
from flask_cors import CORS
import os

app = Flask(__name__)
engine=create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict', echo=True)
CORS(app)

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

@app.route('/predict')
def get_flight_predict():
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

@app.route('/weather/<date>/<origination>/')
def weather(date, origination):

    #example date 2024-07-17; example origination LAX
    forecast_data = origin_fcstfn(date, origination)

    return jsonify(forecast_data)



@app.route('/plane/<date>/<flight_num>/')
def plane(date, flight_num):
    #example date 2024-07-17; example flight_num wn658
    plane_data = aircraft_age(date, flight_num)

    return jsonify(plane_data)

# Ensure images are connected to application through flask
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'images'), filename)

if __name__ == '__main__':
    app.run(debug=True)