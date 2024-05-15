import requests
from datetime import datetime
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# start api
app = FastAPI()

origins = [
    "http://localhost:3000",  # The origin of your Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

OPENAI_API_KEY = "sk-proj-qBbquYjeeRcbwcs8C1IHT3BlbkFJLZHyfNMDcKE3xW9wWaNr"
SERPAPI_API_KEY = "34c3808175a1ca8a9306b7da739366e293f1f08f4c591329551edf8bc353f8c7"
SEARCH_PROMPT = "suggest me a place to visit in the month: {month} and for the trip type: {trip_type}. return only the location AS A STRING without further information. THE PLACE MUST NOT BE IN THE FOLLOWING LIST: {cur_locations}"
AIRPORT_PROMPT = "Give me the international airport codes for {location}. RETURN ONLY THE CODES AND NOTHING ELSE"


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
                    "content": SEARCH_PROMPT.format(
                        cur_locations=cur_locations, month=month, trip_type=trip_type
                    ),
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
        params={
            "outbound_date": outbound_date,
            "return_date": return_date,
            "max_price": max_price,
            "departure_id": "TLV",
            "arrival_id": airports,
            "api_key": SERPAPI_API_KEY,
        },
    )
    res = response.json()
    best_flights = res.get("best_flights", [])
    other_flights = res.get("other_flights", [])
    flights = best_flights + other_flights
    # filter only flights that have a price attribute
    flights = list(filter(lambda d: "price" in d, flights))
    # return min price flight
    return min(flights, key=lambda x: x["price"]) if flights else None

# searches google hotels for a hotel in the given destination on the given trip dates. the price per night is leq than max_price argument.
# returns the most expensive option
def search_hotels(destination, check_in_date, check_out_date, max_price):
    response = requests.get(
        "https://serpapi.com/search?engine=google_hotels",
        params={
            "q": destination,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "max_price": max_price,
            "api_key": SERPAPI_API_KEY,
        },
    )
    res = response.json()
    properties = res.get("properties", [])
    return (
        max(properties, key=lambda x: x["total_rate"]["lowest"]) if properties else None
    )

# this function retrieves valid trips according to given parameters
def get_valid_trips(
    month, trip_type, outbound_date_str, return_date_str, total_days, budget
):
    # list of destinations already given as query
    seen_destinations = []
    # list of returned trips
    trips = {}

    # continues search while there are less than 5 trips fitting the search parameters
    while len(trips) < 1:
        destination = get_trip_suggestion(seen_destinations, month, trip_type)
        seen_destinations.append(destination)
        airports = search_airports(destination)
        flight_info = search_flights(
            airports, outbound_date_str, return_date_str, budget
        )
        # found flights fitting the destination returned by query
        if flight_info:
            max_price_per_night = int(
                (int(budget) - int(flight_info["price"])) / total_days
            )
            hotel_info = search_hotels(
                destination, outbound_date_str, return_date_str, max_price_per_night
            )
            # found hotel fitting the destination returned by query
            if hotel_info:
                trips[destination] = (
                    flight_info["flights"],
                    hotel_info,
                    int(flight_info["price"])
                    + int(re.sub(r"[^\d]", "", hotel_info["total_rate"]["lowest"])),
                )

    return trips


# this function asks the user for the trip parameters and performs the search. retrieves the destinations the are within trip parameters
# call for example http://127.0.0.1:8000/?start_date=1&end_date=2&budget=3&trip_type=4
@app.get("/")
def plan_trip(start_date: str, end_date: str, budget: str, trip_type: str):
    debug = False

    month = datetime.strptime(start_date, "%Y-%m-%d").strftime("%B")

    outbound_date = datetime.strptime(start_date, "%Y-%m-%d")
    return_date = datetime.strptime(end_date, "%Y-%m-%d")

    outbound_date_str = outbound_date.strftime("%Y-%m-%d")
    return_date_str = return_date.strftime("%Y-%m-%d")

    total_days = (return_date - outbound_date).days

    if debug:
        trips = {
            "Barcelona": ("Flight 101", "Quack Inn", 1500),
            "New York": ("Flight 202", "Duck Pond Resort", 1800),
            "Rome": ("Flight 303", "Feather Nest Hotel", 1999),
            "Paris": ("Flight 404", "Mallard Mansion", 1750),
            "Los Angeles": ("Flight 505", "Beak Boulevard Suites", 1600),
        }
    else:
        trips = get_valid_trips(
            month, trip_type, outbound_date_str, return_date_str, total_days, budget
        )
    return trips
