import requests
API_KEY = "AIzaSyAU6gzb9h1h4Xl8ji8lqY0wPi6_H3BSlcE"

def distance(fr: tuple, to: tuple):
    start = f"{fr[1]},{fr[0]}"
    end= f"{to[1]},{to[0]}"
    GOOGLE_API_ENDPOINT = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={API_KEY}"
    response = requests.get(GOOGLE_API_ENDPOINT)
    data = response.json()
    travel_time = data['routes'][0]['legs'][0]['duration']['text'] 
    print(f"The estimated travel time by car is: {travel_time}")

    return travel_time




