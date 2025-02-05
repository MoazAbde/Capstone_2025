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


def load_weather_data():
    """
    TO-DO: Use weather API to get data 
    """
    return None

def generation_data():
    """
    TO-DO: get generation data from every sub-station 
    """
    return None

def pricing_data():
    """
    TO-DO: get pricing data from an API
    """
    return None

def load_demand_data():
    """
    TO-DO: get load demand data from an API
    """
    return None

