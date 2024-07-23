#!pip install gdown

import psycopg2
from sqlalchemy import create_engine
import pandas as pd
import gdown
import zipfile
import os

# Database credentials
db_user = "postgres"
db_password = "postgres"
db_host = "localhost"
db_port = "5432"

# Function to create a database
def create_database(db_name):
    conn = psycopg2.connect(
        dbname="postgres",
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Create the database if it doesn't exist
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {db_name} WITH OWNER {db_user}")

    # Close the connection to the default database
    cursor.close()
    conn.close()

# Function to populate a database with data from a CSV file
def populate_database(db_name, csv_file, table_name):
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    conn = engine.connect()

    # Reading the CSV file
    df = pd.read_csv(csv_file)

    # Create schema and insert records
    df.to_sql(table_name, if_exists='replace', con=conn, index=False)

    # Close the connection
    conn.close()

# Function to unzip a file and return the path to the CSV file
def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.csv'):
                zip_ref.extract(file, extract_to)
                return os.path.join(extract_to, file)
    raise ValueError("No CSV file found in the ZIP archive")

# Create both databases
create_database("flightpredict")

# Unzip the CSV file and get the CSV file path
zip_file_path = 'data/full_data_flightdelay.csv.zip'
extract_to_path = 'data'
csv_file_path = unzip_file(zip_file_path, extract_to_path)

# Populate the first database
populate_database("flightpredict", csv_file_path, 'flight')