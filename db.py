from sqlalchemy import create_engine
import pandas as pd

engine=create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict')
conn=engine.connect()

# Reading first csv file for flights
flight_df=pd.read_csv('data/full_data_flightdelay.csv')
# creates schema and inserts records
flight_df.to_sql('flight', if_exists='replace', con=conn)

conn.close()