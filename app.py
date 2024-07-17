from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine, text, inspect

app = Flask(__name__)
engine=create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict', echo=True)

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
def get_model_data(): 
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
def get_model_data(): 
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
def show_maps():
    return render_template('visualize.html')

if __name__ == '__main__':
    app.run(debug=True)