'use client'
import { useState } from 'react';

export default function Home() {
  const [formData, setFormData] = useState({
    startDate: '',
    endDate: '',
    budget: '',
    tripType: ''
  });

  const [destinations, setDestinations] = useState([]);

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
    } catch (error) {
      console.error('Error fetching destinations:', error);
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
        </div>
      ))}
    </div>
  );
}
