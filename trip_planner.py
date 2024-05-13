import requests
from datetime import datetime
from serpapi import GoogleSearch

OPENAI_API_KEY = "sk-proj-qBbquYjeeRcbwcs8C1IHT3BlbkFJLZHyfNMDcKE3xW9wWaNr"
SERPAPI_API_KEY = "1d6a5130ff1de9d0d819c13cb83d8b5b3a7edd233c912f6065052cbeceb6b1b6"
SEARCH_PROMPT = "suggest 5 places to visit in the month: {month} and for the trip type: {trip_type}. return only the locations without further information and give them in a list format."

def get_trip_suggestions(month, trip_type):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": SEARCH_PROMPT.format(month=month, trip_type=trip_type),
                },
            ],
        },
    )
    return response.json()

def search_flights(destination):
    response = requests.get(
        "https://api.serphouse.com/serp/live",
        headers={"Authorization": "Bearer ${API_KEY}"},
        params={"q": f"flights from Tel Aviv to {destination}", "source": "google", "device": "desktop"})
    flights = response.json().get('flights', [])
    return min(flights, key=lambda x: x['price']) if flights else None

def plan_trip():
    start_date = input("Enter the start date of your trip (DD/MM/YYYY): ")
    end_date = input("Enter the end date of your trip (DD/MM/YYYY): ")
    budget = float(input("Enter your total budget in USD: "))
    trip_type = input("Enter the type of trip (ski/beach/city): ")

    day = datetime.strptime(start_date, "%d/%m/%Y").strftime("%d")
    month = datetime.strptime(start_date, "%d/%m/%Y").strftime("%B")
    year = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y")

    suggestions = get_trip_suggestions(month, trip_type)
    destinations = suggestions['choices'][0]['message']['content']

    for destination in destinations:
        print(destination)
        flight_info = search_flights(destination)
        if flight_info:
            print(f"Cheapest flight to {destination}: {flight_info['price']} USD")

if __name__ == "__main__":
    plan_trip()