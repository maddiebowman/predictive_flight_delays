// Define function for 7-day forecast for origin airport
async function origin_fcstfn(date, origination) {
    const url = 'data/airport_codes_.csv';  // Assuming this file is accessible locally

    // Read in airport codes lat/long file
    const airportCodes = await d3.csv(url);

    // Look up lat/long for airport codes
    const ac_df = airportCodes.find(row => row.iata === origination);
    const origin_lat = ac_df.latitude;
    const origin_long = ac_df.longitude;

    // Get weather data
    const origin_url = `https://api.weather.gov/points/${origin_lat},${origin_long}`;
    const origin_7dresponse = await d3.json(origin_url);
    const origin_7dforecastUrl = origin_7dresponse.properties.forecast;
    const origin_7dforecast = await d3.json(origin_7dforecastUrl);

    let origin_tmax = null;
    let origin_awnd = null;
    let origin_precip = null;

    // Find max temp, max wind speed, and chance of precipitation for origin airport
    origin_7dforecast.properties.periods.forEach(period => {
        const start_time = period.startTime;
        const match = new RegExp(`^${date}`).test(start_time);
        const daytime = period.isDaytime;

        if (match && daytime) {
            origin_tmax = period.temperature;
            try {
                origin_awnd = parseInt(period.windSpeed.split(' ')[2]);
            } catch {
                origin_awnd = parseInt(period.windSpeed.split(' ')[0]);
            }
            origin_precip = period.probabilityOfPrecipitation?.value || 0;
        }
    });

    return `(max temp: ${origin_tmax}, max wind speed: ${origin_awnd}, chance of precipitation: ${origin_precip}%)`;
}

// input for demonstration purposes only. airport and date inputs should come from user interface
const origination = 'LAX';
const date = '2024-07-17';

origin_fcstfn(date, origination)
    .then(result => console.log(result))
    .catch(error => console.error('Error fetching forecast:', error));
