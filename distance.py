from bottle import Bottle, request, run, response
import requests
import json

app = Bottle()

# Google Maps API Key
API_KEY = ''  # <-- Replace with your actual API key

# Central location (fixed as per user's requirement)
CENTRAL_LOCATION = ""

# Function to get latitude and longitude using Google Maps API
def geocode_address(address):
    params = {
        'address': address,
        'key': API_KEY
    }
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None

# Function to get optimized route using Google Maps Directions API
def get_optimized_route(central_lat, central_lng, geocoded_addresses):
    waypoints = "|".join([f"{addr['lat']},{addr['lng']}" for addr in geocoded_addresses])
    params = {
        'origin': f"{central_lat},{central_lng}",
        'destination': f"{central_lat},{central_lng}",  # Return to the central location
        'waypoints': f"optimize:true|{waypoints}",
        'key': API_KEY
    }

    response = requests.get('https://maps.googleapis.com/maps/api/directions/json', params=params)
    if response.status_code == 200:
        return response.json()
    return None

# Function to calculate profitability using the Camry model
def calculate_profitability_camry(total_distance, time_taken_minutes, tip_amounts):
    compensation_per_delivery = 2
    mpg = 32
    gas_price = 2.85
    wear_and_tear_rate = 0.05
    time_cost_per_hour = 4

    gasoline_cost = ((total_distance or 0) / mpg) * gas_price if mpg else 0
    wear_and_tear_cost = (total_distance or 0) * wear_and_tear_rate
    time_cost = ((time_taken_minutes or 0) / 60) * time_cost_per_hour
    total_earnings = compensation_per_delivery + sum(tip if tip is not None else 0 for tip in tip_amounts)
    total_cost = gasoline_cost + wear_and_tear_cost + time_cost
    profitability = total_earnings - total_cost

    return f"Worth it. Profit: ${profitability:.2f}" if profitability > 0 else f"Not worth it. Loss: ${abs(profitability):.2f}"

# Route to get optimized route and profitability data
@app.route('/optimize_route', method='POST')
def optimize_route():
    try:
        data = request.json
        central_location = data.get('central_location', CENTRAL_LOCATION)
        delivery_addresses = data.get('delivery_addresses')
        tip_amounts = data.get('tip_amounts', [])

        if not delivery_addresses or not isinstance(tip_amounts, list):
            raise ValueError("Invalid addresses or tip amounts")

        tip_amounts = [tip if tip is not None else 0 for tip in tip_amounts]

        geocoded_addresses = []
        for address in delivery_addresses:
            lat, lng = geocode_address(address)
            if lat and lng:
                geocoded_addresses.append({"address": address, "lat": lat, "lng": lng})
            else:
                response.status = 400
                return {"error": f"Could not geocode address: {address}"}

        central_lat, central_lng = geocode_address(central_location)
        route_response = get_optimized_route(central_lat, central_lng, geocoded_addresses)
        if route_response:
            total_distance = sum(leg["distance"]["value"] for leg in route_response["routes"][0]["legs"]) / 1609.34
            total_duration = sum(leg["duration"]["value"] for leg in route_response["routes"][0]["legs"]) / 60
            optimized_order = route_response["routes"][0]["waypoint_order"]
            optimized_addresses = [delivery_addresses[i] for i in optimized_order]

            result = calculate_profitability_camry(total_distance, total_duration, tip_amounts)

            return {
                "central_location": central_location,
                "geocoded_addresses": geocoded_addresses,
                "optimized_route": optimized_addresses,
                "total_distance": round(total_distance, 2),
                "total_duration": round(total_duration, 2),
                "profitability": result
            }
        else:
            raise ValueError("Failed to retrieve route data")
    except Exception as e:
        response.status = 500
        return str(e)

# Run the Bottle app
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)
