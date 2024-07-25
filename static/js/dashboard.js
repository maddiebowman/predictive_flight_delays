document.addEventListener('DOMContentLoaded', () => {
  let myMap;

  function initializeMap() {
    if (!myMap) {
      myMap = L.map('map').setView([48, -109], 4);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(myMap);
    }
  }
  
  initializeMap();

  const airportUrl = 'https://gist.githubusercontent.com/tdreyno/4278655/raw/7b0762c09b519f40397e4c3e100b097d861f5588/airports.json';
  let airportData;

  fetch(airportUrl)
    .then(response => response.json())
    .then(data => {
      airportData = data.filter(airport => {
        return airport.country === 'United States' || airport.country === 'Puerto Rico';
      });
      airportData.sort((a, b) => {
        if (!a.name && !b.name) return 0;
        if (!a.name) return 1;
        if (!b.name) return -1;
        return a.name.localeCompare(b.name);
      });
      populateAirportDatalists();
    })
    .catch(error => console.error('Error fetching the airport data:', error));

  function populateAirportDatalists() {
    populateDatalist('origins', airportData);
    populateDatalist('destinations', airportData);
  }

  function populateDatalist(datalistId, items) {
    const datalist = document.getElementById(datalistId);
    if (datalist) {
        datalist.innerHTML = '';
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = `${item.name} (${item.code})`;
            datalist.appendChild(option);
        });
    } else {
        console.error(`Datalist with ID ${datalistId} not found`);
    }
}

  // Manually populate the airline dropdown
  const airlines = [
    'Alaska', 'Allegiant Air', 'American Airlines', 'American Eagle Airlines', 
    'Atlantic Southeast Airlines', 'Comair', 'Delta', 'Endeavor Air', 'Frontier', 
    'Hawaiian Airlines', 'JetBlue', 'Mesa Airlines', 'Midwest Airline', 
    'SkyWest Airlines', 'Southwest', 'Spirit', 'United'
  ];

  const airlineDatalist = document.getElementById('airlines');
  airlines.forEach(airline => {
    const option = document.createElement('option');
    option.value = airline;
    airlineDatalist.appendChild(option);
  });

  function createPopupContent(airport, forecastData) {
    return `
      <div class="popup-content">
        <div class="airport-name">${airport.name}</div>
        <div class="airport-location">${airport.city}, ${airport.state}</div>
        <hr color="black" size="1">
        <div class="weather-container">
          <h4>Weather Forecast</h4>
          <div class="daily-forecast-container">
            <div class="icon-label-container">
              <img src="/static/images/day_icon.png" alt="Day Icon" class="forecast-icon">
              <span class="daily-forecast-label">Daily Forecast</span>
            </div>
            <div id="daily-forecast-${airport.code}" class="weather-forecast hidden">
              ${forecastData.day_time_forecast}
            </div>
          </div>
          <div class="nightly-forecast-container">
            <div class="icon-label-container">
              <img src="/static/images/night_icon.png" alt="Night Icon" class="forecast-icon">
              <span class="nightly-forecast-label">Nightly Forecast</span>
            </div>
            <div id="nightly-forecast-${airport.code}" class="weather-forecast hidden">
              ${forecastData.night_time_forecast}
            </div>
          </div>
          <button class="toggle-button" data-target="weather-details-${airport.code}">Show Weather Details</button>
          <div id="weather-details-${airport.code}" class="weather-details hidden">
            <div class="weather-row">
              <span class="weather-label">Chance of Precipitation:</span>
              <span class="weather-value">${forecastData.chance_of_precipitation}</span>
            </div>
            <div class="weather-row">
              <span class="weather-label">Max Temperature:</span>
              <span class="weather-value">${forecastData.max_temp}°F</span>
            </div>
            <div class="weather-row">
              <span class="weather-label">Max Wind Speed:</span>
              <span class="weather-value">${forecastData.max_wind_speed} mph</span>
            </div>
          </div>
        </div>
      </div>
    `;
    }

  const TransparentOriginIcon = L.Icon.extend({
    options: {
      iconUrl: '/static/images/origin_marker.png',
      iconSize: [50, 50],
      iconAnchor: [25, 50],
      popupAnchor: [0, -50],
      className: 'transparent-icon'
    },
    createIcon: function (oldIcon) {
      const img = L.Icon.prototype.createIcon.call(this, oldIcon);
      img.style.backgroundColor = 'transparent';
      return img;
    }
  });

  const TransparentDestinationIcon = L.Icon.extend({
    options: {
      iconUrl: '/static/images/destination_marker.png',
      iconSize: [50, 50],
      iconAnchor: [25, 50],
      popupAnchor: [0, -50],
      className: 'transparent-icon'
    },
    createIcon: function (oldIcon) {
      const img = L.Icon.prototype.createIcon.call(this, oldIcon);
      img.style.backgroundColor = 'transparent';
      return img;
    }
  });

  const originIcon = new TransparentOriginIcon();
  const destinationIcon = new TransparentDestinationIcon();

  function drawFlightPath(origin, destination, originForecast, destinationForecast) {
    console.log("Drawing flight path");
    console.log("Origin", origin);
    console.log("Destination", destination);
  
    // Remove any existing polylines and markers from the map
    myMap.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.Marker) {
        myMap.removeLayer(layer);
      }
    });
  
    const originCoords = [parseFloat(origin.lat), parseFloat(origin.lon)];
    const destCoords = [parseFloat(destination.lat), parseFloat(destination.lon)];
  
    console.log("Origin Coordinates:", originCoords);
    console.log("Destination Coordinates:", destCoords);
  
    // Draw the flight path
    L.polyline([originCoords, destCoords], { color: 'red', weight: 3, dashArray: '10, 10' }).addTo(myMap);
  
    const originPopupContent = originForecast ? createPopupContent(origin, originForecast) : `<div class="popup-content"><p>Forecast unavailable for ${origin.name}</p></div>`;
    const destPopupContent = destinationForecast ? createPopupContent(destination, destinationForecast) : `<div class="popup-content"><p>Forecast unavailable for ${destination.name}</p></div>`;
  
    // Add markers with popup content
    L.marker(originCoords, { icon: originIcon, title: origin.name })
      .bindPopup(originPopupContent)
      .addTo(myMap)
      .openPopup();
  
    L.marker(destCoords, { icon: destinationIcon, title: destination.name })
      .bindPopup(destPopupContent)
      .addTo(myMap)
      .openPopup();
  
    // Fit the map bounds to include both markers
    const bounds = L.latLngBounds([originCoords, destCoords]);
    myMap.fitBounds(bounds, { padding: [75, 75] });
  
    // Initialize toggle buttons after popups have been added
    initializeWeatherToggle();
  }

  function getForecast(date, airportCode) {
    const formattedDate = new Date(date).toISOString().split('T')[0];
    const url = `http://127.0.0.1:5000/weather/${formattedDate}/${airportCode.toLowerCase()}/`;

    return fetch(url)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .catch(error => {
        console.error('Error fetching forecast:', error);
        throw error;
      });
  }

  function initializeWeatherToggle() {
    // Get all toggle buttons
    const toggleButtons = document.querySelectorAll('.toggle-button');

    toggleButtons.forEach(button => {
      button.addEventListener('click', function() {
        const targetId = this.getAttribute('data-target');
        const weatherDetails = document.getElementById(targetId);

        if (weatherDetails.classList.contains('hidden')) {
          weatherDetails.classList.remove('hidden');
          weatherDetails.classList.add('visible');
          this.textContent = 'Hide';
        } else {
          weatherDetails.classList.remove('visible');
          weatherDetails.classList.add('hidden');
          this.textContent = 'Show Weather Details';
        }
      });
    });
  }

  document.getElementById('flightForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const originInput = document.getElementById('origin').value;
    const destinationInput = document.getElementById('destination').value;
    const airlineInput = document.getElementById('airline').value;
    const departureTime = document.getElementById('departureTime').value;

    const originCode = originInput.split('(').pop().slice(0, -1);
    const destinationCode = destinationInput.split('(').pop().slice(0, -1);
    const airlineName = airlineInput.trim();
    const origin = airportData.find(airport => airport.code === originCode);
    const destination = airportData.find(airport => airport.code === destinationCode);

    if (origin && destination) {
      Promise.all([
        getForecast(departureTime, originCode),
        getForecast(departureTime, destinationCode)
      ])
        .then(([originForecast, destinationForecast]) => {
          drawFlightPath(origin, destination, originForecast, destinationForecast);
        })
        .catch(error => {
          console.error('Error fetching forecasts:', error);
        });
    } else {
      console.error('Could not find airport data');
    }
  });

  document.getElementById('resetButton').addEventListener('click', function () {
    document.getElementById('flightForm').reset();
    myMap.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.Marker) {
        myMap.removeLayer(layer);
      }
    });
    myMap.setView([48, -109], 4);
    document.getElementById('result').innerHTML = '';
    document.getElementById('forecast-content').innerHTML = '';
  });
});