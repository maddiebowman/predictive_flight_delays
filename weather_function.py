# Dependencies and Setup
import pandas as pd
import numpy as np
import requests
import pprint
import json
import re

#define function for 7-day forecast for origin airport
def origin_fcstfn (date, origination):
    
    origination = origination.upper()

    #read in airport codes lat/long file. Source: https://github.com/ip2location/ip2location-iata-icao/blob/master/iata-icao.csv
    airport_codes = pd.read_csv('data/airport_codes_.csv')
    ac_df = pd.DataFrame(airport_codes)
    
    #look up lat/long for airport codes
    origin_lat = ac_df.loc[ac_df['iata'] == origination, ['latitude']].iloc[0,0]
    origin_long = ac_df.loc[ac_df['iata'] == origination, ['longitude']].iloc[0,0]
    
    #get weather data. Source: https://weather-gov.github.io/api/general-faqs
    origin_url = f'https://api.weather.gov/points/{origin_lat},{origin_long}'

    #get 7-day forecast for origin
    origin_7dresponse = requests.get(origin_url).json()['properties']['forecast']
    origin_7dforecast = requests.get(origin_7dresponse).json()

    #find max temp for origin airport
    # Initialize variables
    origin_tmax = 0

    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{date}', start_time)
        daytime = origin_7dforecast['properties']['periods'][i]['isDaytime']
        if match and daytime == True:
            origin_tmax = origin_7dforecast['properties']['periods'][i]['temperature']

    #find max wind speed for origin airport

    # Initialize variables
    day_awnd = night_awnd = 0

    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{date}', start_time)
        daytime = origin_7dforecast['properties']['periods'][i]['isDaytime']
        if match and daytime == True:
            try:
                day_awnd = int(origin_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[2])
            except:
                day_awnd = int(origin_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[0])
        else:
            try:
                night_awnd = int(origin_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[2])
            except:
                night_awnd = int(origin_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[0])
    origin_awnd = max(day_awnd, night_awnd)

    #find chance of precipitation at origination airport

    # Initialize variables
    day_precip = 0

    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{date}', start_time)
        daytime = origin_7dforecast['properties']['periods'][i]['isDaytime']
        if match and daytime == True:
            day_precip = origin_7dforecast['properties']['periods'][i]['probabilityOfPrecipitation']['value']
            if day_precip == None:
                day_precip = 0
        else:
            night_precip = origin_7dforecast['properties']['periods'][i]['probabilityOfPrecipitation']['value']
            if night_precip == None:
                night_precip = 0
    origin_precip = max(day_precip, night_precip)


    return {
        'max_temp': origin_tmax,
        'max_wind_speed': origin_awnd,
        'chance_of_precipitation': f'{origin_precip}%'
    }