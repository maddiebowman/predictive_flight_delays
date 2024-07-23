const days = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"};
var monData = [];
var tuesData = [];
var wedData = [];
var thursData = [];
var friData = [];
var satData = [];
var sunData = [];
var weekData = [];

function pickDay(day) {
  return day==1 ? monData : 
         day==2 ? tuesData :
         day==3 ? wedData : 
         day==4 ? thursData : 
         day==5 ? friData : 
         day==6 ? satData : 
         sunData;
};

var variableOptions = {"Day of Week": "DAY_OF_WEEK",
                       "Departure Time": "DEP_TIME_BLK", 
                       "Month": "MONTH",
                       "Carrier Name": "CARRIER_NAME",
                       "Departing Airport": "DEPARTING_AIRPORT"
};




d3.json("http://127.0.0.1:5000/test2/0").then(data => {
  function createWeeklyChartData(dayOfWk) {
    data.forEach(date_time => {
      if (date_time.DAY_OF_WEEK == dayOfWk) {
        pickDay(date_time.DAY_OF_WEEK).push({x: date_time.DEP_TIME_BLK, y: parseFloat((date_time.tot_delays / date_time.total_flights * 100).toFixed(2))});
      }
  });
  }
  function createChart() {
    weekData = [];
    for (let i = 1; i < 8; i++) {
      createWeeklyChartData(i);
      var lineTrace = {
        x: pickDay(i).map(point => point.x),
        y: pickDay(i).map(point => point.y),
        name: days[i],
        type: 'scatter'
      };
      var lineChartLayout = {
        title: "<b>Flight Delay Rates by Day of Week and Departure Time, 2019</b>", xaxis: {title: "Departure Time Block"}, yaxis: {title: "Delay Rate (%)"}
      }
      weekData.push(lineTrace);
      console.log(weekData);
    }

    Plotly.newPlot("chart",weekData,lineChartLayout);
  }

  createChart();
  var firstVarSelector = document.getElementById("var1Selector");
  var varOpt = document.createElement("option");
  varOpt.text = "First Variable";
  console.log(varOpt);
  firstVarSelector.add(varOpt);
  for (let i=0; i < variableOptions.length; i++) {
    varOpt = document.createElement("option");
    varOpt.text = Object.keys(variableOptions)[i];
    varOpt.value = variableOptions[Object.keys(variableOptions)[i]];
    firstVarSelector.add(varOpt);
    console.log((variableOptions)[i].text)
  };
});

