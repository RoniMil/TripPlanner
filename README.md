
# AI Trip Planner

This project is an AI-powered trip planner developed using Python and Next.js. The application guides users through planning a trip by recommending destinations, finding flights and hotels within a specified budget, generating a daily itinerary, and providing visual representations of the planned trip.

## Features

- **Destination Recommendations**: Based on the user's input, the application recommends five possible travel destinations using OpenAI's GPT API.
- **Flight and Hotel Search**: Automatically searches for the cheapest flights and the most suitable hotels within the user’s budget using the Google Flights and Google Hotels APIs via SerpAPI.
- **Personalized Itinerary**: Generates a detailed daily plan for the selected destination, tailored to the user's trip dates and preferences.
- **Visual Itinerary Representation**: Creates visual images of the trip using OpenAI's DALL-E API to give users a preview of their travel experience.

## How It Works

1. **User Inputs**: The user enters the start and end dates of the trip, the total budget, and the type of trip (e.g., ski, beach, city).
2. **Destination Suggestions**: The system queries OpenAI GPT API for five possible destinations based on the input.
3. **Flight and Hotel Search**: The system searches for flights from Tel Aviv to each suggested destination and identifies the most affordable flight and a hotel that fits the user's budget.
4. **Option Selection**: The user selects one of the five suggested destinations.
5. **Itinerary Creation**: The system generates a daily plan for the chosen destination.
6. **Visualization**: The system creates images representing the trip, using DALL-E API, based on the generated itinerary.

### Running the Application

1. **Navigate to the project directory**:
   ```bash
   cd trip_planner
   ```
   
2. **Start the backend server**:
   ```bash
   uvicorn main:app --reload
   ```

3. **Start the frontend development server**:
   ```bash
   npm run dev
   ```
