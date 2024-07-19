document.addEventListener('DOMContentLoaded', function() {
  d3.csv('../data/airport.csv').then(function(data) {
    const originSelect = document.getElementById('origin');
    const destinationSelect = document.getElementById('destination');
    
    data.forEach(function(airport) {
      const originOption = document.createElement('option');
      originOption.value = airport.IATA;
      originOption.textContent = `${airport.AIRPORT} (${airport.IATA})`;
      originSelect.appendChild(originOption);
      
      const destinationOption = document.createElement('option');
      destinationOption.value = airport.IATA;
      destinationOption.textContent = `${airport.AIRPORT} (${airport.IATA})`;
      destinationSelect.appendChild(destinationOption);
    });
  }).catch(function(error) {
    console.error('Error loading airport data:', error);
  });
});



//   document.getElementById('flightForm').addEventListener('submit', async function(event) {
//     event.preventDefault();

//     const origin = originSelect.value;
//     const destination = destinationSelect.value;
//     const flightNumber = document.getElementById('flightNumber').value;
//     const departureTime = document.getElementById('departureTime').value;

//     updateMaps(origin, destination);
//     updateWeather(origin, destination, departureTime);

//     const delayPrediction = await getDelayPrediction(origin, destination, flightNumber, departureTime);
//     const delayStatus = delayPrediction ? 'DELAY' : 'NO DELAY';
//     document.getElementById('result').textContent = `Flight ${flightNumber} from ${origin} to ${destination} departing at ${departureTime} is predicted ${delayStatus}`;
    
//     this.reset();
//   });

//   const getDelayPrediction = async (origin, destination, flightNumber, departureTime) => {
//     try {
//       const response = await fetch('insert our machine model when complete?', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ origin, destination, flightNumber, departureTime })
//       });

//       if (!response.ok) throw new Error('Failed to fetch delay prediction');

//       const data = await response.json();
//       return data.delay;
//     } catch (error) {
//       console.error('Error fetching delay prediction:', error);
//       return false;
//     }
//   };

//   const updateMaps = (origin, destination) => {
//     console.log(`Updating map for ${origin} to ${destination}`);
//   };

//   const updateWeather = (origin, destination, departureTime) => {
//     console.log(`Updating weather for ${origin} to ${destination}, departing at ${departureTime}`);
//   };
// });
