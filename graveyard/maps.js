// Create a map centered around a specific location
var myMap = L.map('map').setView([48, -109], 4); // Centering the map on the US

// Add a tile layer for the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(myMap);

// Global variable to store airport data
var airportData;

// Function to draw flight path
function drawFlightPath(origin, destination) {
  // Clear existing flight path
  myMap.eachLayer((layer) => {
    if (layer instanceof L.Polyline) {
      myMap.removeLayer(layer);
    }
  });

  const originCoords = [parseFloat(origin.lat), parseFloat(origin.lon)];
  const destCoords = [parseFloat(destination.lat), parseFloat(destination.lon)];

  // Draw a line between origin and destination - adding style to the line
  L.polyline([originCoords, destCoords], { color: 'red', weight: 3, dashArray: '10, 10'}).addTo(myMap);

    // Add markers at the origin and destination
    L.marker(originCoords, { title: origin.name })
    .bindPopup(`<b>${origin.name}</b><br>${origin.city}, ${origin.state}`)
    .addTo(myMap)
    .openPopup();

  L.marker(destCoords, { title: destination.name })
    .bindPopup(`<b>${destination.name}</b><br>${destination.city}, ${destination.state}`)
    .addTo(myMap)
    .openPopup();

  // Fit the map to show both points
  myMap.fitBounds([originCoords, destCoords]);
}

// Fetch airport data from the JSON file
fetch('https://gist.githubusercontent.com/tdreyno/4278655/raw/7b0762c09b519f40397e4c3e100b097d861f5588/airports.json')
  .then(response => response.json())
  .then(data => {
    airportData = data.filter(airport => airport.country === 'United States' || airport.country === 'Puerto Rico');
  })
  .catch(error => console.error('Error fetching the airport data:', error));

// Add event listener for form submission
document.getElementById('flightForm').addEventListener('submit', function (event) {
  event.preventDefault();

  const originInput = document.getElementById('origin').value.split('(').pop().slice(0, -1);
  const destinationInput = document.getElementById('destination').value.split('(').pop().slice(0, -1);

  const origin = airportData.find(airport => airport.code === originInput);
  const destination = airportData.find(airport => airport.code === destinationInput);

  if (origin && destination) {
    drawFlightPath(origin, destination);
  } else {
    console.error('Could not find airport data');
  }
});
