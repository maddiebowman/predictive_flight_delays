#import dependencies 
import requests
import pprint
from splinter import Browser
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

#define function
def aircraft_age(flight_date, flight_num):
    from api_key import flight_api_key
    
    flight_num = flight_num.lower()

    #retrieve flight information
    
    flight_url = 'http://api.aviationstack.com/v1/flights'
    
    params = {
      'access_key': flight_api_key,
        'flight_iata': flight_num
    }
    
    api_result = requests.get(flight_url, params)
    
    api_response = api_result.json()

    # retrieve aircraft tail number if available: tail number is not assigned until pulling into destination gate

    for i in range(len(api_response['data'])):
        aircraft = api_response['data'][i]['aircraft']
        try:
            if aircraft == None:
                print("No aircraft assigned yet, will use previous day's aircraft for same flight as proxy")
            else:
                tail_num = aircraft['registration']
        except:
            tail_num = "No aircraft information available"

    # Set up the service and browser
    service = ChromeService(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service)
    
    #Visiting Website
    url = 'https://registry.faa.gov/aircraftinquiry/search/nnumberinquiry'
    browser.get(url)
    
    #entering the tail number
    tail_num_input = browser.find_element(By.NAME, 'NNumbertxt')
    tail_num_input.send_keys(tail_num)
    
    # Find and wait for the submit button to be clickable
    submit_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Submit')]"))
    )
    
    # Click the submit button using JavaScript to bypass potential issues
    browser.execute_script("arguments[0].click();", submit_button)

    # Wait for the results page to load
    browser.implicitly_wait(10)
    
    # Get the page source
    page_source = browser.page_source
    
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find the manufacture year using BeautifulSoup
    mfr_year_elements = soup.find_all('td', {'data-label': 'Mfr Year'})
    
    # Extract text from each element found
    mfr_years = [element.text.strip() for element in mfr_year_elements]
    
    # Close the browser
    browser.quit()
    
    #access mfr year as integer
    mfr_year = int(mfr_years[0])

    #extract year from flight_date input and convert to integer
    flight_year = datetime.strptime(flight_date, '%Y-%m-%d').year

    #calculate plane age
    plane_age = flight_year - mfr_year

    return {
        'registration/tail number': tail_num,
        "plane's manufactured year": mfr_year,
        'flight year': flight_year,
        'plane age based on flight flight_date': plane_age
    }