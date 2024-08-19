'use client'
import { useState } from 'react';

// Load environment variables from .env file
dotenv.config();

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

export default function Home() {
  const [formData, setFormData] = useState({
    startDate: '',
    endDate: '',
    budget: '',
    tripType: ''
  });

  const [destinations, setDestinations] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [tripPlan, setTripPlan] = useState("");
  const [images, setImages] = useState([]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const apiURL = `http://127.0.0.1:8000/?start_date=${formData.startDate}&end_date=${formData.endDate}&budget=${formData.budget}&trip_type=${formData.tripType}`;
    try {
      const response = await fetch(apiURL);
      const data = await response.json();
      setDestinations(Object.entries(data));
      setSelectedDestination(null);  // Reset selection on new search
    } catch (error) {
      console.error('Error fetching destinations:', error);
    }
  };

  const handleSelectDestination = async (destination) => {
    setSelectedDestination(destination);
    setDestinations([]); // Clear all other destinations

    const tripPrompt = `Create a daily plan for a trip to ${destination} from ${formData.startDate} to ${formData.endDate}. Please give the plan in a JSON format in which the key is: Day x where x is the day number and the value is a list of 3 bullets describing the day.`;
    try {
      const planResponse = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages: [{ role: "user", content: tripPrompt }]
        })
      });
      const planData = await planResponse.json();
      setTripPlan(JSON.parse(planData.choices[0].message['content']));
      const imagePrompts = `Images depicting ${formData.tripType} trip to ${destination} from ${formData.startDate} to ${formData.endDate}`;
      const images = await fetchImages(imagePrompts);
      setImages(images);  // Assuming you have a state to store images
    } catch (error) {
      console.error('Error fetching daily plan or images:', error);
    }
  };

  const fetchImages = async (prompt) => {
    try {
      const response = await fetch('https://api.openai.com/v1/images/generations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: "dall-e-2",
          prompt: `This is my trip plan, give me 4 pictures that best describe the trip. My trip plan: ${prompt}`,
          n: 4 // Generate 4 images
        })
      });
      const data = await response.json();
      return data.data.map(image => image.url);  // Assuming API returns URLs of images
    } catch (error) {
      console.error('Error fetching images:', error);
      return [];
    }
  };

  // Helper function to format the trip plan with HTML line breaks
  const formatTripPlan = (plan) => {
    return (
      <>
        {Object.entries(plan).map(([day, activities], index) => (
          <div key={index}>
            <strong>{day}</strong>
            <ul>
              {activities.map((activity, idx) => (
                <li key={idx}>{activity}</li>
              ))}
            </ul>
            <br /> {/* Add a line break after each day's list for better separation */}
          </div>
        ))}
      </>
    );
  };

  // Helper function to format the trip plan with HTML line breaks
  function formatFlights(flights) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>Flight Details</h1>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {flights.map((flight, index) => (
            <li key={index} style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px' }}>
              <h2 style={{ color: '#ff00ff' }}>Flight Number: {flight.flight_number}</h2>
              <div>
                <strong>Departure:</strong>
                <ul>
                  <li>Name: {flight.departure_airport.name}</li>
                  <li>ID: {flight.departure_airport.id}</li>
                  <li>Time: {flight.departure_airport.time}</li>
                </ul>
              </div>
              <div>
                <strong>Arrival:</strong>
                <ul>
                  <li>Name: {flight.arrival_airport.name}</li>
                  <li>ID: {flight.arrival_airport.id}</li>
                  <li>Time: {flight.arrival_airport.time}</li>
                </ul>
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  // Helper function to format the trip plan with HTML line breaks
  function formatHotel(hotel) {
    return (
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>Hotel Details</h1>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <div>
            <ul style={{ marginBottom: '20px', border: '1px solid #ccc', padding: '10px' }}>
              <li>Name: {hotel["name"]}</li>
              <li>Check in time: {hotel["check_in_time"]}</li>
              <li>Check out time: {hotel["check_out_time"]}</li>
            </ul>
          </div>
        </ul>
      </div>
    );
  }


  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="date" name="startDate" value={formData.startDate} onChange={handleChange} />
        <input type="date" name="endDate" value={formData.endDate} onChange={handleChange} />
        <input type="number" name="budget" value={formData.budget} onChange={handleChange} />
        <select name="tripType" value={formData.tripType} onChange={handleChange}>
          <option value="ski">Ski</option>
          <option value="beach">Beach</option>
          <option value="city">City</option>
        </select>
        <button type="submit">Plan Trip</button>
      </form>
      {destinations.map(([destination, info], index) => (
        <div style={{ marginBottom: '20px', padding: '10px' }} key={index}>
          <h2>{index + 1}. {destination}</h2>
          <p>{formatFlights(info[0])}</p>
          <p>{formatHotel(info[1])}</p>
          <h1>Price: {info[2]}</h1>
          <button onClick={() => handleSelectDestination(destination)}>Select This Destination</button>
        </div>
      ))}
      {selectedDestination && (
        <div>
          <h2>Selected Destination: {selectedDestination}</h2>
          <h3>Your Trip Plan:</h3><br></br>
          <div>{formatTripPlan(tripPlan)}</div><br></br>
          <h3>Your trip will look like this:</h3>
          <div>
            {images.map((image, index) => (
              <img key={index} src={image} alt="Trip Image" />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
