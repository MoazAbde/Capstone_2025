import network
import load_input_data
import config_network
import equity_score

def get_region_buses(n, region_list):
    return n.buses[
        (
            n.buses.country.isin(region_list) #checks to see if the bus is in the region list that we need
            | n.buses.reeds_state.isin(region_list) #
            | n.buses.interconnect.str.lower().isin(region_list) #
            | n.buses.nerc_reg.isin(region_list) #
            | (1 if "all" in region_list else 0)
        )
    ]
