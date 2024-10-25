import streamlit as st
import requests

# Google Maps API Key (Replace with your actual API key)
API_KEY = ''

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

# Set up the Streamlit interface
st.title("Delivery Route Optimizer")

# Input for delivery addresses
st.header("Enter Delivery Addresses")
address_count = st.number_input("Number of delivery addresses", min_value=1, max_value=10, value=3)

addresses = []
for i in range(address_count):
    address = st.text_input(f"Address {i + 1}")
    addresses.append(address)

# Input for tips for each delivery
st.header("Enter Tip Amounts for Each Address")
tips = []
for i in range(address_count):
    tip = st.number_input(f"Tip Amount for Address {i + 1}", min_value=0.0, step=0.5)
    tips.append(tip)

# Button to optimize route
if st.button("Optimize Route"):
    geocoded_addresses = []
    try:
        # Geocode the addresses
        for address in addresses:
            lat, lng = geocode_address(address)
            if lat and lng:
                geocoded_addresses.append({"address": address, "lat": lat, "lng": lng})
            else:
                st.error(f"Could not geocode address: {address}")

        # Calculate the total distance and duration considering the return to central location
        if geocoded_addresses:
            # Define the central location coordinates
            central_lat, central_lng = geocode_address(CENTRAL_LOCATION)

            # Add central location as the final destination
            geocoded_addresses.append({"address": CENTRAL_LOCATION, "lat": central_lat, "lng": central_lng})

            # Send the request to the local running server to optimize route and calculate profitability
            url = 'http://localhost:8080/optimize_route'
            payload = {
                "central_location": CENTRAL_LOCATION,
                "delivery_addresses": [addr['address'] for addr in geocoded_addresses[:-1]],  # Don't include central location twice in the waypoints
                "tip_amounts": tips
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                result = response.json()
                st.header("Optimized Route Results")
                st.write(f"Central Location: {result['central_location']}")
                st.write(f"Optimized Route: {result['optimized_route']}")
                st.write(f"Total Distance: {result['total_distance']} miles")
                st.write(f"Total Duration: {result['total_duration']} minutes")
                st.write(f"Profitability: {result['profitability']}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
