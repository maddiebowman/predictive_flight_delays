from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine, text, inspect
from weather_function import origin_fcstfn #importing function from separate file
from plane_function import aircraft_age
from flask_cors import CORS

app = Flask(__name__)
engine=create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict', echo=True)
CORS(app)

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

@app.route('/visualize')
def show_visuals():
    return render_template('visualize.html')

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

if __name__ == '__main__':
    app.run(debug=True)