import requests
from datetime import datetime

OPENAI_API_KEY = "sk-proj-qBbquYjeeRcbwcs8C1IHT3BlbkFJLZHyfNMDcKE3xW9wWaNr"
SERPAPI_API_KEY = "1d6a5130ff1de9d0d819c13cb83d8b5b3a7edd233c912f6065052cbeceb6b1b6"
SEARCH_PROMPT = "suggest me a place to visit in the month: {month} and for the trip type: {trip_type}. return only the location AS A STRING without further information. THE PLACE MUST NOT BE IN THE FOLLOWING LIST: {cur_locations}"
AIRPORT_PROMPT = 'Give me the international airport codes for {location}. RETURN ONLY THE CODES AND NOTHING ELSE'


# calls on chatGPT to get a trip destination for the given month and trip type. also prevents it from returning a destination already added.
def get_trip_suggestion(cur_locations, month, trip_type):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": SEARCH_PROMPT.format(cur_locations=cur_locations, month=month, trip_type=trip_type),
                },
            ],
        },
    )
    return response.json()["choices"][0]["message"]["content"]

# returns a list of relevant airports for the destination locations for use in google flights search
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

# searches google flights for flights from the given airports (of the found destinations) on the given trip dates whose total round trip time is leq than the given max_price argument.
# returns the cheapest option
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

# this function calls on the api search while there are less than 5 valid destinations
def get_valid_destinations(month, trip_type, outbound_date, return_date, budget):
    seen_destinations = []
    destinations = {}

    # continues search while there are less than 5 destinations fitting the search parameters
    while len(destinations) < 5:
        destination = get_trip_suggestion(seen_destinations, month, trip_type)
        seen_destinations.append(destination)
        airports = search_airports(destination)
        flight_info = search_flights(airports, outbound_date, return_date, budget)
        if flight_info:
            print(f"Cheapest flight to {destination}: {flight_info['price']} USD") 
            destinations[destination] = flight_info  

    return destinations          


# this function asks the user for the trip parameters and performs the search. retrieves the destinations the are within trip parameters
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

    month = datetime.strptime(start_date, "%Y-%m-%d").strftime("%B")

    outbound_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    return_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    destinations = get_valid_destinations(month, trip_type, outbound_date, return_date, budget)

    print(destinations)          


if __name__ == "__main__":
    plan_trip(debug = True)
