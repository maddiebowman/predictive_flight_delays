# Dependencies and Setup
# Dependencies and Setup
import pandas as pd
import numpy as np
import requests
import pprint
import json
import re
from api_key import openweather_api
from datetime import date, datetime

#define function for 7-day forecast for origin airport
def origin_fcstfn (flight_date, origination):
    
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
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
        daytime = origin_7dforecast['properties']['periods'][i]['isDaytime']
        if match and daytime == True:
            origin_tmax = origin_7dforecast['properties']['periods'][i]['temperature']


    #find max wind speed for origin airport
    
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
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
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
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

    #find detailed forecast for origin airport
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
        daytime = origin_7dforecast['properties']['periods'][i]['isDaytime']
        if match and daytime == True:
            day_forecast = origin_7dforecast['properties']['periods'][i]['detailedForecast']
        if match and daytime == False:
            night_forecast = origin_7dforecast['properties']['periods'][i]['detailedForecast']


    return {
        'max_temp': origin_tmax,
        'max_wind_speed': origin_awnd,
        'chance_of_precipitation': f'{origin_precip}%',
        'day_time_forecast': day_forecast,
        'night_time_forecast': night_forecast
    }



#origin function using airport file
#define function for 7-day forecast for origin airport
def origin_fcstfn_2 (flight_date, origination):

    #read in list of available airport names
    airport_name_url = 'https://gist.githubusercontent.com/tdreyno/4278655/raw/7b0762c09b519f40397e4c3e100b097d861f5588/airports.json'
    airport_name_source = requests.get(airport_name_url).json()

    #get lat long of airport from airport name input
    for i in range(len(airport_name_source)):
        name_of_airport = airport_name_source[i]['name']
        lat = airport_name_source[i]['lat']
        long = airport_name_source[i]['lon']
        if name_of_airport == origination:
            origin_lat = lat
            origin_long = long
    
    #get weather data. Source: https://weather-gov.github.io/api/general-faqs
    origin_url = f'https://api.weather.gov/points/{origin_lat},{origin_long}'

    #get 7-day forecast for origin
    origin_7dresponse = requests.get(origin_url).json()['properties']['forecast']
    origin_7dforecast = requests.get(origin_7dresponse).json()

    #find max temp for origin airport
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
        daytime = origin_7dforecast['properties']['periods'][i]['isDaytime']
        if match and daytime == True:
            origin_tmax = origin_7dforecast['properties']['periods'][i]['temperature']


    #find max wind speed for origin airport
    
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
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
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
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

    #find detailed forecast for origin airport
    for i in range(len(origin_7dforecast['properties']['periods'])):
        start_time = origin_7dforecast['properties']['periods'][i]['startTime']
        match = re.search(f'^{flight_date}', start_time)
        daytime = origin_7dforecast['properties']['periods'][i]['isDaytime']
        if match and daytime == True:
            day_forecast = origin_7dforecast['properties']['periods'][i]['detailedForecast']
        if match and daytime == False:
            night_forecast = origin_7dforecast['properties']['periods'][i]['detailedForecast']


    return {
        'max_temp': origin_tmax,
        'max_wind_speed': origin_awnd,
        'chance_of_precipitation': f'{origin_precip}%',
        'day time forecast': day_forecast,
        'night time forecast': night_forecast
    }

#precipitation function

def precip_fn(flight_date, origin_airport):

    #read in list of available airport names
    airport_name_url = 'https://gist.githubusercontent.com/tdreyno/4278655/raw/7b0762c09b519f40397e4c3e100b097d861f5588/airports.json'
    airport_name_source = requests.get(airport_name_url).json()

    #get lat long of airport from airport name input
    for i in range(len(airport_name_source)):
        name_of_airport = airport_name_source[i]['name']
        lat = airport_name_source[i]['lat']
        long = airport_name_source[i]['lon']
        if name_of_airport == origin_airport:
            o_lat = lat
            o_long = long
    
    #get weather data on openweather api
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={o_lat}&lon={o_long}&appid={openweather_api}'

    #get 7-day forecast for origin
    origin_owforecast = requests.get(url).json()

    #find precip
    precip_in = 0
    for i in range(len(origin_owforecast['list'])):
        weather_date = origin_owforecast['list'][i]['dt_txt']
        precip_prob = origin_owforecast['list'][i]['pop']
        match = re.search(f'^{flight_date}', weather_date)
        if match and precip_prob > 0:
            if 'rain' in origin_owforecast['list'][i]:
                precip_in = precip_in + origin_owforecast['list'][i]['rain']['3h']
        else:
            precip_in = precip_in + 0
    return {
        'precipitation': precip_in
    }



