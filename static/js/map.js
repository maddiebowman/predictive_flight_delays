// Create the map
let map = L.map("map", {center: [39.7392, -104.9847],
zoom: 4
});

// Create the tile layer that will be the background of our map.
var streetmap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

streetmap.addTo(map);

d3.json("http://127.0.0.1:5000/map/0").then(data => {

  var coords = []

  data.forEach(airport => {
    // create lists for the heatmap input
    coords.push([airport.LATITUDE, airport.LONGITUDE, airport.delay_rate * 100]);

    // add markers for airports
    const marker = L.circle([airport.LATITUDE, airport.LONGITUDE], {color:"black", radius: 10}).addTo(map);
    marker.bindPopup(`${airport.DEPARTING_AIRPORT} 2019 delay rate: ${airport.delay_rate}%`)
  })
  L.heatLayer(coords, {radius: 30}).addTo(map);
    
});