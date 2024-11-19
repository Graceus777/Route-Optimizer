import os
import re
import pytesseract
from PIL import Image
import discord
from discord.ext import commands
import asyncio
import googlemaps
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Your Discord bot token
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')  # Your Google Maps API key
CENTRAL_LOCATION = os.getenv('CENTRAL_LOCATION')  # Your central location address

# Optional: Set Tesseract command path (if not in PATH)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# Initialize Discord Bot
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
bot = commands.Bot(command_prefix='!', intents=intents)

# Updated Regex pattern to handle unit numbers
ADDRESS_PATTERN = r"(\d{1,5} [A-Za-z0-9 .,-]+(?:\s*(?:#|Apt|Apartment|Suite)\s*\d+)?, (?:Madison|Verona|Fitchburg))"

# Function to perform OCR on an image
def perform_ocr(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    image = image.convert('RGB')  # Ensure image is in RGB mode
    text = pytesseract.image_to_string(image)
    return text

# Function to extract addresses using regex
def extract_addresses(text):
    matches = re.findall(ADDRESS_PATTERN, text)
    # Clean addresses
    cleaned_addresses = [match.replace("?", "").strip() for match in matches]
    return cleaned_addresses

# Function to validate addresses using Google Geocoding API
def validate_addresses(addresses):
    validated = []
    for addr in addresses:
        geocode_result = gmaps.geocode(addr)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            validated.append({
                'address': addr,
                'lat': location['lat'],
                'lng': location['lng']
            })
    return validated

# Function to get optimized route
def get_optimized_route(central_lat, central_lng, geocoded_addresses):
    waypoints = "|".join([f"{addr['lat']},{addr['lng']}" for addr in geocoded_addresses])
    directions_result = gmaps.directions(
        origin=(central_lat, central_lng),
        destination=(central_lat, central_lng),
        waypoints=f"optimize:true|{waypoints}",
        mode="driving",
        departure_time="now"
    )
    return directions_result

# Function to calculate profitability
def calculate_profitability_camry(total_distance, time_taken_minutes, tip_amounts):
    compensation_per_delivery = 2  # Dollars
    mpg = 32
    gas_price = 2.85  # Dollars per gallon
    wear_and_tear_rate = 0.05  # Dollars per mile
    time_cost_per_hour = 4  # Dollars per hour

    gasoline_cost = (total_distance / mpg) * gas_price if mpg else 0
    wear_and_tear_cost = total_distance * wear_and_tear_rate
    time_cost = (time_taken_minutes / 60) * time_cost_per_hour
    total_earnings = compensation_per_delivery * len(tip_amounts) + sum(tip for tip in tip_amounts)
    total_cost = gasoline_cost + wear_and_tear_cost + time_cost
    profitability = total_earnings - total_cost

    if profitability > 0:
        return f"Worth it. **Profit:** ${profitability:.2f}"
    else:
        return f"Not worth it. **Loss:** ${abs(profitability):.2f}"

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

# Command: !go
@bot.command(name='go')
async def go(ctx):
    addresses = []
    
    # Check if there's an attachment
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff']):
            await ctx.send("Processing image... Please wait.")

            try:
                # Download image
                image_bytes = await attachment.read()

                # Perform OCR
                extracted_text = perform_ocr(image_bytes)
                print(f"OCR Extracted Text:\n{extracted_text}")

                # Extract addresses
                addresses = extract_addresses(extracted_text)
                if not addresses:
                    await ctx.send("No valid addresses found in the image.")
                    return

                await ctx.send(f"**Extracted Addresses:**\n" + "\n".join(addresses))

            except Exception as e:
                print(f"Error: {e}")
                await ctx.send(f"An error occurred while processing the image: {str(e)}")
                return
    else:
        # No attachment; assume user will type addresses
        await ctx.send("Please enter the delivery addresses, each on a new line:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for('message', check=check, timeout=120.0)  # Wait for 2 minutes
            input_text = msg.content
            print(f"User Input Addresses:\n{input_text}")

            # Split addresses by newlines only
            addresses = input_text.strip().split('\n')
            addresses = [addr.strip() for addr in addresses if addr.strip()]

            if not addresses:
                await ctx.send("No valid addresses were provided.")
                return

            await ctx.send(f"**Provided Addresses:**\n" + "\n".join(addresses))

        except asyncio.TimeoutError:
            await ctx.send("Timed out waiting for addresses. Please try the command again.")
            return
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send(f"An error occurred while processing the addresses: {str(e)}")
            return

    # Proceed with validation and optimization
    try:
        if not addresses:
            await ctx.send("No addresses to process.")
            return

        # Validate addresses
        validated = validate_addresses(addresses)
        if not validated:
            await ctx.send("None of the provided addresses could be validated.")
            return

        # Geocode central location
        central_geocode = gmaps.geocode(CENTRAL_LOCATION)
        if not central_geocode:
            await ctx.send("Central location could not be geocoded. Please check the CENTRAL_LOCATION configuration.")
            return
        central_lat = central_geocode[0]['geometry']['location']['lat']
        central_lng = central_geocode[0]['geometry']['location']['lng']

        # Optimize route
        directions = get_optimized_route(central_lat, central_lng, validated)
        if not directions:
            await ctx.send("Could not retrieve directions from Google Maps API.")
            return

        route = directions[0]
        waypoint_order = route['waypoint_order']
        optimized_addresses = [validated[i]['address'] for i in waypoint_order]

        # Calculate total distance and duration
        total_distance = sum(leg['distance']['value'] for leg in route['legs']) / 1609.34  # meters to miles
        total_duration = sum(leg['duration']['value'] for leg in route['legs']) / 60  # seconds to minutes

        # Prompt user for tips
        tips = []
        for addr in optimized_addresses:
            await ctx.send(f"Enter tip amount for **{addr}** (in USD):")
            def tip_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and re.match(r'^\d+(\.\d{1,2})?$', m.content)
            try:
                tip_msg = await bot.wait_for('message', check=tip_check, timeout=60.0)
                tip = float(tip_msg.content)
                tips.append(tip)
            except asyncio.TimeoutError:
                await ctx.send("Timed out waiting for tip amount. Assuming $0 tip.")
                tips.append(0.0)
            except ValueError:
                await ctx.send("Invalid input. Assuming $0 tip.")
                tips.append(0.0)

        # Calculate profitability
        profitability = calculate_profitability_camry(total_distance, total_duration, tips)

        # Prepare optimized route message
        route_message = "**Optimized Route:**\n"
        route_message += " ➡️ ".join([CENTRAL_LOCATION] + optimized_addresses + [CENTRAL_LOCATION])

        # Send results
        result_message = (
            f"{route_message}\n\n"
            f"**Total Distance:** {total_distance:.2f} miles\n"
            f"**Total Duration:** {total_duration:.2f} minutes\n"
            f"**Profitability:** {profitability}"
        )

        await ctx.send(result_message)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"An error occurred while processing the delivery data: {str(e)}")


# Run the bot
bot.run(DISCORD_BOT_TOKEN)
