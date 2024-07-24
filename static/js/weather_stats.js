// bar chart for tmax
const temp_url = 'http://127.0.0.1:5000/2019_delay_tmax';

let temps = [];
let pctDelays = [];

function get_temp_delays() {
    d3.json(temp_url).then((temp_data) => {
        // Check if data is an array and has at least one item
        if (Array.isArray(temp_data) && temp_data.length > 0) {
            // Loop through data to get temp and % delays
            temp_data.forEach((data) => {
                // You no longer need to extract temps and pctDelays separately
                temps.push(data['temperature_bucket']);
                pctDelays.push(parseFloat(data['total_percentage_of_total_delays']));
            });

            // Call function to create bar chart
            createTempChart(temps, pctDelays);
        } else {
            console.error('Unexpected data format:', temp_data);
        }
    }).catch(error => {
        console.error('Error fetching data:', error);
    });
}

function createTempChart(buckets, pctDelays) {
    // Set up dimensions and margins
    const margin = { top: 50, right: 30, bottom: 60, left: 50 },
          width = 700 - margin.left - margin.right,
          height = 600 - margin.top - margin.bottom;

    // Append SVG to the body
    const svg = d3.select('#temp-chart').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Add light grey background to match container
    svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', '#f9f9f9');

    // Set up x and y scales
    const x = d3.scaleBand()
        .domain(buckets)
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(pctDelays)])
        .nice()
        .range([height, 0]);

    // Append title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -margin.top / 2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text('% of Flight Delays in 2019 by Temperature Range');

    // Append x-axis
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .append('text')
        .attr('x', width / 2)
        .attr('y', margin.bottom - 10)
        .attr('fill', 'black')
        .attr('font-size', '11px')
        .attr('text-anchor', 'middle')
        .attr('font-weight', 'bold')
        .text('Temperature (°F)');

    // Append y-axis
    svg.append('text')
        .attr('class', 'axis-label')
        .attr('transform', 'rotate(-90)')
        .attr('y', -50) // Adjust this value to position the label correctly
        .attr('x', -height / 2)
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .attr('font-weight', 'bold')
        .text('% of Flights Delayed');


    // Append bars
    svg.selectAll('.bar')
        .data(pctDelays)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', (d, i) => x(buckets[i]))
        .attr('y', d => y(d))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d))
        .attr('fill', '#0f9641'); // Change bar color

        // Add text labels to bars
        svg.selectAll('.bar-label')
        .data(pctDelays)
        .enter().append('text')
        .attr('class', 'bar-label')
        .attr('x', (d, i) => x(buckets[i]) + x.bandwidth() / 2)
        .attr('y', d => y(d) - 10) // Position above the bar
        .attr('text-anchor', 'middle')
        .attr('fill', 'black')
        .attr('font-size', '11px') // Set font size
        .attr('font-weight', 'bold')
        .text(d => `${d.toFixed(2)}%`); // Add % to data labels
}

//awnd bar charts
const awnd_url = 'http://127.0.0.1:5000/2019_delay_awnd'; // Update URL to match your new endpoint

let windSpeedBuckets = [];
let pctDelays_awnd = [];

function get_awnd_delays() {
    d3.json(awnd_url).then((awnd_data) => {
        // Check if data is an array and has at least one item
        if (Array.isArray(awnd_data) && awnd_data.length > 0) {
            // Loop through data to get wind speed buckets and % delays
            awnd_data.forEach((data) => {
                windSpeedBuckets.push(data['wind_speed_bucket']);
                pctDelays_awnd.push(parseFloat(data['percentage_of_total_delays']));
            });

            // Create a map for easy lookup of percentages
            const dataMap = new Map();
            windSpeedBuckets.forEach((bucket, index) => {
                dataMap.set(bucket, pctDelays_awnd[index]);
            });

            // Sort the buckets numerically
            windSpeedBuckets.sort((a, b) => {
                const aMin = parseInt(a.split('–')[0]);
                const bMin = parseInt(b.split('–')[0]);
                return aMin - bMin;
            });

            // Prepare the data in sorted order
            const sortedData = windSpeedBuckets.map(bucket => ({
                wind_speed_bucket: bucket,
                percentage_of_total_delays: dataMap.get(bucket)
            }));

            // Call function to create bar chart
            createAwndChart(sortedData);
        } else {
            console.error('Unexpected data format:', awnd_data);
        }
    }).catch(error => {
        console.error('Error fetching data:', error);
    });
}

