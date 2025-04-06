import requests
import json

def process_city_coordinates(input_file, output_file, api_key, province="AB", country="Canada"):
    """
    Reads a JSON file of cities, fetches their coordinates from the OpenWeatherMap API,
    and writes the coordinates to another JSON file.

    Args:
        input_file (str): Path to the input JSON file containing a key "cities" with a list of city names.
        output_file (str): Path to the output JSON file where the results will be saved.
        api_key (str): Your OpenWeatherMap API key.
        province (str, optional): Province or state code. Defaults to "AB".
        country (str, optional): Country name. Defaults to "Canada".
    """
    # Load the list of cities from the input JSON file
    try:
        with open(input_file, "r") as infile:
            data = json.load(infile)
            cities = data.get("cities", [])
            if not cities:
                print(f"No cities found in {input_file}.")
                return
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return

    # List to hold the coordinate data for each city
    coordinates_list = []

    # Process each city
    for city in cities:
        # Build the API URL for the given city
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{province},{country}&appid={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Take the first result as the most relevant one
                    lat = data[0].get("lat")
                    lon = data[0].get("lon")
                    coordinates_list.append({
                        "city": city,
                        "latitude": lat,
                        "longitude": lon
                    })
                else:
                    print(f"No coordinate data returned for {city}")
            else:
                print(f"Error fetching data for {city}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Exception occurred for {city}: {e}")

    # Write the coordinates to the output JSON file
    try:
        with open(output_file, "w") as outfile:
            json.dump(coordinates_list, outfile, indent=2)
        print(f"City coordinates saved to {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")



def load_weather_data(coordinates_file, api_key):
    """
    Reads the city coordinates from a JSON file, fetches the historical weather data for each city,
    and saves each city's weather history to a separate JSON file named <cityname>.json.
    
    The input JSON file should contain a list of dictionaries with keys:
      - "city": the name of the city
      - "latitude": the city's latitude
      - "longitude": the city's longitude

    Args:
        coordinates_file (str): Path to the JSON file containing city coordinates.
        api_key (str): Your OpenWeatherMap API key.
    """
    # Load city coordinates from the JSON file.
    try:
        with open(coordinates_file, "r") as f:
            city_list = json.load(f)
    except Exception as e:
        print(f"Error reading {coordinates_file}: {e}")
        return

    # Loop through each city in the list.
    for city_entry in city_list:
        city_name = city_entry.get("city")
        lat = city_entry.get("latitude")
        lon = city_entry.get("longitude")
        
        # Validate that we have all the necessary data.
        if not city_name or lat is None or lon is None:
            print(f"Skipping invalid entry: {city_entry}")
            continue

        # Build the URL for the historical weather data.
        # This endpoint returns aggregated historical data for the last 365 days.
        history_url = (
            f"https://history.openweathermap.org/data/2.5/aggregated/year?"
            f"lat={lat}&lon={lon}&appid={api_key}"
        )
        print(f"Fetching weather history for {city_name} using URL:\n{history_url}")

        # Send the GET request to the API.
        try:
            response = requests.get(history_url)
            if response.status_code == 200:
                weather_history = response.json()

                # Create a safe file name (e.g., "Edmonton" -> "edmonton.json").
                safe_city_name = city_name.replace(" ", "_").lower()
                output_filename = f"{safe_city_name}.json"

                # Save the weather data to the file.
                with open(output_filename, "w") as outfile:
                    json.dump(weather_history, outfile, indent=4)
                print(f"Weather history for {city_name} saved to '{output_filename}'.\n")
            else:
                print(f"Error fetching data for {city_name}: HTTP {response.status_code} - {response.text}\n")
        except Exception as e:
            print(f"Exception occurred while fetching data for {city_name}: {e}\n")




