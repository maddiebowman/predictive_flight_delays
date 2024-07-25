# Predictive Flight Delay Model & User Application

#### *Instructions*
1. Run **`python db_sample.py`** to unzip `full_data_flightdelays.csv.zip`, creating a database to store sampled
    Note: **`db.py`:** Creates database containing full dataset (current flask application utilizes the sample database)

3. Run **`python app.py`** to launch flask application, access predictive the flight delay dashboard and related visualizations

**`/notebooks`:** Jupyter lab notebooks containing data preprocessing, feature engineering, model training and analysis of feature selection.


**`/graveyard`:** Archived files


## Project Overview
### Outline 
Using historical flight and weather data, build a machine learning model that predicts future flight delays and cancellations. The model predictions are supported by an interactive user application that reports the probability of an input flight being delayed, based on a variety of features that have impacted historical delays. Supporting our predictive flight delay dashboard, are interactive visualizations that analyze the historical 2019 flight data to provide further visual summary. Following future improvements and model optimization, our application aims to provide more accurate estimates of departure and arrival times for passengers and airline operations. 

## Data Sources
**Main Dataset: [Kaggle - 2019 Airline Delays with Weather and Airport Detail](https://www.kaggle.com/datasets/threnjen/2019-airline-delays-and-cancellations)**

26 Columns - 1.37 GB

**Dataset Sourced:** 

***[Bureau of Transportation Statistics](https://www.transtats.bts.gov/databases.asp?Z1qr_VQ=E&Z1qr_Qr5p=N8vn6v10&f7owrp6_VQF=D)***
***[National Centers for Environmental Information (NOAA)](https://www.ncdc.noaa.gov/cdo-web/datasets)***


### Additional External Data Sources:

#### **Airports and Locations - JSON Data**

**[GitHub Gist - `airports.json`](https://gist.github.com/tdreyno/4278655)**


#### **API Connections for Real-Time Flight and Weather Data**

**[National Weather Service Government API](https://weather-gov.github.io/api/general-faqs)**


**[OpenWeather API](https://openweathermap.org/api)**

#### Target Variable
**Predicted Flight Delay:** `flight_delayed`
`0` = No Delay Predicted
`1` = Delay Over 15 Minutes Predicted
#### **Final Chosen Features**
Following the process of feature engineering the following were selected for training our model:
* Harsh Weather Conditions,including max wind speed, max temprature, precipation. 
* High-Delayed Airlines
* Day of Week
* Elements of Air Travel Congestion & Peak Traffic Times
* Month


## Installation
```python  
!pip install gdown
```

```python  
pip install imblearn
```
```python  
pip install xgboost
```
```python  
!pip install seaborn
```
```python  
!pip install shap
```

## Neural Network Model

### Model 1 - Baseline Model

- Two hidden layers with 64 neurons each
- Activation function: ReLU
- Output layer: Sigmoid activation
- Optimizer: Adam
- Loss function: Binary crossentropy

### Model 2 - Increased Number of Neurons

- Two hidden layers with 128 neurons each
- Activation function: ReLU
- Output layer: Sigmoid activation
- Optimizer: Adam
- Loss function: Binary crossentropy

### Model 3 - Added Hidden Layer

- Three hidden layers with 64 neurons each
- Activation function: ReLU
- Output layer: Sigmoid activation
- Optimizer: Adam
- Loss function: Binary crossentropy

### Feature Engineering
- Iterate Model 1 altering features based on scenarios
- Concluded Features: AWND, TMAX, DEP_TIME_BLK, DAY_OF_WEEK, PRCP, AIRLINE_AIRPORT_FLIGHTS_MONTH, AIRPORT_FLIGHTS_MONTH, AIRLINE_FLIGHTS_MONTH, MONTH

## Flask Application

Program created with postgres to establish a database. **`db.py`** includes all the data points, while **`db_sample.py`** has randomly selected sample data, *easier to run on less powerful machines.* **`app.py`** uses the full database if available, then will use the sample database as a backup if unavailable. Data is then queried from postgres database and returned as jsonified data or used as data routes for user application visuals.

### /predict endpoint
This endpoint helps predict the likelihood of flight delays based on various inputs provided by the user. The user enters flight details into an HTML form, and this data is processed and used to predict the probability of a delay.

Users enter flight details such as origin, destination, airline, and departure time into a form on the /predict endpoint. JavaScript processes this data and sends it to the server using an AJAX connection.

The server receives the input and extracts necessary details like airport names, flight dates, and times. It uses those inputs to gather live weather data from the openweathermaps and weather.gov APIs as well as monthly flight statistics from the database. These details are then prepared for prediction by encoding and scaling the data appropriately.

The processed data is fed into a machine learning model, which predicts the probability of a flight delay. This probability is then sent back to the web page and displayed to the user.

/predict: This endpoint handles both displaying the form (GET request) and processing the prediction (POST request). When a user submits the form, the server processes the input, queries additional data, and returns the delay probability.

Several helper functions are used to streamline data processing:

- split_airport_string: Extracts the name and code from an airport string.
- get_flight_data: Parses user input, extracts features, and gathers weather data.
- dataprep: Prepares the data for the machine learning model.
- query_monthly_stats: Queries the database for monthly flight statistics.
- get_dep_time_block: Determines the departure time block based on the hour.


## Project Summary & Analysis
*Available in: **`Presentation_SlideDeck.pdf`***

## Resources
#### Helpful Documentation
- [Seaborn - countplot](https://seaborn.pydata.org/generated/seaborn.countplot.html)
- [Seaborn - heatmap](https://seaborn.pydata.org/generated/seaborn.heatmap.html)
- [scikit-learn - Feature Importances with Forest of Trees](https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html)
- [statsmodels - User Guide](https://www.statsmodels.org/stable/user-guide.html)
- [SciPy - chi2_contingency](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)
- [mdn web docs - Element: innerHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML)
- [mdn web docs - JavaScript 'Map'](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
- [mdn web docs - EventTarget: addEventListener() method](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/)
- [mdn web docs -  CSS Performance Optimization](https://developer.mozilla.org/en-US/docs/Learn/Performance/CSS)
- [mdn web docs -  z-index](https://developer.mozilla.org/en-US/docs/Web/CSS/z-index)
- [Leaflet Plugins](https://leafletjs.com/plugins.html)

#### Additional Resources
- [CSS Beginner Tutorial](https://www.htmldog.com/guides/css/beginner/)
- [Favicon - Free Icon Library](https://icons8.com/icons)
- [Hoverable Sidenav Buttons - W3](https://www.w3schools.com/howto/howto_css_sidenav_buttons.asp)
- [CSS Styling a Navigation Bar](https://codetheweb.blog/style-a-navigation-bar-css/)
- [Displaying Live Images on HTML with Flask](https://stackoverflow.com/questions/46785507/python-flask-display-image-on-a-html-page)
- [JavaScript HTML DOM EventListener](https://www.w3schools.com/js/js_htmldom_eventlistener.asp)
- [HTML Forms](https://www.w3schools.com/html/html_forms.asp)
- [HTML id Attribute](https://www.w3schools.com/html/html_id.asp)
- [CSS ID Selectors - HTML Elements](https://blog.hubspot.com/website/css-id#:~:text=A%20CSS%20ID%20selector%20uses,to%20the%20element%20in%20brackets.)
- [How to Use id="" or class=""](https://forum.freecodecamp.org/t/how-to-know-when-to-use-id-or-class/506353)
- [innerHTML Style Tag](https://stackoverflow.com/questions/26890675/can-i-add-a-style-tag-to-innerhtml)


## Contributors
**[Maddie Bowman](https://github.com/maddiebowman)**

**[Jinlu Wang](https://github.com/moonsunkey)**

**[Belinda Ho](https://github.com/belindaho2828)**

**[Thomas Ngo](https://github.com/thomasjngo)**

**[Nelson Lin](https://github.com/birdforest)**

**[Meredith Jones](https://github.com/jonesmer)**