#define function for 7-day forecast for destination airport
#TBD w/ Maddine on whether we need this
# def destination_fcstfn (flight_date, destination):
    
#     destination = destination.upper()

#     #read in airport codes lat/long file. Source: https://github.com/ip2location/ip2location-iata-icao/blob/master/iata-icao.csv
#     airport_codes = pd.read_csv('data/airport_codes_.csv')
#     ac_df = pd.DataFrame(airport_codes)
    
#     #look up lat/long for airport codes
#     dest_lat = ac_df.loc[ac_df['iata'] == destination, ['latitude']].iloc[0,0]
#     dest_long = ac_df.loc[ac_df['iata'] == destination, ['longitude']].iloc[0,0]
    
#     #get weather data. Source: https://weather-gov.github.io/api/general-faqs
#     origin_url = f'https://api.weather.gov/points/{dest_lat},{dest_long}'

#     #get 7-day forecast for origin
#     destination_7dresponse = requests.get(destination_url).json()['properties']['forecast']
#     destination_7dforecast = requests.get(destination_7dresponse).json()

#     #find max temp for origin airport
#     for i in range(len(destination_7dforecast['properties']['periods'])):
#         start_time = destination_7dforecast['properties']['periods'][i]['startTime']
#         match = re.search(f'^{flight_date}', start_time)
#         daytime = destination_7dforecast['properties']['periods'][i]['isDaytime']
#         if match and daytime == True:
#             destination_tmax = destination_7dforecast['properties']['periods'][i]['temperature']


#     #find max wind speed for origin airport
    
#     for i in range(len(destination_7dforecast['properties']['periods'])):
#         start_time = destination_7dforecast['properties']['periods'][i]['startTime']
#         match = re.search(f'^{flight_date}', start_time)
#         daytime = destination_7dforecast['properties']['periods'][i]['isDaytime']
#         if match and daytime == True:
#             try:
#                 day_awnd = int(destination_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[2])
#             except:
#                 day_awnd = int(destination_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[0])
#         else:
#             try:
#                 night_awnd = int(destination_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[2])
#             except:
#                 night_awnd = int(destination_7dforecast['properties']['periods'][i]['windSpeed'].split(' ')[0])
#     destination_awnd = max(day_awnd, night_awnd)

#     #find chance of precipitation at origination airport
#     for i in range(len(destination_7dforecast['properties']['periods'])):
#         start_time = destination_7dforecast['properties']['periods'][i]['startTime']
#         match = re.search(f'^{flight_date}', start_time)
#         daytime = destination_7dforecast['properties']['periods'][i]['isDaytime']
#         if match and daytime == True:
#             day_precip = destination_7dforecast['properties']['periods'][i]['probabilityOfPrecipitation']['value']
#             if day_precip == None:
#                 day_precip = 0
#         else:
#             night_precip = destination_7dforecast['properties']['periods'][i]['probabilityOfPrecipitation']['value']
#             if night_precip == None:
#                 night_precip = 0
#     destination_precip = max(day_precip, night_precip)

#     #find detailed forecast for origin airport
#     for i in range(len(destination_7dforecast['properties']['periods'])):
#         start_time = destination_7dforecast['properties']['periods'][i]['startTime']
#         match = re.search(f'^{date}', start_time)
#         daytime = destination_7dforecast['properties']['periods'][i]['isDaytime']
#         if match and daytime == True:
#             day_forecast = destination_7dforecast['properties']['periods'][i]['detailedForecast']
#         if match and daytime == False:
#             night_forecast = destination_7dforecast['properties']['periods'][i]['detailedForecast']


#     return {
#         'max_temp': origin_tmax,
#         'max_wind_speed': origin_awnd,
#         'chance_of_precipitation': f'{origin_precip}%',
#         'day time forecast': day_forecast,
#         'night time forecast': night_forecast
#     }