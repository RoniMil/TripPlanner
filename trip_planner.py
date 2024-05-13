import requests
from datetime import datetime

OPENAI_API_KEY = "sk-proj-qBbquYjeeRcbwcs8C1IHT3BlbkFJLZHyfNMDcKE3xW9wWaNr"
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


def plan_trip():
    start_date = input("Enter the start date of your trip (YYYY-MM-DD): ")
    end_date = input("Enter the end date of your trip (YYYY-MM-DD): ")
    budget = float(input("Enter your total budget in USD: "))
    trip_type = input("Enter the type of trip (ski/beach/city): ")

    month = datetime.strptime(start_date, "%Y-%m-%d").strftime("%B")
    suggestions = get_trip_suggestions(month, trip_type)
    destinations = suggestions['choices'][0]['message']['content']



if __name__ == "__main__":
    plan_trip()