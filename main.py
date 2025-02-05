import network
from load_input_data import process_city_coordinates
import config_network
import equity_score

def get_region_buses(n, region_list):
    return n.buses[
        (
            n.buses.country.isin(region_list) #checks to see if the bus is in the region list that we need
            | n.buses.read_state.isin(region_list) #reads the state of the bus
            | n.buses.interconnect.str.lower().isin(region_list) #no idea
            | n.buses.AESO_reg.isin(region_list) #
            | (1 if "all" in region_list else 0)
        )
    ]


# Example usage:
if __name__ == "__main__":
    API_KEY = "6fcc0a2663778d91c4c12f8fb070742f"  #API Key
    process_city_coordinates("city.json", "city_coordinates.json", API_KEY)