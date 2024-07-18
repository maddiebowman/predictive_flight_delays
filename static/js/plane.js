const plane_url = 'http://127.0.0.1:5000/plane/2024-07-17/wn658/';
d3.json(plane_url).then((data) => {
    //enter js code to display data visualization as desired here. console log is just for testing the data:
    console.log(`registration/tail number: ${data['registration/tail number']}`);
    console.log(`year of flight: ${data['flight year']}`);
    console.log(`plane's manufactured year: ${data["plane's manufactured year"]}`);
    console.log(`plane age based on flight date: ${data['plane age based on flight date']} year`);

}); 

