# Delivery Route Optimizer

This project is a **Delivery Route Optimizer** application built using **Bottle** for backend services and **Streamlit** for an interactive web-based frontend. The application calculates an optimized delivery route using the Google Maps API and provides profitability information based on a specific cost model.

## Features

- Geocodes delivery addresses using Google Maps API.
- Calculates an optimized route that returns to a central location.
- Computes total distance, duration, and profitability for delivery routes.
- Allows users to input multiple delivery addresses and corresponding tip amounts.
- Includes a basic cost model tailored for a **2021 Toyota Camry**.

## Cost Model

The profitability model is designed around the following parameters:

- **Delivery Vehicle**: 2021 Toyota Camry
- **Compensation Per Delivery**: $2.00
- **Gas Mileage**: 32 miles per gallon
- **Gas Price**: $2.85 per gallon
- **Wear and Tear Cost**: $0.05 per mile
- **Driver's On-Road Time Cost**: $4.00 per hour (representing opportunity cost for drivers)
- **Tip Input**: User-defined for each delivery address

## Getting Started

### Prerequisites

Before running the project, you will need to install the following Python packages:

```bash
pip install bottle streamlit requests
```

Setting Up
Google Maps API Key: You will need to obtain a Google Maps API Key from the Google Cloud Platform. After generating your key, update it in both script files:

```python
API_KEY = 'YOUR_API_KEY_HERE'
```
Central Location: Set your central location in both script files. This is the address from where your deliveries start and end:

```python
CENTRAL_LOCATION = "YOUR_CENTRAL_LOCATION"
```
Run the Bottle Backend Server:

```bash
python distance.py
```
This will start the server on localhost:8080.

Run the Streamlit Frontend:

```bash
streamlit run address_selector.py
```
This will open an interactive UI in your web browser, where you can enter delivery addresses and calculate the optimized route.

## How to Use
Enter Delivery Addresses: In the UI, specify the number of delivery addresses and input each address in the respective fields.
Enter Tips: Enter the tip amount for each address.
Optimize Route: Click the "Optimize Route" button to calculate the route, total distance, duration, and profitability.
## Profitability Calculation
The profitability calculation considers the following factors:

Gasoline Cost: Based on the total distance and gas price.
Wear and Tear Cost: Based on the total distance at $0.05 per mile.
Time Cost: Based on the time taken and an hourly opportunity cost of $4.00.
Earnings: Flat $2.00 delivery compensation plus tips per address.

## Example API Request (For Advanced Users)
To test the API directly, you can use a cURL command:

```bash
curl -X POST http://localhost:8080/optimize_route \
    -H "Content-Type: application/json" \
    -d '{"central_location": "YOUR_CENTRAL_LOCATION", "delivery_addresses": ["123 Main St, City, State", "456 Oak St, City, State"], "tip_amounts": [5, 3]}'
```
## Notes
The code has built-in error handling for invalid addresses that cannot be geocoded.
Ensure that all inputs are correctly formatted and that the API key and central location are properly set.
The app assumes that the delivery route always starts and ends at the central location.

## Acknowledgments
Google Maps Platform for providing the geocoding and directions API services.
Streamlit and Bottle for enabling a straightforward and interactive web application setup.
