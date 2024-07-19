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

  const url = 'https://gist.githubusercontent.com/tdreyno/4278655/raw/7b0762c09b519f40397e4c3e100b097d861f5588/airports.json';
  let airportData;

  fetch(url)
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
      populateDatalist('origins', airportData);
      populateDatalist('destinations', airportData);
    })
    .catch(error => console.error('Error fetching the airport data:', error));

  function populateDatalist(datalistId, airports) {
    const datalist = document.getElementById(datalistId);
    if (datalist) {
      datalist.innerHTML = '';
      airports.forEach(airport => {
        const option = document.createElement('option');
        option.value = `${airport.name} (${airport.code})`;
        datalist.appendChild(option);
      });
    } else {
      console.error(`Datalist with ID ${datalistId} not found`);
    }
  }

  function createPopupContent(airport, forecastData) {
    return `
      <div class="popup-content">
        <div class="airport-name">${airport.name}</div>
        <div class="airport-location">${airport.city}, ${airport.state}</div>
        <h4>Weather Forecast</h4>
        <div class="weather-details">
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
        </div>
      </div>
    `;
  }

  function drawFlightPath(origin, destination, originForecast, destinationForecast) {
    myMap.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.Marker) {
        myMap.removeLayer(layer);
      }
    });

    const originCoords = [parseFloat(origin.lat), parseFloat(origin.lon)];
    const destCoords = [parseFloat(destination.lat), parseFloat(destination.lon)];

    L.polyline([originCoords, destCoords], { color: 'red', weight: 3, dashArray: '10, 10' }).addTo(myMap);

    L.marker(originCoords, { title: origin.name })
      .bindPopup(createPopupContent(origin, originForecast))
      .addTo(myMap)
      .openPopup();

    L.marker(destCoords, { title: destination.name })
      .bindPopup(createPopupContent(destination, destinationForecast))
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
    const departureTime = document.getElementById('departureTime').value;

    const originCode = originInput.split('(').pop().slice(0, -1);
    const destinationCode = destinationInput.split('(').pop().slice(0, -1);

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
          document.getElementById('forecast-content').innerHTML = `<p>Error: ${error.message}</p>`;
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
