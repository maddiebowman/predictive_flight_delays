from sqlalchemy import create_engine
import pandas as pd
import gdown

engine=create_engine('postgresql://postgres:postgres@localhost:5432/flightpredict')
conn=engine.connect()

file_id = '1WClX4TtAVny-bz7AI1VNrqeGlnzyXiam'
url = f'https://drive.google.com/uc?id={file_id}'

output = 'sampled_data_full_nl.csv'
gdown.download(url, output, quiet=False)

# Reading first csv file for flights
flight_df=pd.read_csv(output)
# creates schema and inserts records
flight_df.to_sql('flight', if_exists='replace', con=conn)

conn.close()