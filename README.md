# Delivery Route Optimizer Discord Bot

A Discord bot that optimizes delivery routes by handling both image uploads and text inputs for addresses. It utilizes OCR to extract addresses from images, validates them using the Google Geocoding API, and calculates the most efficient delivery route. Additionally, it assesses profitability based on distance, time, and tip amounts.

## Features

- **Dual Input Handling:** Supports both image uploads and direct text inputs for delivery addresses.
- **OCR Integration:** Extracts text from images using Tesseract OCR.
- **Address Validation:** Geocodes addresses via Google Maps Geocoding API.
- **Route Optimization:** Determines the most efficient route using Google Maps Directions API.
- **Profitability Calculation:** Evaluates if the delivery route is profitable based on various factors.

## Prerequisites

- **Python 3.8+**
- **Tesseract OCR:** Installed and added to your system `PATH`.
  - [Installation Guide](https://github.com/tesseract-ocr/tesseract#installing-tesseract)
- **Google Maps API Key:** Enabled for Geocoding and Directions APIs.
- **Discord Bot Token:** Created via the [Discord Developer Portal](https://discord.com/developers/applications).

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/delivery-route-optimizer.git
    cd delivery-route-optimizer
    ```

2. **Set Up Virtual Environment (Optional but Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Unix or MacOS
    venv\Scripts\activate     # On Windows
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *If `requirements.txt` is not available:*
    ```bash
    pip install discord.py pytesseract Pillow googlemaps python-dotenv
    ```

4. **Configure Environment Variables:**
    - Create a `.env` file in the project root:
        ```
        DISCORD_BOT_TOKEN=your_discord_bot_token
        GOOGLE_MAPS_API_KEY=your_google_maps_api_key
        CENTRAL_LOCATION=your_central_location_address
        ```
    - Ensure `.env` is added to `.gitignore` to keep credentials secure.

## Usage

1. **Run the Bot:**
    ```bash
    python delivery_bot.py
    ```
    - **Expected Output:**
        ```
        Logged in as Delivery Bot - 123456789012345678
        ```

2. **Interact via Discord:**
    - **Command:** `!go`
      - **With Image:**
        ```
        !go
        [Attach Image Containing Addresses]
        ```
        - The bot processes the image, extracts addresses, prompts for tips, and returns the optimized route with profitability.
      - **Without Image:**
        ```
        !go
        ```
        - The bot prompts you to enter addresses line by line, then proceeds similarly.

## Functionality Overview

- **OCR Processing (`perform_ocr`):** Extracts text from uploaded images using Tesseract OCR.
- **Address Extraction (`extract_addresses`):** Uses regex to parse valid addresses from extracted text.
- **Validation (`validate_addresses`):** Geocodes addresses to obtain latitude and longitude.
- **Route Optimization (`get_optimized_route`):** Utilizes Google Maps Directions API to compute the most efficient route.
- **Profitability Calculation (`calculate_profitability_camry`):** Determines profitability based on distance, time, and tips.

## Troubleshooting

- **Tesseract Not Found:**
  - Ensure Tesseract OCR is installed and the path is correctly set in the script.
- **Invalid Addresses:**
  - Verify that addresses are in the correct format and within the supported cities.
- **Google Maps API Issues:**
  - Check API key validity and ensure necessary APIs are enabled.
- **Bot Unresponsive:**
  - Confirm that the bot is running without errors and that the Discord token is correct.

## Contributing

Contributions are welcome! Follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch:**
    ```bash
    git checkout -b feature/YourFeatureName
    ```
3. **Commit Your Changes:**
    ```bash
    git commit -m "Add Your Feature"
    ```
4. **Push to the Branch:**
    ```bash
    git push origin feature/YourFeatureName
    ```
5. **Open a Pull Request**

## License

MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [discord.py](https://discordpy.readthedocs.io/) - Discord API wrapper for Python.
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Open-source OCR engine.
- [Google Maps APIs](https://developers.google.com/maps) - Geocoding and Directions APIs.
- [Python-dotenv](https://github.com/theskumar/python-dotenv) - Loads environment variables from `.env` file.
