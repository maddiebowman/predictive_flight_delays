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

  function fetchAirlines() {
    fetch('/data_test/0')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        // Extract unique airline names
        const airlineData = [...new Set(data.map(flight => flight.CARRIER_NAME))];
        airlineData.sort();
        populateDatalist('airlines', airlineData, airline => airline);
      })
      .catch(error => console.error('Error fetching airlines:', error));
  }

  // Call fetchAirlines after airport data has been populated
  fetchAirlines();

  function createPopupContent(airport, forecastData) {
    return `
      <div class="popup-content">
        <div class="airport-name">${airport.name}</div>
        <div class="airport-location">${airport.city}, ${airport.state}</div>
        <h4>Weather Forecast</h4>
        <div class="weather-details">
        <div class="weather-row">
            <span class="weather-label"Day Time Forecast:</span>
            <strong class="weather-forecast-day">Daily Forecast: ${forecastData.day_time_forecast}</strong>
          </div>
          <div class="weather-row">
            <span class="weather-label">Chance of Precipitation:</span>
            <strong class="weather-value">${forecastData.chance_of_precipitation}</strong>
          </div>
          <div class="weather-row">
            <span class="weather-label">Max Temperature:</span>
            <strong class="weather-value">${forecastData.max_temp}°F</strong>
          </div>
          <div class="weather-row">
            <span class="weather-label">Max Wind Speed:</span>
            <strong class="weather-value">${forecastData.max_wind_speed} mph</strong>
          </div>
          <div class="weather-row">
            <span class="weather-label"Night Time Forecast:</span>
            <strong class="weather-forecast-night">Nightly Forecast: ${forecastData.night_time_forecast}</strong>
          </div>
        </div>
      </div>
    `;
  }

  const TransparentOriginIcon = L.Icon.extend({options: {
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

  const TransparentDestinationIcon = L.Icon.extend({options: {
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
    console.log("Desstination", destination);

    myMap.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.Marker) {
        myMap.removeLayer(layer);
      }
    });
  
    const originCoords = [parseFloat(origin.lat), parseFloat(origin.lon)];
    const destCoords = [parseFloat(destination.lat), parseFloat(destination.lon)];

    console.log("Origin Coordinates:", originCoords);
    console.log("Destination Coordinates:", destCoords);
  
    L.polyline([originCoords, destCoords], { color: 'red', weight: 3, dashArray: '10, 10' }).addTo(myMap);
  
    const originPopupContent = originForecast ? createPopupContent(origin, originForecast) : `<div class="popup-content"><p>Forecast unavailable for ${origin.name}</p></div>`;
    const destPopupContent = destinationForecast ? createPopupContent(destination, destinationForecast) : `<div class="popup-content"><p>Forecast unavailable for ${destination.name}</p></div>`;
  
    L.marker(originCoords, { icon: originIcon, title: origin.name })
      .bindPopup(originPopupContent)
      .addTo(myMap)
      .openPopup();
  
    L.marker(destCoords, { icon: destinationIcon, title: destination.name })
      .bindPopup(destPopupContent)
      .addTo(myMap)
      .openPopup();
  
    const bounds = L.latLngBounds([originCoords, destCoords]);
    myMap.fitBounds(bounds, { padding: [50, 50] });
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
