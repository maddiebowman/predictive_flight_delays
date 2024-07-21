document.getElementById('flightForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const origin = document.getElementById('origin').value;
    const destination = document.getElementById('destination').value;
    const departureTime = document.getElementById('departureTime').value;

    const departureDate = new Date(departureTime).toISOString().split('T')[0];
    const departureHour = new Date(departureTime).getHours();

    // Fetch weather data
    fetch(`/weather/${departureDate}/${origin}`)
        .then(response => response.json())
        .then(weatherData => {
            const tmax = weatherData.tmax;
            const awnd = weatherData.awnd;
            const prcp = weatherData.prcp;

            // Prepare data to send to Flask backend
            const formData = new FormData();
            formData.append('origin', origin);
            formData.append('destination', destination);
            formData.append('departureDate', departureDate);
            formData.append('departureHour', departureHour);
            formData.append('tmax', tmax);
            formData.append('awnd', awnd);
            formData.append('prcp', prcp);

            fetch('/predictions', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('prediction-result').innerText = data.prediction;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        })
        .catch(error => {
            console.error('Error fetching weather data:', error);
        });
});
