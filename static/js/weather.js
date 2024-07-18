const url = 'http://127.0.0.1:5000/weather/2024-07-17/lax/';
d3.json(url).then((data) => {
    //enter js code to display data visualization as desired here. console log is just for testing the data:
    console.log(`chance of precipitation: ${data['chance_of_precipitation']}`);
    console.log(`max temperature: ${data['max_temp']}F`);
    console.log(`max wind speed: ${data['max_wind_speed']} mph`);

}); 