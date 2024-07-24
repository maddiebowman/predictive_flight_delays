document.addEventListener('DOMContentLoaded', function () {
    // Create the map
    let map = L.map("heatmap", {
        center: [39.7392, -104.9847],
        zoom: 3.5
    });

    // Create the tile layer
    var streetmap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    streetmap.addTo(map);

    // Fetch data from the server
    d3.json("http://127.0.0.1:5000/map/0").then(data => {
        var coords = [];

        data.forEach(airport => {
            // Create lists for the heatmap input
            coords.push([airport.LATITUDE, airport.LONGITUDE, airport.delay_rate*100]);

            // Add markers for airports
            const marker = L.circle([airport.LATITUDE, airport.LONGITUDE], {
                color: "black",
                radius: 40
            }).addTo(map);
            marker.bindPopup(`${airport.DEPARTING_AIRPORT} 2019 delay rate: ${airport.delay_rate}%`);
        });

        // Add the heat layer
        const heatLayer = L.heatLayer(coords, {
            radius: 30
        }).addTo(map);

        // Dynamically create legend with heatmap colors
        const legend = L.control({position: 'bottomright'});

      legend.onAdd = function (map) {
          const div = L.DomUtil.create('div', 'legend');
          div.innerHTML = `
              <span class="legend-title">Delay Rates (%)</span>
              <div class="legend-row">
                  <div class="legend-color-box" style="background-color: blue;"></div>
                  <div class="legend-label">≤ 10%</div>
              </div>
              <div class="legend-row">
                  <div class="legend-color-box" style="background-color: cyan;"></div>
                  <div class="legend-label">11-14%</div>
              </div>
              <div class="legend-row">
                  <div class="legend-color-box" style="background-color: lime;"></div>
                  <div class="legend-label">15-17%</div>
              </div>
              <div class="legend-row">
                  <div class="legend-color-box" style="background-color: yellow;"></div>
                  <div class="legend-label">18-20%</div>
              </div>
              <div class="legend-row legend-bottom">
                  <div class="legend-color-box" style="background-color: red;"></div>
                  <div class="legend-label">≥ 21%</div>
              </div>
          `;
          return div;
      };

        legend.addTo(map);
    });
});
