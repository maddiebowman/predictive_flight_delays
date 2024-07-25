// init variables
var primaryVarOpts = {"DAY_OF_WEEK": "Day of Week",
  "DEP_TIME_BLK": "Departure Time",
  "MONTH": "Month",
  "DISTANCE_GROUP": "Flight Distance",
  "SEGMENT_NUMBER": "Airplane Daily Segment",
  "CONCURRENT_FLIGHTS": "Concurrent Flights",
  "AIRPORT_FLIGHTS_MONTH": "Airport Flights/Month",
  "AIRLINE_FLIGHTS_MONTH": "Airline Flights/Month",
  "AVG_MONTHLY_PASS_AIRPORT": "Avg Monthly Pax, Airport",
  "AVG_MONTHLY_PASS_AIRLINE": "Avg Monthly Pax, Airline"};

var secondaryVarOpts = {"DAY_OF_WEEK": "Day of Week",
    "DEP_TIME_BLK": "Departure Time",
    "MONTH": "Month",
    "CARRIER_NAME": "Airline",
    "DISTANCE_GROUP": "Flight Distance"}


const lineMetadata = {
  DAY_OF_WEEK: {
    title: "Day of Week",
    increments: {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"},
    count: 7
  },
  DEP_TIME_BLK: {
    title: "Departure Time",
    increments: {
      1: "0000-0559", 2: "0600-0659", 3: "0700-0759", 4: "0800-0859", 5: "0900-0959", 6: "1000-1059", 7: "1100-1159",
      8: "1200-1259", 9: "1300-1359", 10: "1400-1459", 11: "1500-1559", 12: "1600-1659", 13: "1700-1759", 14: "1800-1859",
      15: "1900-1959", 16: "2000-2059", 17: "2100-2159", 18: "2200-2259", 19: "2300-2359"},
    count: 19
  },
  MONTH: {
    title: "Month",
    increments: {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
    count: 12
  },
  DISTANCE_GROUP: {
    title: "Flight Distance",
    increments: {
      1: "<250 Miles", 2: "250-499 Miles", 3: "500-749 Miles", 4: "750-999 Miles", 5: "1000-1249 Miles", 6: "1250-1499 Miles",
      7: "1500-1750 Miles", 8: "1751-1999 Miles", 9: "2000-2249 Miles", 10: "2250-2499 Miles", 11: "2500+ Miles"
    },
    count: 11
  },
  CARRIER_NAME: {
    title: "Airline",
    increments: {
      1: "Alaska Airlines Inc.", 2: "Allegiant Air", 3: "American Airlines Inc.", 4: "American Eagle Airlines Inc.", 5: "Atlantic Southeast Airlines",
      6: "Comair Inc.", 7: "Delta Air Lines Inc.", 8: "Endeavor Air Inc.", 9: "Frontier Airlines Inc.", 10: "Hawaiian Airlines Inc.", 11: "JetBlue Airways",
      12: "Mesa Airlines Inc.", 13: "Midwest Airline, Inc.", 14: "SkyWest Airlines Inc.", 15: "Southwest Airlines Co.", 16: "Spirit Air Lines", 17: "United Air Lines Inc."
    },
    count: 17
  }
}
// populate first dropdown
var firstVarSelector = document.getElementById("var1Selector");
var var1Opt = document.createElement("option");
var1Opt.text = "First Variable";
firstVarSelector.add(var1Opt);
Object.keys(primaryVarOpts).forEach(function(key) {
  var1Opt = document.createElement("option");
  var1Opt.value = key;
  var1Opt.text = primaryVarOpts[key];
  firstVarSelector.add(var1Opt);
});

//populate second dropdown, based on what is selected in first
var secondVarSelector = document.getElementById("var2Selector");
firstVarSelector.addEventListener("change", function() {
  secondVarSelector.innerHTML = "";
  var var2Opt = document.createElement("option");
  var2Opt.text = "Second Variable";
  secondVarSelector.add(var2Opt);
  Object.keys(secondaryVarOpts).forEach(function(key) {
    console.log(key);
    console.log(firstVarSelector.value);
    if(key != firstVarSelector.value) {
    var2Opt = document.createElement("option");
    var2Opt.value = key;
    var2Opt.text = secondaryVarOpts[key];
    secondVarSelector.add(var2Opt);}
  });
});
function createChart(data, var1, var2) {
  var linesData = {};
  var metadataLookup = {}; // Create an empty lookup object each time

  // Create a lookup table for metadata based on the current var2
  Object.entries(lineMetadata[var2].increments).forEach(([key, value]) => {
    metadataLookup[key] = value;
    console.log(key, value);
  });
  console.log(metadataLookup);
  // Create buckets for each line
  data.forEach(object => {
    var lineKey = object[var2];
    console.log(object[var2]);
    if (!linesData[lineKey]) {
      linesData[lineKey] = [];
    }
    linesData[lineKey].push({
      x: object[var1],
      y: parseFloat((object.tot_delays / object.total_flights * 100).toFixed(2)),
      // Use the lineKey as the name
      name: metadataLookup[lineKey] || lineKey
    });
  });

  // Convert linesData into an array of line objects
  var lines = Object.values(linesData).map(lineData => ({
    x: lineData.map(point => point.x),
    y: lineData.map(point => point.y),
    name: lineData[0].name // Use the first element's name as the line name
  }));

  var lineChartLayout = {
    title: `<b>Flight Delay Rates by ${primaryVarOpts[var1]} and ${secondaryVarOpts[var2]}, 2019</b>`, xaxis: {title: primaryVarOpts[var1]}, yaxis: {title: "Delay Rate (%)"}}
  Plotly.newPlot("chart", lines, lineChartLayout);
}


function updateChart() {
  var var1 = document.getElementById("var1Selector").value;
  var var2 = document.getElementById("var2Selector").value;

  d3.json("http://127.0.0.1:5000/charts/" + var1 + "/" + var2 + "/0")
    .then(data => {
      createChart(data, var1, var2); 
    });
}

function initChart() {
  d3.json("http://127.0.0.1:5000/charts/DEP_TIME_BLK/DAY_OF_WEEK/0").then(data => {
;
    createChart(data, "DEP_TIME_BLK", "DAY_OF_WEEK");
    })

  }

initChart();
document.getElementById("var2Selector").addEventListener("change", updateChart);

