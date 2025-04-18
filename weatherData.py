from load_input_data import process_city_coordinates
from load_input_data import load_weather_data



# Example usage:
if __name__ == "__main__":
    
    API_KEY = "6fcc0a2663778d91c4c12f8fb070742f"  #API Key
    
    # Get city coord and save it in a json file
    process_city_coordinates("city.json", "city_coordinates.json", API_KEY)
    
    coordinates_file = "city_coordinates.json"    # The JSON file with city coordinates.
    
    # Gets 365 days of weather history for each city, uncomment and run once
    # will return a json file for each city and it's weather data
    #load_weather_data(coordinates_file, API_KEY) 