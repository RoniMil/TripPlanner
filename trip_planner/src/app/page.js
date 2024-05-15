'use client'
import { useState } from 'react';
const OPENAI_API_KEY = "sk-proj-qBbquYjeeRcbwcs8C1IHT3BlbkFJLZHyfNMDcKE3xW9wWaNr"

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
  
    const apiKey = OPENAI_API_KEY;
    const prompt = `Create a daily plan for a trip to ${destination} from ${formData.startDate} to ${formData.endDate}.`;
  
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: "gpt-3.5-turbo",
          messages: [
            {
              role: "user",
              content: prompt
            }
          ]
        })
      });
      const data = await response.json();
      setTripPlan(data.choices[0].message['content']);
    } catch (error) {
      console.error('Error fetching daily plan:', error);
    }
  };
  

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
        <div key={index}>
          <h2>{destination}</h2>
          <p>Flight Info: {info[0]}</p>
          <p>Hotel Info: {info[1]}</p>
          <p>Price: {info[2]}</p>
          <button onClick={() => handleSelectDestination(destination)}>Select This Destination</button>
        </div>
      ))}
      {selectedDestination && (
        <div>
          <h3>Selected Destination: {selectedDestination}</h3>
          <p>Daily Plan: {tripPlan}</p>
        </div>
      )}
    </div>
  );
}


