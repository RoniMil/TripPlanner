import requests
from datetime import datetime

OPENAI_API_KEY = "sk-proj-qBbquYjeeRcbwcs8C1IHT3BlbkFJLZHyfNMDcKE3xW9wWaNr"
SERPAPI_API_KEY = "1d6a5130ff1de9d0d819c13cb83d8b5b3a7edd233c912f6065052cbeceb6b1b6"
SEARCH_PROMPT = "suggest 5 places to visit in the month: {month} and for the trip type: {trip_type}. return only the location without further information in the following format: \"PLACE1\nPLACE2\nPLACE3\nPLACE4\nPLACE5\""
AIRPORT_PROMPT = 'Give me the international airport codes for {location}. RETURN ONLY THE CODES AND NOTHING ELSE'



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
    return response.json()["choices"][0]["message"]["content"]


def search_airports(locations):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": AIRPORT_PROMPT.format(location=locations),
                },
            ],
        },
    )
    return response.json()["choices"][0]["message"]["content"]


def search_flights(airports, outbound_date, return_date, max_price):
    response = requests.get(
        "https://serpapi.com/search?engine=google_flights",
        params={"outbound_date": outbound_date, "return_date": return_date, "max_price": max_price, "departure_id": "TLV", "arrival_id": airports,"api_key": SERPAPI_API_KEY},
    )
    res = response.json()
    best_flights = res.get("best_flights", [])
    other_flights = res.get("other_flights", [])
    flights = best_flights + other_flights
    return min(flights, key=lambda x: x["price"]) if flights else None


def plan_trip(debug=False):
    if debug: 
        start_date = "2024-06-10"
        end_date = "2024-06-24"
        budget = "2000"
        trip_type = "beach"
    else:    
        start_date = input("Enter the start date of your trip (YYYY-MM-DD): ")
        end_date = input("Enter the end date of your trip (YYYY-MM-DD): ")
        budget = float(input("Enter your total budget in USD: "))
        trip_type = input("Enter the type of trip (ski/beach/city): ")

    #day = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d")
    month = datetime.strptime(start_date, "%Y-%m-%d").strftime("%B")
    #year = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y")

    outbound_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    return_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    destinations = get_trip_suggestions(month, trip_type).split('\n')

    for destination in destinations:
        airports = search_airports(destination)
        print(destination)
        flight_info = search_flights(airports, outbound_date, return_date, budget)
        if flight_info:
            print(f"Cheapest flight to {destination}: {flight_info['price']} USD")    




if __name__ == "__main__":
    plan_trip(debug = True)