function createAwndChart(sortedData) {
    // Set up dimensions and margins
    const margin = { top: 100, right: 30, bottom: 60, left: 60 },
          width = 500 - margin.left - margin.right,
          height = 600 - margin.top - margin.bottom;

    // Append SVG to the body
    const svg = d3.select('#awnd-chart').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Add light grey background to match container
    svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', '#f9f9f9');

    // Set up x and y scales
    const x = d3.scaleBand()
        .domain(sortedData.map(d => d.wind_speed_bucket))
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(sortedData, d => d.percentage_of_total_delays)])
        .nice()
        .range([height, 0]);

    // Append title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -margin.top / 2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text('% of Flight Delays in 2019 by Wind Speed Range');

    // Append x-axis
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .append('text')
        .attr('x', width / 2)
        .attr('y', margin.bottom - 10)
        .attr('fill', 'black')
        .attr('text-anchor', 'middle')
        .attr('font-weight', 'bold')
        .attr('font-size', '11px')
        .text('Wind Speed (mph)');

    // Append y-axis
    svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y))
        .append('text')
        .attr('x', -width / 2)
        .attr('y', -50)
        .attr('fill', 'black')
        .attr('text-anchor', 'middle')
        .attr('transform', 'rotate(-90)')
        .attr('font-weight', 'bold')
        .attr('font-size', '11px')
        .text('% of Flights Delayed');

    // Append bars
    svg.selectAll('.bar')
        .data(sortedData)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.wind_speed_bucket))
        .attr('y', d => y(d.percentage_of_total_delays))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.percentage_of_total_delays))
        .attr('fill', '#2196F3'); // Change bar color

    // Add text labels to bars
    svg.selectAll('.bar-label')
        .data(sortedData)
        .enter().append('text')
        .attr('class', 'bar-label')
        .attr('x', d => x(d.wind_speed_bucket) + x.bandwidth() / 2)
        .attr('y', d => y(d.percentage_of_total_delays) - 5) // Position above the bar
        .attr('text-anchor', 'middle')
        .attr('fill', 'black')
        .attr('font-weight', 'bold')
        .attr('font-size', '12px')
        .text(d => `${d.percentage_of_total_delays.toFixed(2)}%`); // Add % to data labels
}


// Precipitation bar charts
const prcp_url = 'http://127.0.0.1:5000/2019_delay_prcp'; // Update URL to match your new endpoint

let precipitationBuckets = [];
let pctDelays_prcp = [];

function get_prcp_delays() {
    d3.json(prcp_url).then((prcp_data) => {
        // Check if data is an array and has at least one item
        if (Array.isArray(prcp_data) && prcp_data.length > 0) {
            // Loop through data to get precipitation buckets and % delays
            prcp_data.forEach((data) => {
                precipitationBuckets.push(data['precipitation_bucket']);
                pctDelays_prcp.push(parseFloat(data['percentage_of_total_delays']));
            });

            // Create a map for easy lookup of percentages
            const dataMap = new Map();
            precipitationBuckets.forEach((bucket, index) => {
                dataMap.set(bucket, pctDelays_prcp[index]);
            });

            // Sort the buckets numerically
            precipitationBuckets.sort((a, b) => a - b);

            // Prepare the data in sorted order
            const sortedData = precipitationBuckets.map(bucket => ({
                precipitation_bucket: bucket,
                percentage_of_total_delays: dataMap.get(bucket)
            }));

            // Call function to create bar chart
            createPrcpChart(sortedData);
        } else {
            console.error('Unexpected data format:', prcp_data);
        }
    }).catch(error => {
        console.error('Error fetching data:', error);
    });
}

function createPrcpChart(sortedData) {
    // Set up dimensions and margins
    const margin = { top: 20, right: 30, bottom: 40, left: 40 },
          width = 800 - margin.left - margin.right,
          height = 400 - margin.top - margin.bottom;

    // Append SVG to the body
    const svg = d3.select('body').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Set up x and y scales
    const x = d3.scaleBand()
        .domain(sortedData.map(d => d.precipitation_bucket))
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(sortedData, d => d.percentage_of_total_delays)])
        .nice()
        .range([height, 0]);

    // Append title
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -margin.top / 2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .text('% of Flight Delays in 2019 by Precipitation Range');

    // Append x-axis
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).tickFormat(d => `${d} in`)) // Format x-axis labels
        .append('text')
        .attr('x', width / 2)
        .attr('y', margin.bottom - 10)
        .attr('fill', 'black')
        .attr('text-anchor', 'middle')
        .text('Precipitation (inches)');

    // Append y-axis
    svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y))
        .append('text')
        .attr('x', -margin.left)
        .attr('y', -40)
        .attr('fill', 'black')
        .attr('text-anchor', 'middle')
        .attr('transform', 'rotate(-90)')
        .text('% of Flights Delayed in 2019');

    // Append bars
    svg.selectAll('.bar')
        .data(sortedData)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.precipitation_bucket))
        .attr('y', d => y(d.percentage_of_total_delays))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.percentage_of_total_delays))
        .attr('fill', '#69b3a2'); // Change bar color

    // Add text labels to bars
    svg.selectAll('.bar-label')
        .data(sortedData)
        .enter().append('text')
        .attr('class', 'bar-label')
        .attr('x', d => x(d.precipitation_bucket) + x.bandwidth() / 2)
        .attr('y', d => y(d.percentage_of_total_delays) - 5) // Position above the bar
        .attr('text-anchor', 'middle')
        .attr('fill', 'black')
        .text(d => `${d.percentage_of_total_delays.toFixed(2)}%`); // Add % to data labels
}

// Call the function to execute
get_temp_delays();

// Call the function to execute
get_awnd_delays();

// Will not clal the precipiation function to execute (does not tell a story about impact on delays)




