'use client'
import { useState } from 'react';

const OPENAI_API_KEY = "sk-proj-qBbquYjeeRcbwcs8C1IHT3BlbkFJLZHyfNMDcKE3xW9wWaNr";

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

    const tripPrompt = `Create a daily plan for a trip to ${destination} from ${formData.startDate} to ${formData.endDate}. Please give the plan in a list where each element is a day. SEPARATE EACH DAY WITH A NEWLINE.`;

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
      setTripPlan(planData.choices[0].message['content']);
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
          prompt: prompt,
          n: 4, // Generate 4 images
        })
      });
      const data = await response.json();
      return data.data.map(image => image.url);  // Assuming API returns URLs of images
    } catch (error) {
      console.error('Error fetching images:', error);
      return [];
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
