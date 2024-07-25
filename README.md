# Predictive Flight Delay Model & User Application

#### *Instructions*
1. Run **`python db_sample.py`** in terminal to unzip `full_data_flightdelays.csv.zip` and create a new database that stores sampled data into new collections.

3. Run **`python app.py`** in terminal to launch the flask application with multiple routes and access the predictive delay dashboard.


#### Additional Files
**db.py:** Creates database containing full dataset

**/notebooks:** Jupyter lab notebooks containing data preprocessing, feature engineering, model training and analysis of feature selection.

**/trained_modules:** This folder contains the pkl files from NNW that we originally tested and built in flask.

**/trained_modules_R:** This folder contains the pkl files from Random Forest model that were used on the final version of the model.


## Project Overview
### Outline 
Using historical flight and weather data, build a machine learning model that predicts future flight delays and cancellations. This model and the related visuals are supported by an interactive user application that reports the probability of a given flight being delayed or canceled, to provide more accurate estimates of departure and arrival times for passengers and airline operations. 

### Data Sources
**Main Dataset: [Kaggle - 2019 Airline Delays with Weather and Airport Detail](https://www.kaggle.com/datasets/threnjen/2019-airline-delays-and-cancellations)**

26 Columns - 1.37 GB

**Dataset Sourced:** 

***[Bureau of Transportation Statistics](https://www.transtats.bts.gov/databases.asp?Z1qr_VQ=E&Z1qr_Qr5p=N8vn6v10&f7owrp6_VQF=D)***
***[National Centers for Environmental Information (NOAA)](https://www.ncdc.noaa.gov/cdo-web/datasets)***


#### Additional Data Used:

**Airports and Locations - JSON Data**
**[GitHub Gist - `airports.json`](https://gist.github.com/tdreyno/4278655)**

**API Connections for Real-Time Flight and Weather Data**
**[API - National Weather Service](https://weather-gov.github.io/api/general-faqs)**

## Data Preprocessing
#### Feature Engineering
Explain process of predicting for a future flight delay; features changed and calculations required to return meaningful features to train our model.

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

## Compiling, Training, and Evaluating the Model
**Neural Network Structure**

**Model Optimization**

## Flask Application

A program was created to establish a database with postgres. `db.py` includes all the data points while `db_sample.py` has a randomly selected sample which is easier to run on less powerful machines. `app.py` will use the full database if it is available, but will use the sample database as a backup if not. The data is then queried from the postgres database and returned as jsonified data or used for the various routes and visualizations on the website.

## Project Summary & Analysis

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
