# Predictive Flight Delay Model & User Application
After cloning the repository to local, navigate to `data` folder and click **`full_data_flightdelays.csv.zip`**, expanding the file to an accessible csv.
1. Open **`data_preprocessing.ipynb`** to clean and sample data, saving both as new csv files.

2. Run **`python db.py`** in terminal to create a database named `'flightpredict'` and store the preprocessed data into new collections.

3. Open **`flight_delay_predictions.ipynb`** to build predictive learning model and save h5 files.

4. Run **`app.py`** in terminal to launch the flask application, an interactive user dashboard that receives multiple inputs of user flight data, returning an output of **`YES`** or **`NO`** for a predicted flight delay and corresponding visualizations of the input flight and weather report. 



## Project Overview
### Outline 
Using historical flight and weather data, build a machine learning model that predicts future flight delays and cancellations. This model and the related visuals are supported by an interactive user application that reports the probability of a given flight being delayed or canceled, to provide more accurate estimates of departure and arrival times for passengers and airline operations. 

### Data
**Dataset: [Kaggle - 2019 Airline Delays with Weather and Airport Detail](https://www.kaggle.com/datasets/threnjen/2019-airline-delays-and-cancellations)**

26 Columns - 1.37 GB

**Dataset Sourced:** 
***[Bureau of Transportation Statistics](https://www.transtats.bts.gov/databases.asp?Z1qr_VQ=E&Z1qr_Qr5p=N8vn6v10&f7owrp6_VQF=D)***
***[National Centers for Environmental Information (NOAA)](https://www.ncdc.noaa.gov/cdo-web/datasets)***

#### Additional Data Used:

**List of US Airports and Location Details: City, State, Geolocation Coordinates, etc.**
**[Kaggle - Open Source List of US Airports](https://www.kaggle.com/datasets/aravindram11/list-of-us-airports)**

**API Connections for Real-Time Flight and Weather Data:**
**[API Layer - Aviation Stack API](https://apilayer.com/)**
**[FAA Government Aircraft API Data](https://apilayer.com/)**
**[OpenWeather API](https://openweathermap.org/)**

## Data Preprocessing
#### Feature Engineering
Explain process of predicting for a future flight delay; features changed and calculations required to return meaningful features to train our model.

#### Target Variable
**Predicted Flight Delay:** `flight_delayed`
`0` = No Delay Predicted
`1` = Delay Over 15 Minutes Predicted
#### **Features**
Following the process of feature engineering the following were selected for training our model:
* Harsh Weather Conditions
* High-Delayed Airlines
* Aircraft Age
* Air Travel Congestion & Peak Traffic Times
* Possibility of Prior Tail Segment Delays

## Compiling, Training, and Evaluating the Model
**Neural Network Structure**

**Model Optimization**

## Flask Application

## Project Summary & Analysis

## Resources
#### Helpful Documentation
- [Seaborn - countplot](https://seaborn.pydata.org/generated/seaborn.countplot.html)
- [Seaborn - heatmap](https://seaborn.pydata.org/generated/seaborn.heatmap.html)
- [scikit-learn - Feature Importances with Forest of Trees](https://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html)
- [statsmodels - User Guide](https://www.statsmodels.org/stable/user-guide.html)
- [SciPy - chi2_contingency](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)
- [mdn web docs - JavaScript 'Map'](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
- [mdn web docs - EventTarget: addEventListener() method](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/)
- [mdn web docs -  CSS Performance Optimization](https://developer.mozilla.org/en-US/docs/Learn/Performance/CSS)
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


## Contributors
**[Maddie Bowman](https://github.com/maddiebowman)**

**[Jinlu Wang](https://github.com/moonsunkey)**

**[Belinda Ho](https://github.com/belindaho2828)**

**[Thomas Ngo](https://github.com/thomasjngo)**

**[Nelson Lin](https://github.com/birdforest)**

**[Meredith Jones](https://github.com/jonesmer)**
