import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import networkx
import linopy
import pypsa
import xlrd
import openpyxl
from pypsa.plot import add_legend_patches

#fuel costs, will be determined by AESO APIs 
fuel_cost = dict(
    bio = 8,
    gas = 100,
    oil = 48,
)

#idk if we need this
efficiency = dict(
    bio = 0.33,
    gas = 0.58,
    oil = 0.35,
)

emissions = dict(
    bio = 0.15,
    gas = 0.2,
    solar = 0,
    hydro = 0,
    wind = 0,
)

area = ["AREA13", "AREA17", "AREA18", "AREA19", "AREA20", "AREA21", "AREA22", "AREA23", "AREA24", "AREA25", 
        "AREA26", "AREA27", "AREA28", "AREA29", "AREA30", "AREA31", "AREA32", "AREA33", "AREA34", "AREA35", 
        "AREA36", "AREA37", "AREA38", "AREA39", "AREA4", "AREA40", "AREA42", "AREA43", "AREA44", "AREA45", 
        "AREA46", "AREA47", "AREA48", "AREA49", "AREA52", "AREA53", "AREA54", "AREA55", "AREA56", "AREA57", 
        "AREA6", "AREA60", "solar_percentage", "wind_percentage"]

file_path = "Data/hourly_load_data_by_area.xlsx"
df = pd.read_excel(file_path, sheet_name="Sheet1")

def get_load_matrix(df, user_date, user_time, area_list):
    datetime_str = f"{user_date} {user_time}"

    try:
        user_datetime = pd.to_datetime(datetime_str)
    except ValueError:
        return "Invalid date or time format. Please enter correctly."

    row = df[df["DT_MST"] == user_datetime]

    if row.empty:
        return "No data found for the given date and time."

    # Create a matrix (DataFrame) with areas as index and the timestamp as the column
    load_matrix = pd.DataFrame(index=area_list, columns=[user_datetime])

    for area in area_list:
        if area in df.columns:
            load_matrix.loc[area, user_datetime] = row[area].values[0]
        else:
            load_matrix.loc[area, user_datetime] = "N/A"  # Mark as N/A if area is missing

    return load_matrix


date = str(input("Enter the date in YYYY-MM-DD format: "))
time = str(input("Enter the time in HH:00:00 format: "))

load_matrix = get_load_matrix(df, date, time, area)

dg = pd.read_excel("Data/Generation Data.xlsx")

power_plants = {
    "Lloydminster": {"solar": 0, 
                     "gas": 0, 
                     "wind": 0, 
                     "bio": 0, 
                     "hydro": 0}, 
    "Rainbow_Lake" :{"solar": 0,
                     "hydro": 0, 
                     "wind": 0, 
                     "bio": 0,
                     "gas": dg["Capacity_MW"][36]},
    "High_Level" : {"solar": 0, 
                    "gas": 0, 
                    "wind": 0, 
                    "bio": 0, 
                    "hydro": 0}, 
    "Peace_River": {"solar": 0,
                    "wind": 0,
                    "hydro": 0, 
                    "gas": dg["Capacity_MW"][8] + dg["Capacity_MW"][33] + dg["Capacity_MW"][45], 
                    "bio": dg["Capacity_MW"][96]},
    "Grande_Prairie": {"solar": 0,
                       "wind": 0,
                       "hydro": 0, 
                       "gas": dg["Capacity_MW"][6] + dg["Capacity_MW"][32] + dg["Capacity_MW"][35], 
                       "bio": dg["Capacity_MW"][94] + dg["Capacity_MW"][95] + dg["Capacity_MW"][102]}, 
    "High_Prairie": {"solar": 0, 
                     "gas": 0, 
                     "wind": 0, 
                     "bio": 0, 
                     "hydro": 0}, 
    "Grande_Cache": {"solar": 0, 
                     "gas": dg["Capacity_MW"][23],
                     "wind": 0, 
                     "bio": 0, 
                     "hydro": 0}, 
    "Valleyview": {"solar": 0, 
                   "wind": 0,
                   "gas": dg["Capacity_MW"][11] + dg["Capacity_MW"][12] + dg["Capacity_MW"][25] + dg["Capacity_MW"][26] + dg["Capacity_MW"][42] + dg["Capacity_MW"][48], 
                   "hydro": dg["Capacity_MW"][52], 
                   "bio": dg["Capacity_MW"][97] + dg["Capacity_MW"][101]}, 
    "Fox_Creek": {"solar": 0, 
                  "gas": 0, 
                  "wind": 0, 
                  "bio": 0, 
                  "hydro": 0},
    "Fort_Mac": {"solar": 0, 
                 "gas": dg["Capacity_MW"][28] + dg["Capacity_MW"][31] + dg["Capacity_MW"][34],
                 "wind": 0, 
                 "bio": 0, 
                 "hydro": 0}, 
    "Swan_Hills": {"solar": 0,
                   "gas": 0, 
                   "wind": 0, 
                   "bio": dg["Capacity_MW"][103], 
                   "hydro": 0}, 
    "Athabasca": {"solar": 0, 
                  "bio": dg["Capacity_MW"][93], 
                  "gas": 0, 
                  "wind": 0,
                  "hydro": 0}, 
    "Cold_Lake": {"bio": 0,
                  "hydro": 0,  
                  "wind": 0,
                  "gas": dg["Capacity_MW"][15] + dg["Capacity_MW"][19], 
                  "solar": load_matrix.values[42,0]*(dg["Capacity_MW"][92])}, 
    "Hinton_Edson": {"solar": 0, 
                     "gas": 0, 
                     "wind": 0, 
                     "bio": 0, 
                     "hydro": 0},  
    "Drayton_Valley": {"solar": 0,
                       "gas": 0,
                       "wind": 0, 
                       "hydro": dg["Capacity_MW"][53] + dg["Capacity_MW"][54] + dg["Capacity_MW"][55] + dg["Capacity_MW"][56] + 
                       dg["Capacity_MW"][58] + dg["Capacity_MW"][60] + dg["Capacity_MW"][61] + dg["Capacity_MW"][64], 
                       "bio": dg["Capacity_MW"][98]}, 
    "Wetaskiwin": {"solar": 0, 
                    "gas": 0, 
                    "wind": 0, 
                    "bio": 0, 
                    "hydro": 0}, 
    "Wainwright": {"solar": 0, 
                    "gas": 0, 
                    "wind": 0, 
                    "bio": 0, 
                    "hydro": 0}, 
    "Fort_Sask": {"solar": 0, 
                  "gas": dg["Capacity_MW"][18] + dg["Capacity_MW"][27] + dg["Capacity_MW"][37] + dg["Capacity_MW"][38] + dg["Capacity_MW"][39], 
                  "wind": 0,
                  "bio": 0,
                  "hydro": 0}, 
    "Abraham_Lake": {"solar": 0, 
                     "gas": 0, 
                     "wind": 0, 
                     "bio": 0, 
                     "hydro": 0}, 
    "Red_Deer": {"gas": dg["Capacity_MW"][24], 
                 "solar": load_matrix.values[42,0]*(dg["Capacity_MW"][82] + dg["Capacity_MW"][84] + dg["Capacity_MW"][86] + dg["Capacity_MW"][87]), 
                 "wind": 0, 
                 "bio": 0,
                 "hydro": 0}, 
    "Alliance_Battle_River": {"solar": 0, 
                              "gas": 0, 
                              "wind": 0, 
                              "bio": 0, 
                              "hydro": 0}, 
    "Provost": {"solar": 0, 
                "gas": 0, 
                "wind": 0, 
                "bio": 0, 
                "hydro": 0}, 
    "Caroline": {"solar": 0, 
                 "gas": 0, 
                 "wind": 0, 
                 "bio": 0, 
                 "hydro": 0}, 
    "Didsbury": {"solar": 0, 
                 "gas": 0, 
                 "wind": 0, 
                 "bio": 0, 
                 "hydro": 0}, 
    "Medicine_Hat": {"hydro": 0,
                     "gas": dg["Capacity_MW"][30], 
                     "wind": load_matrix.values[43,0]*(dg["Capacity_MW"][77] + dg["Capacity_MW"][78]), 
                     "solar": load_matrix.values[42,0]*(dg["Capacity_MW"][79] + dg["Capacity_MW"][81] + dg["Capacity_MW"][89]), 
                     "bio": dg["Capacity_MW"][100]}, 
    "Wabamun": {"bio": 0,
                "wind": 0,
                "hydro": 0,
                "solar": 0, 
                "gas": dg["Capacity_MW"][43] + dg["Capacity_MW"][44]}, 
    "Hanna": {"solar": 0, 
              "gas": dg["Capacity_MW"][40],
              "bio": 0,
              "wind": 0,
              "hydro": 0,}, 
    "Sheerness": {"solar": 0, 
                  "gas": 0, 
                  "wind": 0, 
                  "bio": 0, 
                  "hydro": 0}, 
    "Seebe": {"gas": 0,
              "wind": 0,
              "bio": 0, 
              "solar": 0, 
              "hydro": dg["Capacity_MW"][49] + dg["Capacity_MW"][57] + dg["Capacity_MW"][59]}, 
    "Srathmore_Blackie": {"bio": 0, 
                          "hydro": 0,
                          "gas": dg["Capacity_MW"][4] + dg["Capacity_MW"][5] + dg["Capacity_MW"][7] + dg["Capacity_MW"][10] + 
                   dg["Capacity_MW"][13] + dg["Capacity_MW"][21] + dg["Capacity_MW"][22] + dg["Capacity_MW"][29], 
                   "wind": load_matrix.values[43,0]*(dg["Capacity_MW"][71]), 
                   "solar": load_matrix.values[42,0]*(dg["Capacity_MW"][88] + dg["Capacity_MW"][90])}, 
    "High_River": {"solar": 0, 
                    "gas": 0, 
                    "wind": 0, 
                    "bio": 0, 
                    "hydro": 0}, 
    "Brooks": {"gas": 0, 
               "bio": 0,
               "hydro": dg["Capacity_MW"][62] + dg["Capacity_MW"][63], 
               "wind": load_matrix.values[43,0]*(dg["Capacity_MW"][69] + dg["Capacity_MW"][70] + dg["Capacity_MW"][72] + dg["Capacity_MW"][73] + dg["Capacity_MW"][74] + dg["Capacity_MW"][76]), 
               "solar": load_matrix.values[42,0]*(dg["Capacity_MW"][83])}, 
    "Empress": {"solar": 0, 
                "gas": 0, 
                "wind": 0, 
                "bio": 0, 
                "hydro": 0}, 
    "Stavely": {"solar": 0, 
                "gas": 0, 
                "wind": 0, 
                "bio": 0, 
                "hydro": 0}, 
    "Vauxhall": {"solar": load_matrix.values[42,0]*(dg["Capacity_MW"][91]), 
                 "gas": 0,
                 "wind": 0,
                 "bio": 0, 
                 "hydro": 0}, 
    "Fort_Macleod": {"bio": 0, 
                     "hydro": 0,
                     "solar": 0, 
                     "gas": dg["Capacity_MW"][0], 
                     "wind": load_matrix.values[43,0]*(dg["Capacity_MW"][66] + dg["Capacity_MW"][67] + dg["Capacity_MW"][68])}, 
    "Lethbridge": {"bio": 0, 
                   "hydro": 0,
                   "gas": dg["Capacity_MW"][1] + dg["Capacity_MW"][3], 
                   "wind": load_matrix.values[43,0]*(dg["Capacity_MW"][75]), 
                   "solar": load_matrix.values[42,0]*(dg["Capacity_MW"][80])},
    "Glenwood": {"solar": 0,
                 "wind": 0,
                 "bio": 0, 
                 "gas": dg["Capacity_MW"][17], 
                 "hydro": dg["Capacity_MW"][51] + dg["Capacity_MW"][65]}, 
    "Vegreville": {"solar": 0, 
                   "gas": dg["Capacity_MW"][20], 
                   "wind": 0,
                   "bio": 0,
                   "hydro": 0}, 
    "Airdrie": {"solar": 0, 
                "gas": 0, 
                "wind": 0, 
                "bio": 0, 
                "hydro": 0}, 
    "Calgary": {"wind": 0, 
                "bio": 0,
                "solar": 0, 
                "gas": dg["Capacity_MW"][3] + dg["Capacity_MW"][9] + dg["Capacity_MW"][16] + dg["Capacity_MW"][41] + dg["Capacity_MW"][47],
                "hydro": dg["Capacity_MW"][50]}, 
    "Edmonton": {"wind": 0,
                 "hydro": 0, 
                 "gas": dg["Capacity_MW"][14] + dg["Capacity_MW"][46],
                 "solar": load_matrix.values[42,0]*(dg["Capacity_MW"][85]), 
                 "bio": dg["Capacity_MW"][99]}   
}
   
loads = {
    "Lloydminster": load_matrix.values[0,0],
    "Rainbow_Lake" : load_matrix.values[1,0],
    "High_Level" : load_matrix.values[2,0], 
    "Peace_River": load_matrix.values[3,0],
    "Grande_Prairie": load_matrix.values[4,0], 
    "High_Prairie": load_matrix.values[5,0], 
    "Grande_Cache": load_matrix.values[6,0], 
    "Valleyview": load_matrix.values[7,0], 
    "Fox_Creek": load_matrix.values[8,0],
    "Fort_Mac": load_matrix.values[9,0], 
    "Swan_Hills": load_matrix.values[10,0], 
    "Athabasca": load_matrix.values[11,0], 
    "Cold_Lake": load_matrix.values[12,0], 
    "Hinton_Edson": load_matrix.values[13,0],  
    "Drayton_Valley": load_matrix.values[14,0], 
    "Wetaskiwin": load_matrix.values[15,0], 
    "Wainwright": load_matrix.values[16,0], 
    "Fort_Sask": load_matrix.values[17,0], 
    "Abraham_Lake": load_matrix.values[18,0], 
    "Red_Deer": load_matrix.values[19,0], 
    "Alliance_Battle_River": load_matrix.values[20,0], 
    "Provost": load_matrix.values[21,0], 
    "Caroline": load_matrix.values[22,0], 
    "Didsbury": load_matrix.values[23,0], 
    "Medicine_Hat": load_matrix.values[24,0], 
    "Wabamun": load_matrix.values[25,0], 
    "Hanna": load_matrix.values[26,0], 
    "Sheerness": load_matrix.values[27,0], 
    "Seebe": load_matrix.values[28,0], 
    "Srathmore_Blackie": load_matrix.values[29,0], 
    "High_River": load_matrix.values[30,0], 
    "Brooks": load_matrix.values[31,0], 
    "Empress": load_matrix.values[32,0], 
    "Stavely": load_matrix.values[33,0], 
    "Vauxhall": load_matrix.values[34,0], 
    "Fort_Macleod": load_matrix.values[35,0], 
    "Lethbridge": load_matrix.values[36,0],
    "Glenwood": load_matrix.values[37,0], 
    "Vegreville": load_matrix.values[38,0], 
    "Airdrie": load_matrix.values[39,0], 
    "Calgary": load_matrix.values[40,0], 
    "Edmonton": load_matrix.values[41,0]   
}
    
n = pypsa.Network()

dl = pd.read_excel("Data/Load Data With Coordinates.xlsx") 

for data in dl:
    City = dl["Name"]
    y_coordinate = dl["y - coordinate"]
    x_coordinate = dl["x - coordinate"]
    
    n.add("Bus", City, y = y_coordinate.values, x = x_coordinate.values, v_nom = 120, carrier = "AC")

n.add(
    "Carrier",
    ["gas", "wind", "solar", "bio", "hydro"],
    co2_emissions=emissions,
    nice_name=["Gas", "Onshore Wind", "Solar", "Biomass/Biogas/Waste Heat Recovery", "Hydro"],
    color=["indianred", "orange", "green", "darkviolet", "dodgerblue"],
)
    
n.add("Carrier", 
      ["electricity", "AC"])
    
for tech, p_nom in power_plants["Lloydminster"].items():
    n.add(
        "Generator",
        f"Lloydminster {tech}",
        bus="Lloydminster",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )

for tech, p_nom in power_plants["Rainbow_Lake"].items():
    n.add(
        "Generator",
        f"Rainbow_Lake {tech}",
        bus="Rainbow_Lake",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["High_Level"].items():
    n.add(
        "Generator",
        f"High_Level {tech}",
        bus="High_Level",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Peace_River"].items():
    n.add(
        "Generator",
        f"Peace_River {tech}",
        bus="Peace_River",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Grande_Prairie"].items():
    n.add(
        "Generator",
        f"Grande_Prairie {tech}",
        bus="Grande_Prairie",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["High_Prairie"].items():
    n.add(
        "Generator",
        f"High_Prairie {tech}",
        bus="High_Prairie",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Grande_Cache"].items():
    n.add(
        "Generator",
        f"Grande_Cache {tech}",
        bus="Grande_Cache",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Valleyview"].items():
    n.add(
        "Generator",
        f"Valleyview {tech}",
        bus="Valleyview",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Fox_Creek"].items():
    n.add(
        "Generator",
        f"Fox_Creek {tech}",
        bus="Fox_Creek",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Fort_Mac"].items():
    n.add(
        "Generator",
        f"Fort_Mac {tech}",
        bus="Fort_Mac",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Swan_Hills"].items():
    n.add(
        "Generator",
        f"Swan_Hills {tech}",
        bus="Swan_Hills",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Athabasca"].items():
    n.add(
        "Generator",
        f"Athabasca {tech}",
        bus="Athabasca",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Cold_Lake"].items():
    n.add(
        "Generator",
        f"Cold_Lake {tech}",
        bus="Cold_Lake",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Hinton_Edson"].items():
    n.add(
        "Generator",
        f"Hinton_Edson {tech}",
        bus="Hinton_Edson",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Drayton_Valley"].items():
    n.add(
        "Generator",
        f"Drayton_Valley {tech}",
        bus="Drayton_Valley",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Wetaskiwin"].items():
    n.add(
        "Generator",
        f"Wetaskiwin {tech}",
        bus="Wetaskiwin",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Wainwright"].items():
    n.add(
        "Generator",
        f"Wainwright {tech}",
        bus="Wainwright",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Fort_Sask"].items():
    n.add(
        "Generator",
        f"Fort_Sask {tech}",
        bus="Fort_Sask",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Abraham_Lake"].items():
    n.add(
        "Generator",
        f"Abraham_Lake {tech}",
        bus="Abraham_Lake",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Red_Deer"].items():
    n.add(
        "Generator",
        f"Red_Deer {tech}",
        bus="Red_Deer",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Alliance_Battle_River"].items():
    n.add(
        "Generator",
        f"Alliance_Battle_River {tech}",
        bus="Alliance_Battle_River",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Provost"].items():
    n.add(
        "Generator",
        f"Provost {tech}",
        bus="Provost",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Caroline"].items():
    n.add(
        "Generator",
        f"Caroline {tech}",
        bus="Caroline",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Didsbury"].items():
    n.add(
        "Generator",
        f"Didsbury {tech}",
        bus="Didsbury",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Medicine_Hat"].items():
    n.add(
        "Generator",
        f"Medicine_Hat {tech}",
        bus="Medicine_Hat",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Wabamun"].items():
    n.add(
        "Generator",
        f"Wabamun {tech}",
        bus="Wabamun",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Hanna"].items():
    n.add(
        "Generator",
        f"Hanna {tech}",
        bus="Hanna",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Sheerness"].items():
    n.add(
        "Generator",
        f"Sheerness {tech}",
        bus="Sheerness",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Seebe"].items():
    n.add(
        "Generator",
        f"Seebe {tech}",
        bus="Seebe",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Srathmore_Blackie"].items():
    n.add(
        "Generator",
        f"Srathmore_Blackie {tech}",
        bus="Srathmore_Blackie",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["High_River"].items():
    n.add(
        "Generator",
        f"High_River {tech}",
        bus="High_River",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Brooks"].items():
    n.add(
        "Generator",
        f"Brooks {tech}",
        bus="Brooks",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Empress"].items():
    n.add(
        "Generator",
        f"Empress {tech}",
        bus="Empress",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Stavely"].items():
    n.add(
        "Generator",
        f"Stavely {tech}",
        bus="Stavely",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Vauxhall"].items():
    n.add(
        "Generator",
        f"Vauxhall {tech}",
        bus="Vauxhall",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Fort_Macleod"].items():
    n.add(
        "Generator",
        f"Fort_Macleod {tech}",
        bus="Fort_Macleod",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )

for tech, p_nom in power_plants["Lethbridge"].items():
    n.add(
        "Generator",
        f"Lethbridge {tech}",
        bus="Lethbridge",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Glenwood"].items():
    n.add(
        "Generator",
        f"Glenwood {tech}",
        bus="Glenwood",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Vegreville"].items():
    n.add(
        "Generator",
        f"Vegreville {tech}",
        bus="Vegreville",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Airdrie"].items():
    n.add(
        "Generator",
        f"Airdrie {tech}",
        bus="Airdrie",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Calgary"].items():
    n.add(
        "Generator",
        f"Calgary {tech}",
        bus="Calgary",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )
    
for tech, p_nom in power_plants["Edmonton"].items():
    n.add(
        "Generator",
        f"Edmonton {tech}",
        bus="Edmonton",
        carrier=tech,
        efficiency=efficiency.get(tech, 1),
        p_nom=p_nom,
        marginal_cost=fuel_cost.get(tech, 0) / efficiency.get(tech, 1),
    )


n.add(
    "Load",
    "Lloydminster electricity demand",
    bus ="Lloydminster",
    p_set=loads["Lloydminster"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Rainbow_Lake electricity demand",
    bus ="Rainbow_Lake",
    p_set=loads["Rainbow_Lake"],
    carrier="electricity",
 )

n.add(
    "Load",
    "High_Level electricity demand",
    bus ="High_Level",
    p_set=loads["High_Level"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Peace_River electricity demand",
    bus ="Peace_River",
    p_set=loads["Peace_River"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Grande_Prairie electricity demand",
    bus ="Grande_Prairie",
    p_set=loads["Grande_Prairie"],
    carrier="electricity",
 )

n.add(
    "Load",
    "High_Prairie electricity demand",
    bus ="High_Prairie",
    p_set=loads["High_Prairie"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Grande_Cache electricity demand",
    bus ="Grande_Cache",
    p_set=loads["Grande_Cache"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Valleyview electricity demand",
    bus ="Valleyview",
    p_set=loads["Valleyview"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Fox_Creek electricity demand",
    bus ="Fox_Creek",
    p_set=loads["Fox_Creek"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Fort_Mac electricity demand",
    bus ="Fort_Mac",
    p_set=loads["Fort_Mac"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Swan_Hills electricity demand",
    bus ="Swan_Hills",
    p_set=loads["Swan_Hills"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Athabasca electricity demand",
    bus ="Athabasca",
    p_set=loads["Athabasca"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Cold_Lake electricity demand",
    bus ="Cold_Lake",
    p_set=loads["Cold_Lake"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Hinton_Edson electricity demand",
    bus ="Hinton_Edson",
    p_set=loads["Hinton_Edson"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Drayton_Valley electricity demand",
    bus ="Drayton_Valley",
    p_set=loads["Drayton_Valley"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Wetaskiwin electricity demand",
    bus ="Wetaskiwin",
    p_set=loads["Wetaskiwin"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Wainwright electricity demand",
    bus ="Wainwright",
    p_set=loads["Wainwright"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Fort_Sask electricity demand",
    bus ="Fort_Sask",
    p_set=loads["Fort_Sask"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Abraham_Lake electricity demand",
    bus ="Abraham_Lake",
    p_set=loads["Abraham_Lake"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Red_Deer electricity demand",
    bus ="Red_Deer",
    p_set=loads["Red_Deer"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Alliance_Battle_River electricity demand",
    bus ="Alliance_Battle_River",
    p_set=loads["Alliance_Battle_River"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Provost electricity demand",
    bus ="Provost",
    p_set=loads["Provost"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Caroline electricity demand",
    bus ="Caroline",
    p_set=loads["Caroline"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Didsbury  electricity demand",
    bus ="Didsbury",
    p_set=loads["Didsbury"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Medicine_Hat electricity demand",
    bus ="Medicine_Hat",
    p_set=loads["Medicine_Hat"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Wabamun electricity demand",
    bus ="Wabamun",
    p_set=loads["Wabamun"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Hanna electricity demand",
    bus ="Hanna",
    p_set=loads["Hanna"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Sheerness electricity demand",
    bus ="Sheerness",
    p_set=loads["Sheerness"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Seebe electricity demand",
    bus ="Seebe",
    p_set=loads["Seebe"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Srathmore_Blackie electricity demand",
    bus ="Srathmore_Blackie",
    p_set=loads["Srathmore_Blackie"],
    carrier="electricity",
 )

n.add(
    "Load",
    "High_River electricity demand",
    bus ="High_River",
    p_set=loads["High_River"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Brooks electricity demand",
    bus ="Brooks",
    p_set=loads["Brooks"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Empress electricity demand",
    bus ="Empress",
    p_set=loads["Empress"],
    carrier="electricity",
 )

n.add(
    "Load",
    "Stavely electricity demand",
    bus ="Stavely",
    p_set=loads["Stavely"],
    carrier="electricity",
 )
 
n.add(
    "Load",
    "Vauxhall electricity demand",
    bus ="Vauxhall",
    p_set=loads["Vauxhall"],
    carrier="electricity",
 )
 
n.add(
    "Load",
    "Fort_Macleod electricity demand",
    bus ="Fort_Macleod",
    p_set=loads["Fort_Macleod"],
    carrier="electricity",
 )
 
n.add(
    "Load",
    "Lethbridge electricity demand",
    bus ="Lethbridge",
    p_set=loads["Lethbridge"],
    carrier="electricity",
 )
 
n.add(
    "Load",
    "Glenwood electricity demand",
    bus ="Glenwood",
    p_set=loads["Glenwood"],
    carrier="electricity",
 )
 
n.add(
    "Load",
    "Vegreville electricity demand",
    bus ="Vegreville",
    p_set=loads["Vegreville"],
    carrier="electricity",
 )
  
n.add(
    "Load",
    "Airdrie demand",
    bus ="Airdrie",
    p_set=loads["Airdrie"],
    carrier="electricity",
 )
 
n.add(
    "Load",
    "Calgary electricity demand",
    bus ="Calgary",
    p_set=loads["Calgary"],
    carrier="electricity",
 )
 
n.add(
    "Load",
    "Edmonton electricity demand",
    bus ="Edmonton",
    p_set=loads["Edmonton"],
    carrier="electricity",
 )

n.add(
    "Line",
    "High_Level-Rainbow_Lake",
    bus0="High_Level",
    bus1="Rainbow_Lake",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Rainbow_Lake-Peace_River",
    bus0="Rainbow_Lake",
    bus1="Peace_River",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Mac-High_Level",
    bus0="Fort_Mac",
    bus1="High_Level",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Peace_River-High_Level",
    bus0="Peace_River",
    bus1="High_Level",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Mac-High Prarie",
    bus0="Fort_Mac",
    bus1="High_Prairie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Mac-Peace_River",
    bus0="Fort_Mac",
    bus1="Peace_River",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Peace_River-Grande Prarie",
    bus0="Peace_River",
    bus1="Grande_Prairie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Peace_River-Valleyview",
    bus0="Peace_River",
    bus1="Valleyview",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Peace_River-High_Prairie",
    bus0="Peace_River",
    bus1="High_Prairie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Grande_Cache-Grande Prarie",
    bus0="Grande_Cache",
    bus1="Grande_Prairie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Valleyview-High_Prairie",
    bus0="Valleyview",
    bus1="High_Prairie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Valleyview-Fox_Creek",
    bus0="Valleyview",
    bus1="Fox_Creek",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Valleyview-Swan_Hills",
    bus0="Valleyview",
    bus1="Swan_Hills",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Mac-Athabasca",
    bus0="Fort_Mac",
    bus1="Athabasca",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Mac-Cold_Lake",
    bus0="Fort_Mac",
    bus1="Cold_Lake",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Grande_Cache-Hinton_Edson",
    bus0="Grande_Cache",
    bus1="Hinton_Edson",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Grande_Cache-Fox_Creek",
    bus0="Grande_Cache",
    bus1="Fox_Creek",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "High_Prairie-Swan_Hills",
    bus0="High_Prairie",
    bus1="Swan_Hills",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hinton_Edson-Fox_Creek",
    bus0="Hinton_Edson",
    bus1="Fox_Creek",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Swan_Hills-Fox_Creek",
    bus0="Swan_Hills",
    bus1="Fox_Creek",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Swan_Hills-Wabamun",
    bus0="Swan_Hills",
    bus1="Wabamun",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Swan_Hills-Athabasca",
    bus0="Swan_Hills",
    bus1="Athabasca",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hinton_Edson-Wabamun",
    bus0="Hinton_Edson",
    bus1="Wabamun",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Athabasca-Wabamun",
    bus0="Athabasca",
    bus1="Wabamun",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Drayton_Valley-Wabamun",
    bus0="Drayton_Valley",
    bus1="Wabamun",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hinton_Edson-Drayton_Valley",
    bus0="Hinton_Edson",
    bus1="Drayton_Valley",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hinton_Edson-Abraham_Lake",
    bus0="Hinton_Edson",
    bus1="Abraham_Lake",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Abraham_Lake-Drayton_Valley",
    bus0="Abraham_Lake",
    bus1="Drayton_Valley",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Caroline-Drayton_Valley",
    bus0="Caroline",
    bus1="Drayton_Valley",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wetaskiwin-Drayton_Valley",
    bus0="Wetaskiwin",
    bus1="Drayton_Valley",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Cold_Lake-Athabasca",
    bus0="Cold_Lake",
    bus1="Athabasca",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Cold_Lake-Vegreville",
    bus0="Cold_Lake",
    bus1="Vegreville",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Cold_Lake-Lloydminster",
    bus0="Cold_Lake",
    bus1="Lloydminster",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Sask-Athabasca",
    bus0="Fort_Sask",
    bus1="Athabasca",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Sask-Vegreville",
    bus0="Fort_Sask",
    bus1="Vegreville",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Sask-Edmonton",
    bus0="Fort_Sask",
    bus1="Edmonton",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Sask-Wetaskiwin",
    bus0="Fort_Sask",
    bus1="Wetaskiwin",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Vegreville-Lloydminster",
    bus0="Vegreville",
    bus1="Lloydminster",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wainwright-Lloydminster",
    bus0="Wainwright",
    bus1="Lloydminster",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wainwright-Vegreville",
    bus0="Wainwright",
    bus1="Vegreville",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wainwright-Alliance_Battle_River",
    bus0="Wainwright",
    bus1="Alliance_Battle_River",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wetaskiwin-Vegreville",
    bus0="Wetaskiwin",
    bus1="Vegreville",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wetaskiwin-Edmonton",
    bus0="Wetaskiwin",
    bus1="Edmonton",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wetaskiwin-Alliance_Battle_River",
    bus0="Wetaskiwin",
    bus1="Alliance_Battle_River",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Athabasca-Edmonton",
    bus0="Athabasca",
    bus1="Edmonton",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wabamun-Edmonton",
    bus0="Wabamun",
    bus1="Edmonton",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wabamun-Wetaskiwin",
    bus0="Wabamun",
    bus1="Wetaskiwin",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Red_Deer-Wetaskiwin",
    bus0="Red_Deer",
    bus1="Wetaskiwin",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Red_Deer-Alliance_Battle_River",
    bus0="Red_Deer",
    bus1="Alliance_Battle_River",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Red_Deer-Hanna",
    bus0="Red_Deer",
    bus1="Hanna",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Red_Deer-Didsbury",
    bus0="Red_Deer",
    bus1="Didsbury",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Red_Deer-Caroline",
    bus0="Red_Deer",
    bus1="Caroline",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Abraham_Lake-Caroline",
    bus0="Abraham_Lake",
    bus1="Caroline",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Didsbury-Caroline",
    bus0="Didsbury",
    bus1="Caroline",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Alliance_Battle_River-Hanna",
    bus0="Alliance_Battle_River",
    bus1="Hanna",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Alliance_Battle_River-Provost",
    bus0="Alliance_Battle_River",
    bus1="Provost",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Wainwright-Provost",
    bus0="Wainwright",
    bus1="Provost",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hanna-Provost",
    bus0="Hanna",
    bus1="Provost",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hanna-Didsbury",
    bus0="Hanna",
    bus1="Didsbury",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hanna-Airdrie",
    bus0="Hanna",
    bus1="Airdrie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hanna-Srathmore_Blackie",
    bus0="Hanna",
    bus1="Srathmore_Blackie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hanna-Sheerness",
    bus0="Hanna",
    bus1="Sheerness",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Hanna-Empress",
    bus0="Hanna",
    bus1="Empress",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Seebe-Abraham_Lake",
    bus0="Seebe",
    bus1="Abraham_Lake",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Seebe-Caroline",
    bus0="Seebe",
    bus1="Caroline",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Seebe-Airdrie",
    bus0="Seebe",
    bus1="Airdrie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Seebe-Calgary",
    bus0="Seebe",
    bus1="Calgary",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Seebe-High_River",
    bus0="Seebe",
    bus1="High_River",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Airdrie-Didsbury",
    bus0="Airdrie",
    bus1="Didsbury",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Airdrie-Calgary",
    bus0="Airdrie",
    bus1="Calgary",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Srathmore_Blackie-Calgary",
    bus0="Srathmore_Blackie",
    bus1="Calgary",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "High_River-Calgary",
    bus0="High_River",
    bus1="Calgary",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Sheerness-Empress",
    bus0="Sheerness",
    bus1="Empress",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Sheerness-Brooks",
    bus0="Sheerness",
    bus1="Brooks",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Sheerness-Srathmore_Blackie",
    bus0="Sheerness",
    bus1="Srathmore_Blackie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "High_River-Fort_Macleod",
    bus0="High_River",
    bus1="Fort_Macleod",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "High_River-Srathmore_Blackie",
    bus0="High_River",
    bus1="Srathmore_Blackie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "High_River-Stavely",
    bus0="High_River",
    bus1="Stavely",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Stavely-Srathmore_Blackie",
    bus0="Stavely",
    bus1="Srathmore_Blackie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Brooks-Srathmore_Blackie",
    bus0="Brooks",
    bus1="Srathmore_Blackie",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Brooks-Empress",
    bus0="Brooks",
    bus1="Empress",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Brooks-Stavely",
    bus0="Brooks",
    bus1="Stavely",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Brooks-Vauxhall",
    bus0="Brooks",
    bus1="Vauxhall",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Macleod-Stavely",
    bus0="Fort_Macleod",
    bus1="Stavely",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Lethbridge-Stavely",
    bus0="Lethbridge",
    bus1="Stavely",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Vauxhall-Stavely",
    bus0="Vauxhall",
    bus1="Stavely",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Vauxhall-Medicine_Hat",
    bus0="Vauxhall",
    bus1="Medicine_Hat",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Vauxhall-Glenwood",
    bus0="Vauxhall",
    bus1="Glenwood",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Vauxhall-Lethbridge",
    bus0="Vauxhall",
    bus1="Lethbridge",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Empress-Medicine_Hat",
    bus0="Empress",
    bus1="Medicine_Hat",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Glenwood-Medicine_Hat",
    bus0="Glenwood",
    bus1="Medicine_Hat",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Macleod-Glenwood",
    bus0="Fort_Macleod",
    bus1="Glenwood",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Fort_Macleod-Lethbridge",
    bus0="Fort_Macleod",
    bus1="Lethbridge",
    s_nom=500,
    x=1,
    r=1,
)

n.add(
    "Line",
    "Lethbridge-Glenwood",
    bus0="Lethbridge",
    bus1="Glenwood",
    s_nom=500,
    x=1,
    r=1,
)

n.optimize(solver_name="highs")

extent = [-130, -55, 36.5, 75]
central_lon = np.mean(extent[:2])
central_lat = np.mean(extent[2:])

plt.figure(figsize=(12, 8))
norm = plt.Normalize(vmin=0, vmax=100)
ax = plt.axes(projection=ccrs.EqualEarth(central_lon, central_lat))
ax.set_extent(extent)
resol = '50m'

line_loading = n.lines_t.p0.iloc[0].abs() / n.lines.s_nom / n.lines.s_max_pu *100

s = n.generators_t.p.loc["now"].groupby([n.generators.bus, n.generators.carrier]).sum()

n.plot( ax=ax, 
       margin= 0.35, 
       bus_sizes = s/6000,
       line_colors=line_loading, 
       line_norm=norm, 
       line_cmap="viridis", 
       flow = "mean",
       line_widths = 0.1, 
       color_geomap=True)

plt.colorbar(
    plt.cm.ScalarMappable(cmap="viridis", norm=norm),
    ax=ax,
    label="Relative line loading [%]",
    shrink=0.6,
)

solar_patch = mpatches.Patch(color='green', label='Solar')
gas_patch = mpatches.Patch(color='indianred', label='Gas')
wind_patch = mpatches.Patch(color='orange', label='Wind')
bio_patch = mpatches.Patch(color='darkviolet', label='Biomass/Biogas/Waste Heat Recovery')
hydro_patch = mpatches.Patch(color='dodgerblue', label='Hydro')

plt.legend(handles=[solar_patch, gas_patch, wind_patch, bio_patch, hydro_patch])

country_bodr = cartopy.feature.NaturalEarthFeature(category='cultural', 
    name='admin_0_boundary_lines_land', scale=resol, facecolor='none', edgecolor='k')

provinc_bodr = cartopy.feature.NaturalEarthFeature(category='cultural', 
    name='admin_1_states_provinces_lines', scale=resol, facecolor='none', edgecolor='k')

ax.add_feature(country_bodr, linestyle='--', linewidth=0.8, edgecolor="k", zorder=10)  
ax.add_feature(provinc_bodr, linestyle='--', linewidth=0.6, edgecolor="k", zorder=10)

#Finding the percentages of solar to trad energy per generation node
lloydminster_percentage = ((s.Lloydminster.bio)+(s.Lloydminster.solar)+(s.Lloydminster.wind)+(s.Lloydminster.hydro))/((s.Lloydminster.bio)+(s.Lloydminster.solar)+(s.Lloydminster.wind)+(s.Lloydminster.hydro)+(s.Lloydminster.gas))
if np.isnan(lloydminster_percentage):
    lloydminster_percentage = 0
    
rainbow_lake_percentage = ((s.Rainbow_Lake.bio)+(s.Rainbow_Lake.solar)+(s.Rainbow_Lake.wind)+(s.Rainbow_Lake.hydro))/((s.Rainbow_Lake.bio)+(s.Rainbow_Lake.solar)+(s.Rainbow_Lake.wind)+(s.Rainbow_Lake.hydro)+(s.Rainbow_Lake.gas))
if np.isnan(rainbow_lake_percentage):
    rainbow_lake_percentage = 0
    
high_level_percentage =  ((s.High_Level.bio)+(s.High_Level.solar)+(s.High_Level.wind)+(s.High_Level.hydro))/((s.High_Level.bio)+(s.High_Level.solar)+(s.High_Level.wind)+(s.High_Level.hydro)+(s.High_Level.gas))
if np.isnan(high_level_percentage):
    high_level_percentage = 0
    
peace_river_percentage = ((s.Peace_River.bio)+(s.Peace_River.solar)+(s.Peace_River.wind)+(s.Peace_River.hydro))/((s.Peace_River.bio)+(s.Peace_River.solar)+(s.Peace_River.wind)+(s.Peace_River.hydro)+(s.Peace_River.gas))
if np.isnan(peace_river_percentage):
    peace_river_percentage = 0
    
grande_prairie_percentage = ((s.Grande_Prairie.bio)+(s.Grande_Prairie.solar)+(s.Grande_Prairie.wind)+(s.Grande_Prairie.hydro))/((s.Grande_Prairie.bio)+(s.Grande_Prairie.solar)+(s.Grande_Prairie.wind)+(s.Grande_Prairie.hydro)+(s.Grande_Prairie.gas))
if np.isnan(lloydminster_percentage):
    lloydminster_percentage = 0
    
high_prairie_percentage = ((s.High_Prairie.bio)+(s.High_Prairie.solar)+(s.High_Prairie.wind)+(s.High_Prairie.hydro))/((s.High_Prairie.bio)+(s.High_Prairie.solar)+(s.High_Prairie.wind)+(s.High_Prairie.hydro)+(s.High_Prairie.gas))
if np.isnan(high_prairie_percentage):
    high_prairie_percentage = 0
    
grande_cache_percentage = ((s.Grande_Cache.bio)+(s.Grande_Cache.solar)+(s.Grande_Cache.wind)+(s.Grande_Cache.hydro))/((s.Grande_Cache.bio)+(s.Grande_Cache.solar)+(s.Grande_Cache.wind)+(s.Grande_Cache.hydro)+(s.Grande_Cache.gas))
if np.isnan(grande_cache_percentage):
    grande_cache_percentage = 0
    
valleyview_percentage =  ((s.Valleyview.bio)+(s.Valleyview.solar)+(s.Valleyview.wind)+(s.Valleyview.hydro))/((s.Valleyview.bio)+(s.Valleyview.solar)+(s.Valleyview.wind)+(s.Valleyview.hydro)+(s.Valleyview.gas))
if np.isnan(valleyview_percentage):
    valleyview_percentage = 0
    
fox_creek_percentage = ((s.Fox_Creek.bio)+(s.Fox_Creek.solar)+(s.Fox_Creek.wind)+(s.Fox_Creek.hydro))/((s.Fox_Creek.bio)+(s.Fox_Creek.solar)+(s.Fox_Creek.wind)+(s.Fox_Creek.hydro)+(s.Fox_Creek.gas))
if np.isnan(fox_creek_percentage):
    fox_creek_percentage = 0
    
fort_mac_percentage = ((s.Fort_Mac.bio)+(s.Fort_Mac.solar)+(s.Fort_Mac.wind)+(s.Fort_Mac.hydro))/((s.Fort_Mac.bio)+(s.Fort_Mac.solar)+(s.Fort_Mac.wind)+(s.Fort_Mac.hydro)+(s.Fort_Mac.gas))
if np.isnan(fort_mac_percentage):
    fort_mac_percentage = 0

swan_hills_percentage = ((s.Swan_Hills.bio)+(s.Swan_Hills.solar)+(s.Swan_Hills.wind)+(s.Swan_Hills.hydro))/((s.Swan_Hills.bio)+(s.Swan_Hills.solar)+(s.Swan_Hills.wind)+(s.Swan_Hills.hydro)+(s.Swan_Hills.gas))
if np.isnan(swan_hills_percentage):
    swan_hills_percentage = 0
    
athabasca_percentage = ((s.Athabasca.bio)+(s.Athabasca.solar)+(s.Athabasca.wind)+(s.Athabasca.hydro))/((s.Athabasca.bio)+(s.Athabasca.solar)+(s.Athabasca.wind)+(s.Athabasca.hydro)+(s.Athabasca.gas))
if np.isnan(athabasca_percentage):
    athabasca_percentage = 0

cold_lake_percentage =  ((s.Cold_Lake.bio)+(s.Cold_Lake.solar)+(s.Cold_Lake.wind)+(s.Cold_Lake.hydro))/((s.Cold_Lake.bio)+(s.Cold_Lake.solar)+(s.Cold_Lake.wind)+(s.Cold_Lake.hydro)+(s.Cold_Lake.gas))
if np.isnan(cold_lake_percentage):
    cold_lake_percentage = 0
    
hinton_edson_percentage = ((s.Hinton_Edson.bio)+(s.Hinton_Edson.solar)+(s.Hinton_Edson.wind)+(s.Hinton_Edson.hydro))/((s.Hinton_Edson.bio)+(s.Hinton_Edson.solar)+(s.Hinton_Edson.wind)+(s.Hinton_Edson.hydro)+(s.Hinton_Edson.gas))
if np.isnan(hinton_edson_percentage):
    hinton_edson_percentage = 0
    
drayton_valley_percentage = ((s.Drayton_Valley.bio)+(s.Drayton_Valley.solar)+(s.Drayton_Valley.wind)+(s.Drayton_Valley.hydro))/((s.Drayton_Valley.bio)+(s.Drayton_Valley.solar)+(s.Drayton_Valley.wind)+(s.Drayton_Valley.hydro)+(s.Drayton_Valley.gas))
if np.isnan(drayton_valley_percentage):
    drayton_valley_percentage = 0
    
wetaskiwin_percentage = ((s.Wetaskiwin.bio)+(s.Wetaskiwin.solar)+(s.Wetaskiwin.wind)+(s.Wetaskiwin.hydro))/((s.Wetaskiwin.bio)+(s.Wetaskiwin.solar)+(s.Wetaskiwin.wind)+(s.Wetaskiwin.hydro)+(s.Wetaskiwin.gas))
if np.isnan(wetaskiwin_percentage):
    wetaskiwin_percentage = 0
    
wainwright_percentage = ((s.Wainwright.bio)+(s.Wainwright.solar)+(s.Wainwright.wind)+(s.Wainwright.hydro))/((s.Wainwright.bio)+(s.Wainwright.solar)+(s.Wainwright.wind)+(s.Wainwright.hydro)+(s.Wainwright.gas))
if np.isnan(wainwright_percentage):
    wainwright_percentage = 0
    
fort_sask_percentage =  ((s.Fort_Sask.bio)+(s.Fort_Sask.solar)+(s.Fort_Sask.wind)+(s.Fort_Sask.hydro))/((s.Fort_Sask.bio)+(s.Fort_Sask.solar)+(s.Fort_Sask.wind)+(s.Fort_Sask.hydro)+(s.Fort_Sask.gas))
if np.isnan(fort_sask_percentage):
    fort_sask_percentage = 0
    
abraham_lake_percentage = ((s.Abraham_Lake.bio)+(s.Abraham_Lake.solar)+(s.Abraham_Lake.wind)+(s.Abraham_Lake.hydro))/((s.Abraham_Lake.bio)+(s.Abraham_Lake.solar)+(s.Abraham_Lake.wind)+(s.Abraham_Lake.hydro)+(s.Abraham_Lake.gas))
if np.isnan(abraham_lake_percentage):
    abraham_lake_percentage = 0
    
red_deer_percentage = ((s.Red_Deer.bio)+(s.Red_Deer.solar)+(s.Red_Deer.wind)+(s.Red_Deer.hydro))/((s.Red_Deer.bio)+(s.Red_Deer.solar)+(s.Red_Deer.wind)+(s.Red_Deer.hydro)+(s.Red_Deer.gas))
if np.isnan(red_deer_percentage):
    red_deer_percentage = 0
    
alliance_battle_river_percentage = ((s.Alliance_Battle_River.bio)+(s.Alliance_Battle_River.solar)+(s.Alliance_Battle_River.wind)+(s.Alliance_Battle_River.hydro))/((s.Alliance_Battle_River.bio)+(s.Alliance_Battle_River.solar)+(s.Alliance_Battle_River.wind)+(s.Alliance_Battle_River.hydro)+(s.Alliance_Battle_River.gas))
if np.isnan(alliance_battle_river_percentage):
    alliance_battle_river_percentage = 0
    
provost_percentage = ((s.Provost.bio)+(s.Provost.solar)+(s.Provost.wind)+(s.Provost.hydro))/((s.Provost.bio)+(s.Provost.solar)+(s.Provost.wind)+(s.Provost.hydro)+(s.Provost.gas))
if np.isnan(provost_percentage):
    provost_percentage = 0
    
caroline_percentage =  ((s.Caroline.bio)+(s.Caroline.solar)+(s.Caroline.wind)+(s.Caroline.hydro))/((s.Caroline.bio)+(s.Caroline.solar)+(s.Caroline.wind)+(s.Caroline.hydro)+(s.Caroline.gas))
if np.isnan(caroline_percentage):
    caroline_percentage = 0
    
didsbury_percentage = ((s.Didsbury.bio)+(s.Didsbury.solar)+(s.Didsbury.wind)+(s.Didsbury.hydro))/((s.Didsbury.bio)+(s.Didsbury.solar)+(s.Didsbury.wind)+(s.Didsbury.hydro)+(s.Didsbury.gas))
if np.isnan(didsbury_percentage):
    didsbury_percentage = 0
    
medicine_hat_percentage = ((s.Medicine_Hat.bio)+(s.Medicine_Hat.solar)+(s.Medicine_Hat.wind)+(s.Medicine_Hat.hydro))/((s.Medicine_Hat.bio)+(s.Medicine_Hat.solar)+(s.Medicine_Hat.wind)+(s.Medicine_Hat.hydro)+(s.Medicine_Hat.gas))
if np.isnan(medicine_hat_percentage):
    medicine_hat_percentage = 0
    
wabamun_percentage = ((s.Wabamun.bio)+(s.Wabamun.solar)+(s.Wabamun.wind)+(s.Wabamun.hydro))/((s.Wabamun.bio)+(s.Wabamun.solar)+(s.Wabamun.wind)+(s.Wabamun.hydro)+(s.Wabamun.gas))
if np.isnan(wabamun_percentage):
    wabamun_percentage = 0
    
hanna_percentage = ((s.Hanna.bio)+(s.Hanna.solar)+(s.Hanna.wind)+(s.Hanna.hydro))/((s.Hanna.bio)+(s.Hanna.solar)+(s.Hanna.wind)+(s.Hanna.hydro)+(s.Hanna.gas))
if np.isnan(hanna_percentage):
    hanna_percentage = 0
    
sheerness_percentage =  ((s.Sheerness.bio)+(s.Sheerness.solar)+(s.Sheerness.wind)+(s.Sheerness.hydro))/((s.Sheerness.bio)+(s.Sheerness.solar)+(s.Sheerness.wind)+(s.Sheerness.hydro)+(s.Sheerness.gas))
if np.isnan(sheerness_percentage):
    sheerness_percentage = 0
    
seebe_percentage = ((s.Seebe.bio)+(s.Seebe.solar)+(s.Seebe.wind)+(s.Seebe.hydro))/((s.Seebe.bio)+(s.Seebe.solar)+(s.Seebe.wind)+(s.Seebe.hydro)+(s.Seebe.gas))
if np.isnan(seebe_percentage):
    seebe_percentage = 0
    
srathmore_blackie_percentage = ((s.Srathmore_Blackie.bio)+(s.Srathmore_Blackie.solar)+(s.Srathmore_Blackie.wind)+(s.Srathmore_Blackie.hydro))/((s.Srathmore_Blackie.bio)+(s.Srathmore_Blackie.solar)+(s.Srathmore_Blackie.wind)+(s.Srathmore_Blackie.hydro)+(s.Srathmore_Blackie.gas))
if np.isnan(srathmore_blackie_percentage):
    srathmore_blackie_percentage = 0
    
high_river_percentage = ((s.High_River.bio)+(s.High_River.solar)+(s.High_River.wind)+(s.High_River.hydro))/((s.High_River.bio)+(s.High_River.solar)+(s.High_River.wind)+(s.High_River.hydro)+(s.High_River.gas))
if np.isnan(high_river_percentage):
    high_river_percentage = 0
    
brooks_percentage = ((s.Brooks.bio)+(s.Brooks.solar)+(s.Brooks.wind)+(s.Brooks.hydro))/((s.Brooks.bio)+(s.Brooks.solar)+(s.Brooks.wind)+(s.Brooks.hydro)+(s.Brooks.gas))
if np.isnan(brooks_percentage):
    brooks_percentage = 0
    
empress_percentage =  ((s.Empress.bio)+(s.Empress.solar)+(s.Empress.wind)+(s.Empress.hydro))/((s.Empress.bio)+(s.Empress.solar)+(s.Empress.wind)+(s.Empress.hydro)+(s.Empress.gas))
if np.isnan(empress_percentage):
    empress_percentage = 0
    
stavely_percentage = ((s.Stavely.bio)+(s.Stavely.solar)+(s.Stavely.wind)+(s.Stavely.hydro))/((s.Stavely.bio)+(s.Stavely.solar)+(s.Stavely.wind)+(s.Stavely.hydro)+(s.Stavely.gas))
if np.isnan(stavely_percentage):
    stavely_percentage = 0
    
vauxhall_percentage = ((s.Vauxhall.bio)+(s.Vauxhall.solar)+(s.Vauxhall.wind)+(s.Vauxhall.hydro))/((s.Vauxhall.bio)+(s.Vauxhall.solar)+(s.Vauxhall.wind)+(s.Vauxhall.hydro)+(s.Vauxhall.gas))
if np.isnan(vauxhall_percentage):
    vauxhall_percentage = 0
    
fort_macleod_percentage = ((s.Fort_Macleod.bio)+(s.Fort_Macleod.solar)+(s.Fort_Macleod.wind)+(s.Fort_Macleod.hydro))/((s.Fort_Macleod.bio)+(s.Fort_Macleod.solar)+(s.Fort_Macleod.wind)+(s.Fort_Macleod.hydro)+(s.Fort_Macleod.gas))
if np.isnan(fort_macleod_percentage):
    fort_macleod_percentage = 0
    
lethbridge_percentage = ((s.Lethbridge.bio)+(s.Lethbridge.solar)+(s.Lethbridge.wind)+(s.Lethbridge.hydro))/((s.Lethbridge.bio)+(s.Lethbridge.solar)+(s.Lethbridge.wind)+(s.Lethbridge.hydro)+(s.Lethbridge.gas))
if np.isnan(lethbridge_percentage):
    lethbridge_percentage = 0
    
glenwood_percentage = ((s.Glenwood.bio)+(s.Glenwood.solar)+(s.Glenwood.wind)+(s.Glenwood.hydro))/((s.Glenwood.bio)+(s.Glenwood.solar)+(s.Glenwood.wind)+(s.Glenwood.hydro)+(s.Glenwood.gas))
if np.isnan(glenwood_percentage):
    glenwood_percentage = 0
    
vegreville_percentage = ((s.Vegreville.bio)+(s.Vegreville.solar)+(s.Vegreville.wind)+(s.Vegreville.hydro))/((s.Vegreville.bio)+(s.Vegreville.solar)+(s.Vegreville.wind)+(s.Vegreville.hydro)+(s.Vegreville.gas))
if np.isnan(vegreville_percentage):
    vegreville_percentage = 0
    
airdrie_percentage = ((s.Airdrie.bio)+(s.Airdrie.solar)+(s.Airdrie.wind)+(s.Airdrie.hydro))/((s.Airdrie.bio)+(s.Airdrie.solar)+(s.Airdrie.wind)+(s.Airdrie.hydro)+(s.Airdrie.gas))
if np.isnan(airdrie_percentage):
    airdrie_percentage = 0
    
calgary_percentage = ((s.Calgary.bio)+(s.Calgary.solar)+(s.Calgary.wind)+(s.Calgary.hydro))/((s.Calgary.bio)+(s.Calgary.solar)+(s.Calgary.wind)+(s.Calgary.hydro)+(s.Calgary.gas))
if np.isnan(calgary_percentage):
    calgary_percentage = 0
    
edmonton_percentage = ((s.Edmonton.bio)+(s.Edmonton.solar)+(s.Edmonton.wind)+(s.Edmonton.hydro))/((s.Edmonton.bio)+(s.Edmonton.solar)+(s.Edmonton.wind)+(s.Edmonton.hydro)+(s.Edmonton.gas))
if np.isnan(edmonton_percentage):
    edmonton_percentage = 0

#Total power supplied in each line initialization
highlevel_rainbowlake = n.lines_t.p0.iloc[0,0]
rainbowlake_peaceriver = n.lines_t.p0.iloc[0,1]
fortmac_highlevel = n.lines_t.p0.iloc[0,2]
peaceriver_highlevel = n.lines_t.p0.iloc[0,3]
fortmac_highprairie = n.lines_t.p0.iloc[0,4]
fortmac_peaceriver = n.lines_t.p0.iloc[0,5]
peaceriver_grandeprairie = n.lines_t.p0.iloc[0,6]
peaceriver_valleyview = n.lines_t.p0.iloc[0,7]
peaceriver_highprairie = n.lines_t.p0.iloc[0,8]
grandecache_grandeprairie = n.lines_t.p0.iloc[0,9]

valleyview_highprairie = n.lines_t.p0.iloc[0,10]
valleyview_foxcreek = n.lines_t.p0.iloc[0,11]
valleyview_swanhills = n.lines_t.p0.iloc[0,12]
fortmac_athabasca = n.lines_t.p0.iloc[0,13]
fortmac_coldlake = n.lines_t.p0.iloc[0,14]
grandecache_hintonedson = n.lines_t.p0.iloc[0,15]
grandecache_foxcreek = n.lines_t.p0.iloc[0,16]
highprairie_swanhills = n.lines_t.p0.iloc[0,17]
hintonedson_foxcreek = n.lines_t.p0.iloc[0,18]
swanhills_foxcreek = n.lines_t.p0.iloc[0,19]

swanhills_wabamun = n.lines_t.p0.iloc[0,20]
swanhills_athabasca = n.lines_t.p0.iloc[0,21]
hintonedson_wabamun = n.lines_t.p0.iloc[0,22]
athabasca_wabamun = n.lines_t.p0.iloc[0,23]
draytonvalley_wabamun = n.lines_t.p0.iloc[0,24]
hintonedson_draytonvalley = n.lines_t.p0.iloc[0,25]
hintonedson_abrahamlake = n.lines_t.p0.iloc[0,26]
abrahamlake_draytonvalley = n.lines_t.p0.iloc[0,27]
caroline_draytonvalley = n.lines_t.p0.iloc[0,28]
wetaskiwin_draytonvalley = n.lines_t.p0.iloc[0,29]

coldlake_athabasca = n.lines_t.p0.iloc[0,30]
coldlake_vegreville = n.lines_t.p0.iloc[0,31]
coldlake_lloydminster = n.lines_t.p0.iloc[0,32]
fortsask_athabasca = n.lines_t.p0.iloc[0,33]
fortsask_vegreville = n.lines_t.p0.iloc[0,34]
fortsask_edmonton = n.lines_t.p0.iloc[0,35]
fortsask_wetaskiwin = n.lines_t.p0.iloc[0,36]
vegreville_lloydminster = n.lines_t.p0.iloc[0,37]
wainwright_lloydminster = n.lines_t.p0.iloc[0,38]
wainwright_vegreville = n.lines_t.p0.iloc[0,39]

wainwright_alliance = n.lines_t.p0.iloc[0,40]
wetaskiwin_vegreville = n.lines_t.p0.iloc[0,41]
wetaskiwin_edmonton = n.lines_t.p0.iloc[0,42]
wetaskiwin_alliance = n.lines_t.p0.iloc[0,43]
athabasca_edmonton = n.lines_t.p0.iloc[0,44]
wabamun_edmonton = n.lines_t.p0.iloc[0,45]
wabamun_wetaskiwin = n.lines_t.p0.iloc[0,46]
reddeer_wetaskiwin = n.lines_t.p0.iloc[0,47]
reddeer_alliance = n.lines_t.p0.iloc[0,48]
reddeer_hanna = n.lines_t.p0.iloc[0,49]

reddeer_didsbury = n.lines_t.p0.iloc[0,50]
reddeer_caroline = n.lines_t.p0.iloc[0,51]
abrahamlake_caroline = n.lines_t.p0.iloc[0,52]
didsbury_caroline = n.lines_t.p0.iloc[0,53]
alliance_hanna = n.lines_t.p0.iloc[0,54]
alliance_provost = n.lines_t.p0.iloc[0,55]
wainwright_provost = n.lines_t.p0.iloc[0,56]
hanna_provost = n.lines_t.p0.iloc[0,57]
hanna_didsbury = n.lines_t.p0.iloc[0,58]
hanna_airdrie = n.lines_t.p0.iloc[0,59]

hanna_srathmore = n.lines_t.p0.iloc[0,60]
hanna_sheerness = n.lines_t.p0.iloc[0,61]
hanna_empress = n.lines_t.p0.iloc[0,62]
seebe_abrahamlake = n.lines_t.p0.iloc[0,63]
seebe_caroline = n.lines_t.p0.iloc[0,64]
seebe_airdrie = n.lines_t.p0.iloc[0,65]
seebe_calgary =  n.lines_t.p0.iloc[0,66]
seebe_highriver = n.lines_t.p0.iloc[0,67]
airdrie_didsbury = n.lines_t.p0.iloc[0,68]
airdrie_calgary = n.lines_t.p0.iloc[0,69]

srathmore_calgary = n.lines_t.p0.iloc[0,70]
highriver_calgary = n.lines_t.p0.iloc[0,71]
sheerness_empress = n.lines_t.p0.iloc[0,72]
sheerness_brooks = n.lines_t.p0.iloc[0,73]
sheerness_srathmore = n.lines_t.p0.iloc[0,74]
highriver_fortmacleod = n.lines_t.p0.iloc[0,75]
highriver_srathmore = n.lines_t.p0.iloc[0,76]
highriver_stavely = n.lines_t.p0.iloc[0,77]
stavely_srathmore = n.lines_t.p0.iloc[0,78]
brooks_srathmore = n.lines_t.p0.iloc[0,79]

brooks_empress = n.lines_t.p0.iloc[0,80]
brooks_stavely = n.lines_t.p0.iloc[0,81]
brooks_vauxhall = n.lines_t.p0.iloc[0,82]
fortmacleod_stavely = n.lines_t.p0.iloc[0,83]
lethbridge_stavely = n.lines_t.p0.iloc[0,84]
vauxhall_stavely = n.lines_t.p0.iloc[0,85]
vauxhall_medicinehat = n.lines_t.p0.iloc[0,86]
vauxhall_glenwood = n.lines_t.p0.iloc[0,87]
vauxhall_lethbridge = n.lines_t.p0.iloc[0,88]
empress_medicinehat = n.lines_t.p0.iloc[0,89]

glenwood_medicinehat = n.lines_t.p0.iloc[0,90]
fortmacleod_glenwood = n.lines_t.p0.iloc[0,91]
fortmacleod_lethbridge = n.lines_t.p0.iloc[0,92]
lethbridge_glenwood = n.lines_t.p0.iloc[0,93]

#total power that is supplied by parent generation site
lloydminsterpower = n.loads.p_set[0] - (coldlake_lloydminster + wainwright_lloydminster + vegreville_lloydminster)
rainbowlakepower = n.loads.p_set[1] - (highlevel_rainbowlake + (-1*rainbowlake_peaceriver))
highlevelpower = n.loads.p_set[2] - ((-1*highlevel_rainbowlake) + fortmac_highlevel + peaceriver_highlevel)
peaceriverpower = n.loads.p_set[3] - ((rainbowlake_peaceriver) + (-1*peaceriver_highlevel) + (fortmac_peaceriver) + (-1*peaceriver_grandeprairie) +(-1*peaceriver_valleyview) + (-1*peaceriver_highprairie))
grandeprairiepower = n.loads.p_set[4] - ((peaceriver_grandeprairie) + (grandecache_grandeprairie))
highprairiepower = n.loads.p_set[5] - ((fortmac_highprairie) + (peaceriver_highprairie) + (valleyview_highprairie) + (-1*highprairie_swanhills))
grandecachepower = n.loads.p_set[6] - ((-1*grandecache_grandeprairie) + (-1*grandecache_hintonedson) + (-1*grandecache_foxcreek))
valleyviewpower = n.loads.p_set[7] - ((peaceriver_valleyview) + (-1*valleyview_highprairie) + (-1*valleyview_foxcreek) + (-1*valleyview_swanhills))
foxcreekpower = n.loads.p_set[8] - ((valleyview_foxcreek) + (grandecache_foxcreek) + (hintonedson_foxcreek) + (swanhills_foxcreek))
fortmacpower = n.loads.p_set[9] - ((-1*fortmac_highlevel) + (-1*fortmac_highprairie) + (-1*fortmac_peaceriver) + (-1*fortmac_athabasca) + (-1*fortmac_coldlake))
swanhillspower = n.loads.p_set[10] - ((valleyview_swanhills) + (highprairie_swanhills) + (-1*swanhills_foxcreek) + (-1*swanhills_wabamun) + (-1*swanhills_athabasca))
athabascapower = n.loads.p_set[11] - ((fortmac_athabasca) + (swanhills_athabasca) + (-1*athabasca_wabamun) + (coldlake_athabasca) + (fortsask_athabasca) + (-1*athabasca_edmonton))
coldlakepower = n.loads.p_set[12] - ((fortmac_coldlake) + (-1*coldlake_athabasca) + (-1*coldlake_vegreville) + (-1*coldlake_lloydminster))
hintonedsonpower = n.loads.p_set[13] - ((grandecache_hintonedson) + (-1*hintonedson_foxcreek) + (-1*hintonedson_wabamun) + (-1*hintonedson_draytonvalley) + (-1*hintonedson_abrahamlake))
draytonvalleypower = n.loads.p_set[14] - ((-1*draytonvalley_wabamun) + (hintonedson_draytonvalley) + (abrahamlake_draytonvalley) + (caroline_draytonvalley) + (wetaskiwin_draytonvalley))
wetaskiwinpower = n.loads.p_set[15] - ((-1*wetaskiwin_draytonvalley) + (fortsask_wetaskiwin) + (-1*wetaskiwin_vegreville) + (-1*wetaskiwin_edmonton) + (-1*wetaskiwin_alliance) + (wabamun_wetaskiwin) + (reddeer_wetaskiwin))
wainwrightpower = n.loads.p_set[16] - ((-1*wainwright_lloydminster) + (-1*wainwright_vegreville) + (-1*wainwright_alliance) + (-1*wainwright_provost))
fortsaskpower = n.loads.p_set[17] - ((-1*fortsask_athabasca) + (-1*fortsask_vegreville) + (-1*fortsask_edmonton) + (-1*fortsask_wetaskiwin))
abrahamlakepower = n.loads.p_set[18] - ((hintonedson_abrahamlake) + (-1*abrahamlake_draytonvalley) + (-1*abrahamlake_caroline) + (seebe_abrahamlake))
reddeerpower = n.loads.p_set[19] - ((-1*reddeer_wetaskiwin) + (-1*reddeer_alliance) + (-1*reddeer_hanna) + (-1*reddeer_didsbury) + (-1*reddeer_caroline))
alliancepower = n.loads.p_set[20] - ((wainwright_alliance) + (wetaskiwin_alliance) + (reddeer_alliance) + (-1*alliance_hanna) + (-1*alliance_provost))
provostpower = n.loads.p_set[21] - ((alliance_provost) + (wainwright_provost) + (hanna_provost))
carolinepower = n.loads.p_set[22] - ((-1*caroline_draytonvalley) + (reddeer_caroline) + (abrahamlake_caroline) + (didsbury_caroline) + (seebe_caroline))
didsburypower = n.loads.p_set[23] - ((reddeer_didsbury) + (-1*didsbury_caroline) + (hanna_didsbury) + (airdrie_didsbury))
medicinehatpower = n.loads.p_set[24] - ((vauxhall_medicinehat) + (empress_medicinehat) + (glenwood_medicinehat))
wabamunpower = n.loads.p_set[25] - ((swanhills_wabamun) + (hintonedson_wabamun) + (athabasca_wabamun) + (draytonvalley_wabamun) + (-1*wabamun_edmonton) + (-1*wabamun_wetaskiwin))
hannapower = n.loads.p_set[26] - ((reddeer_hanna) + (alliance_hanna) + (-1*hanna_provost) + (-1*hanna_didsbury) + (-1*hanna_airdrie) + (-1*hanna_srathmore) + (-1*hanna_sheerness) + (-1*hanna_empress))
sheernesspower = n.loads.p_set[27] - ((hanna_sheerness) + (-1*sheerness_empress) + (-1*sheerness_brooks) + (-1*sheerness_srathmore))
seebepower = n.loads.p_set[28] - ((-1*seebe_abrahamlake) + (-1*seebe_caroline) + (-1*seebe_airdrie) + (-1*seebe_calgary) + (-1*seebe_highriver))
srathmorepower = n.loads.p_set[29] - ((hanna_srathmore) + (-1*srathmore_calgary) + (sheerness_srathmore) + (highriver_srathmore) + (stavely_srathmore) + (brooks_srathmore))
highriverpower = n.loads.p_set[30] - ((seebe_highriver) + (-1*highriver_calgary) + (-1*highriver_fortmacleod) + (-1*highriver_srathmore) + (-1*highriver_stavely))
brookspower = n.loads.p_set[31] - ((sheerness_brooks) + (-1*brooks_srathmore) + (-1*brooks_empress) + (-1*brooks_stavely) + (-1*brooks_vauxhall))
empresspower = n.loads.p_set[32] - ((hanna_empress) + (sheerness_empress) + (brooks_empress) + (-1*empress_medicinehat))
stavelypower = n.loads.p_set[33] - ((highriver_stavely) + (-1*stavely_srathmore) + (brooks_stavely) + (fortmacleod_stavely) + (lethbridge_stavely) + (vauxhall_stavely))
vauxhallpower = n.loads.p_set[34] - ((brooks_vauxhall) + (-1*vauxhall_stavely) + (-1*vauxhall_medicinehat) + (-1*vauxhall_glenwood) + (-1*vauxhall_lethbridge))
fortmacleodpower = n.loads.p_set[35] - ((highriver_fortmacleod) + (-1*fortmacleod_stavely) + (-1*fortmacleod_glenwood) + (-1*fortmacleod_lethbridge))
lethbridgepower = n.loads.p_set[36] - ((-1*lethbridge_stavely) + (vauxhall_lethbridge) + (fortmacleod_lethbridge) + (-1*lethbridge_glenwood))
glenwoodpower = n.loads.p_set[37] - ((vauxhall_glenwood) + (-1*glenwood_medicinehat) + (fortmacleod_glenwood) + (lethbridge_glenwood))
vegrevillepower = n.loads.p_set[38] - ((coldlake_vegreville) + (fortsask_vegreville) + (-1*vegreville_lloydminster) + (wainwright_vegreville) + (wetaskiwin_vegreville))
airdriepower = n.loads.p_set[39] - ((hanna_airdrie) + (seebe_airdrie) + (-1*airdrie_didsbury) + (-1*airdrie_calgary))
calgarypower = n.loads.p_set[40] - ((seebe_calgary) + (airdrie_calgary) + (srathmore_calgary) + (highriver_calgary))
edmontonpower = n.loads.p_set[41] - ((fortsask_edmonton) + (wetaskiwin_edmonton) + (athabasca_edmonton) + (wabamun_edmonton))

#solar percentage for Lloydminster
if coldlake_lloydminster < 0:
    coldlake_lloydminster = 0
if wainwright_lloydminster < 0:
    wainwright_lloydminster = 0
if vegreville_lloydminster < 0: 
    vegreville_lloydminster = 0
solar_percentage_lloydminster = 100*(((lloydminsterpower*lloydminster_percentage) + (cold_lake_percentage*coldlake_lloydminster) + (wainwright_percentage*wainwright_lloydminster) + (vegreville_percentage*vegreville_lloydminster))/(n.loads.p_set[0]))
if solar_percentage_lloydminster > 100:
    solar_percentage_lloydminster = 100
coldlake_lloydminster = n.lines_t.p0.iloc[0,32]
wainwright_lloydminster = n.lines_t.p0.iloc[0,38]
vegreville_lloydminster = n.lines_t.p0.iloc[0,37]

#solar percentage for Rainbow Lake
if highlevel_rainbowlake < 0:
    highlevel_rainbowlake = 0
if rainbowlake_peaceriver > 0:
    rainbowlake_peaceriver = 0
solar_percentage_rainbowlake = 100*(((rainbowlakepower*rainbow_lake_percentage) + (high_level_percentage*highlevel_rainbowlake) + (peace_river_percentage*(-1*rainbowlake_peaceriver)))/(n.loads.p_set[1]))
if solar_percentage_rainbowlake > 100:
    solar_percentage_rainbowlake = 100
highlevel_rainbowlake = n.lines_t.p0.iloc[0,0]
rainbowlake_peaceriver = n.lines_t.p0.iloc[0,1]

#solar percentage for High Level
if highlevel_rainbowlake > 0:
    highlevel_rainbowlake = 0
if fortmac_highlevel < 0:
    fortmac_highlevel = 0
if peaceriver_highlevel < 0:
    peaceriver_highlevel = 0
solar_percentage_highlevel = 100*(((highlevelpower*high_level_percentage) + (rainbow_lake_percentage*(-1*highlevel_rainbowlake)) + (fort_mac_percentage*fortmac_highlevel) + (peace_river_percentage*peaceriver_highlevel))/(n.loads.p_set[2]))
if solar_percentage_highlevel > 100:
    solar_percentage_highlevel = 100
highlevel_rainbowlake = n.lines_t.p0.iloc[0,0]
fortmac_highlevel = n.lines_t.p0.iloc[0,2]
peaceriver_highlevel = n.lines_t.p0.iloc[0,3]

#solar percentage for Peace River
if rainbowlake_peaceriver < 0:
    rainbowlake_peaceriver = 0
if peaceriver_highlevel > 0:
    peaceriver_highlevel = 0
if fortmac_peaceriver < 0:
    fortmac_peaceriver = 0
if peaceriver_grandeprairie > 0:
    peaceriver_grandeprairie = 0
if peaceriver_valleyview > 0:
    peaceriver_valleyview = 0
if peaceriver_highprairie > 0:
    peaceriver_highprairie = 0
solar_percentage_peaceriver = 100*(((peace_river_percentage*peaceriverpower) + (rainbow_lake_percentage*rainbowlake_peaceriver) + (high_level_percentage*(-1*peaceriver_highlevel)) + (fort_mac_percentage*fortmac_peaceriver) + (grande_prairie_percentage*(-1*peaceriver_grandeprairie)) + (valleyview_percentage*(-1*peaceriver_valleyview)) + (high_prairie_percentage*(-1*peaceriver_highprairie)))/(n.loads.p_set[3]))
if solar_percentage_peaceriver > 100:
    solar_percentage_peaceriver = 100
rainbowlake_peaceriver = n.lines_t.p0.iloc[0,1]
peaceriver_highlevel = n.lines_t.p0.iloc[0,3]
fortmac_peaceriver = n.lines_t.p0.iloc[0,5]
peaceriver_grandeprairie = n.lines_t.p0.iloc[0,6]
peaceriver_valleyview = n.lines_t.p0.iloc[0,7]
peaceriver_highprairie = n.lines_t.p0.iloc[0,8]

#solar percentage for Grande Prairie
if peaceriver_grandeprairie < 0:
    peaceriver_grandeprairie = 0
if grandecache_grandeprairie < 0:
    grandecache_grandeprairie = 0
solar_percentage_grandeprairie = 100*(((grande_prairie_percentage*grandeprairiepower) + (peace_river_percentage*peaceriver_grandeprairie) + (grande_cache_percentage*grandecache_grandeprairie))/(n.loads.p_set[4]))
if solar_percentage_grandeprairie > 100:
    solar_percentage_grandeprairie = 100
peaceriver_grandeprairie = n.lines_t.p0.iloc[0,6]
grandecache_grandeprairie = n.lines_t.p0.iloc[0,9]

#solar percentage High Prairie 
if fortmac_highprairie < 0:
    fortmac_highprairie = 0
if peaceriver_highprairie < 0:
    peaceriver_highprairie = 0
if valleyview_highprairie < 0:
    valleyview_highprairie = 0
if highprairie_swanhills > 0:
    highprairie_swanhills = 0
solar_percentage_highprairie = 100*(((high_prairie_percentage*highprairiepower) + (fort_mac_percentage*fortmac_highprairie) + (peace_river_percentage*peaceriver_highprairie) + (valleyview_percentage*valleyview_highprairie) + (swan_hills_percentage*(-1*highprairie_swanhills)))/(n.loads.p_set[5]))
if solar_percentage_highprairie > 100:
    solar_percentage_highprairie = 100
fortmac_highprairie = n.lines_t.p0.iloc[0,4]
peaceriver_highprairie = n.lines_t.p0.iloc[0,8]
valleyview_highprairie = n.lines_t.p0.iloc[0,10]
highprairie_swanhills = n.lines_t.p0.iloc[0,17]

#solar percentage of Grande Cache
if grandecache_grandeprairie > 0:
    grandecache_grandeprairie = 0
if grandecache_hintonedson > 0:
    grandecache_hintonedson = 0
if grandecache_foxcreek > 0:
    grandecache_foxcreek = 0
solar_percentage_grandecache = 100*(((grande_cache_percentage*grandecachepower) + (grande_prairie_percentage*(-1*grandecache_grandeprairie)) + (hinton_edson_percentage*(-1*grandecache_hintonedson)) + (fox_creek_percentage*(-1*grandecache_foxcreek)))/(n.loads.p_set[6]))
if solar_percentage_grandecache > 100:
    solar_percentage_grandecache = 100
grandecache_grandeprairie = n.lines_t.p0.iloc[0,9]
grandecache_hintonedson = n.lines_t.p0.iloc[0,15]
grandecache_foxcreek = n.lines_t.p0.iloc[0,16]

#solar percentage of Valleyview
if peaceriver_valleyview < 0:
    peaceriver_valleyview = 0
if valleyview_highprairie > 0:
    valleyview_highprairie = 0
if valleyview_foxcreek > 0:
    valleyview_foxcreek = 0
if valleyview_swanhills > 0:
    valleyview_swanhills = 0
solar_percentage_valleyview = 100*(((valleyview_percentage*valleyviewpower) + (peace_river_percentage*peaceriver_valleyview) + (high_prairie_percentage*(-1*valleyview_highprairie)) + (fox_creek_percentage*(-1*valleyview_foxcreek)) + (swan_hills_percentage*(-1*valleyview_swanhills)))/(n.loads.p_set[7]))
if solar_percentage_valleyview > 100:
    solar_percentage_valleyview = 100
peaceriver_valleyview = n.lines_t.p0.iloc[0,7]
valleyview_highprairie = n.lines_t.p0.iloc[0,10]
valleyview_foxcreek = n.lines_t.p0.iloc[0,11]
valleyview_swanhills = n.lines_t.p0.iloc[0,12]

#solar percentage of Fox Creek
if valleyview_foxcreek < 0:
    valleyview_foxcreek = 0
if grandecache_foxcreek < 0:
    grandecache_foxcreek = 0
if hintonedson_foxcreek < 0:
    hintonedson_foxcreek = 0
if swanhills_foxcreek < 0:
    swanhills_foxcreek = 0
solar_percentage_foxcreek = 100*(((fox_creek_percentage*foxcreekpower) + (valleyview_percentage*valleyview_foxcreek) + (grande_cache_percentage*grandecache_foxcreek) + (hinton_edson_percentage*hintonedson_foxcreek) + (swan_hills_percentage*swanhills_foxcreek))/(n.loads.p_set[8]))
if solar_percentage_foxcreek > 100:
    solar_percentage_foxcreek = 100
valleyview_foxcreek = n.lines_t.p0.iloc[0,11]
grandecache_foxcreek = n.lines_t.p0.iloc[0,16]
hintonedson_foxcreek = n.lines_t.p0.iloc[0,18]
swanhills_foxcreek = n.lines_t.p0.iloc[0,19]

#solar percentage of Fort Mac
if fortmac_highlevel > 0:
    fortmac_highlevel = 0
if fortmac_highprairie > 0:
    fortmac_highprairie = 0
if fortmac_peaceriver > 0:
    fortmac_peaceriver = 0
if fortmac_athabasca > 0:
    fortmac_athabasca = 0
if fortmac_coldlake > 0:
    fortmac_coldlake = 0
solar_percentage_fortmac = 100*(((fort_mac_percentage*fortmacpower) + (high_level_percentage*(-1*fortmac_highlevel)) + (high_prairie_percentage*(-1*fortmac_highprairie)) + (peace_river_percentage*(-1*fortmac_peaceriver)) + (athabasca_percentage*(-1*fortmac_athabasca)) + (cold_lake_percentage*(-1*fortmac_coldlake)))/(n.loads.p_set[9]))
if solar_percentage_fortmac > 100:
    solar_percentage_fortmac = 100
fortmac_highlevel = n.lines_t.p0.iloc[0,2]
fortmac_highprairie = n.lines_t.p0.iloc[0,4]
fortmac_peaceriver = n.lines_t.p0.iloc[0,5]
fortmac_athabasca = n.lines_t.p0.iloc[0,13]
fortmac_coldlake = n.lines_t.p0.iloc[0,14]

#solar percentage of Swan Hills
if valleyview_swanhills < 0:
    valleyview_swanhills = 0
if highprairie_swanhills < 0:
    highprairie_swanhills = 0
if swanhills_foxcreek > 0:
    swanhills_foxcreek = 0
if swanhills_wabamun > 0:
    swanhills_wabamun = 0
if swanhills_athabasca > 0:
    swanhills_athabasca = 0
solar_percentage_swanhills = 100*(((swan_hills_percentage*swanhillspower) + (valleyview_percentage*valleyview_swanhills) + (high_prairie_percentage*highprairie_swanhills) + (fox_creek_percentage*(-1*swanhills_foxcreek)) + (wabamun_percentage*(-1*swanhills_wabamun)) + (athabasca_percentage*(-1*swanhills_athabasca)))/(n.loads.p_set[10]))
if solar_percentage_swanhills > 100:
    solar_percentage_swanhills = 100
valleyview_swanhills = n.lines_t.p0.iloc[0,12]
highprairie_swanhills = n.lines_t.p0.iloc[0,17]
swanhills_foxcreek = n.lines_t.p0.iloc[0,19]
swanhills_wabamun = n.lines_t.p0.iloc[0,20]
swanhills_athabasca = n.lines_t.p0.iloc[0,21]


#solar percentage of Athabasca
if fortmac_athabasca < 0:
    fortmac_athabasca = 0
if swanhills_athabasca < 0:
    swanhills_athabasca = 0
if athabasca_wabamun > 0:
    athabasca_wabamun = 0
if coldlake_athabasca < 0:
    coldlake_athabasca = 0
if fortsask_athabasca < 0:
    fortsask_athabasca = 0
if athabasca_edmonton > 0:
    athabasca_edmonton = 0
solar_percentage_athabasca = 100*(((athabasca_percentage*athabascapower) + (fort_mac_percentage*fortmac_athabasca) + (swan_hills_percentage*swanhills_athabasca) + (athabasca_percentage*(-1*athabasca_wabamun)) + (cold_lake_percentage*coldlake_athabasca) + (fort_sask_percentage*fortsask_athabasca) + (edmonton_percentage*(-1*athabasca_edmonton)))/(n.loads.p_set[11]))
if solar_percentage_athabasca > 100:
    solar_percentage_athabasca = 100
fortmac_athabasca = n.lines_t.p0.iloc[0,13]
swanhills_athabasca = n.lines_t.p0.iloc[0,21]
athabasca_wabamun = n.lines_t.p0.iloc[0,23]
coldlake_athabasca = n.lines_t.p0.iloc[0,30]
fortsask_athabasca = n.lines_t.p0.iloc[0,33]
athabasca_edmonton = n.lines_t.p0.iloc[0,44]

#solar percentage of Cold Lake
if fortmac_coldlake < 0:
    fortmac_coldlake = 0
if coldlake_athabasca > 0:
    coldlake_athabasca = 0
if coldlake_vegreville > 0:
    coldlake_vegreville = 0
if coldlake_lloydminster > 0:
    coldlake_lloydminster = 0
solar_percentage_coldlake = 100*(((cold_lake_percentage*coldlakepower) + (fort_mac_percentage*fortmac_coldlake) + (athabasca_percentage*(-1*coldlake_athabasca)) + (vegreville_percentage*(-1*coldlake_vegreville)) + (lloydminster_percentage*(-1*coldlake_lloydminster)))/(n.loads.p_set[12]))
if solar_percentage_coldlake > 100:
    solar_percentage_coldlake = 100
fortmac_coldlake = n.lines_t.p0.iloc[0,14]
coldlake_athabasca = n.lines_t.p0.iloc[0,30]
coldlake_vegreville = n.lines_t.p0.iloc[0,31]
coldlake_lloydminster = n.lines_t.p0.iloc[0,32]

#solar percentage of Hinton/Edson
if grandecache_hintonedson < 0:
    grandecache_hintonedson = 0
if hintonedson_foxcreek > 0:
    hintonedson_foxcreek = 0
if hintonedson_wabamun > 0:
    hintonedson_wabamun = 0
if hintonedson_draytonvalley > 0:
    hintonedson_draytonvalley = 0
if hintonedson_abrahamlake > 0:
    hintonedson_abrahamlake = 0
solar_percentage_hintonedson = 100*(((hinton_edson_percentage*hintonedsonpower) + (grande_cache_percentage*grandecache_hintonedson) + (fox_creek_percentage*(-1*hintonedson_foxcreek)) + (wabamun_percentage*(-1*hintonedson_wabamun)) + (drayton_valley_percentage*(-1*hintonedson_draytonvalley)) + (abraham_lake_percentage*(-1*hintonedson_abrahamlake)))/(n.loads.p_set[13]))
if solar_percentage_hintonedson > 100:
    solar_percentage_hintonedson = 100
grandecache_hintonedson = n.lines_t.p0.iloc[0,15]
hintonedson_foxcreek = n.lines_t.p0.iloc[0,18]
hintonedson_wabamun = n.lines_t.p0.iloc[0,22]
hintonedson_draytonvalley = n.lines_t.p0.iloc[0,25]
hintonedson_abrahamlake = n.lines_t.p0.iloc[0,26]

#solar percentage of Drayton Valley
if draytonvalley_wabamun < 0:
    draytonvalley_wabamun = 0
if hintonedson_draytonvalley < 0:
    hintonedson_draytonvalley = 0
if abrahamlake_draytonvalley < 0:
    abrahamlake_draytonvalley = 0
if caroline_draytonvalley < 0:
    caroline_draytonvalley = 0
if wetaskiwin_draytonvalley < 0:
    wetaskiwin_draytonvalley = 0
solar_percentage_draytonvalley = 100*(((drayton_valley_percentage*draytonvalleypower) + (wabamun_percentage*(-1*draytonvalley_wabamun)) + (hinton_edson_percentage*hintonedson_draytonvalley) + (abraham_lake_percentage*abrahamlake_draytonvalley) + (caroline_percentage*caroline_draytonvalley) + (wetaskiwin_percentage*wetaskiwin_draytonvalley))/(n.loads.p_set[14]))
if solar_percentage_draytonvalley > 100:
    solar_percentage_draytonvalley = 100
draytonvalley_wabamun = n.lines_t.p0.iloc[0,24]
hintonedson_draytonvalley = n.lines_t.p0.iloc[0,25]
abrahamlake_draytonvalley = n.lines_t.p0.iloc[0,27]
caroline_draytonvalley = n.lines_t.p0.iloc[0,28]
wetaskiwin_draytonvalley = n.lines_t.p0.iloc[0,29]

#solar percentage of wetaskiwin
if wetaskiwin_draytonvalley > 0:
    wetaskiwin_draytonvalley = 0
if fortsask_wetaskiwin < 0:
    fortsask_wetaskiwin = 0
if wetaskiwin_vegreville > 0:
    wetaskiwin_vegreville = 0
if wetaskiwin_edmonton > 0:
    wetaskiwin_edmonton = 0
if wetaskiwin_alliance > 0:
    wetaskiwin_alliance = 0
if wabamun_wetaskiwin < 0:
    wabamun_wetaskiwin = 0
if reddeer_wetaskiwin < 0:
    reddeer_wetaskiwin = 0
solar_percentage_wetaskiwin = 100*(((wetaskiwin_percentage*wetaskiwinpower) + (drayton_valley_percentage*(-1*wetaskiwin_draytonvalley)) + (fort_sask_percentage*fortsask_wetaskiwin) + (vegreville_percentage*(-1*wetaskiwin_vegreville)) + (edmonton_percentage*(-1*wetaskiwin_edmonton)) + (alliance_battle_river_percentage*(-1*wetaskiwin_alliance)) + (wabamun_percentage*wabamun_wetaskiwin) + (red_deer_percentage*reddeer_wetaskiwin))/(n.loads.p_set[15]))
if solar_percentage_wetaskiwin > 100:
    solar_percentage_wetaskiwin = 100
wetaskiwin_draytonvalley = n.lines_t.p0.iloc[0,29]
fortsask_wetaskiwin = n.lines_t.p0.iloc[0,36]
wetaskiwin_vegreville = n.lines_t.p0.iloc[0,41]
wetaskiwin_edmonton = n.lines_t.p0.iloc[0,42]
wetaskiwin_alliance = n.lines_t.p0.iloc[0,43]
wabamun_wetaskiwin = n.lines_t.p0.iloc[0,46]
reddeer_wetaskiwin = n.lines_t.p0.iloc[0,47]

#solar percentage of Wainwright
if wainwright_lloydminster > 0:
    wainwright_lloydminster = 0
if wainwright_vegreville > 0:
    wainwright_vegreville = 0
if wainwright_alliance > 0:
    wainwright_alliance = 0
if wainwright_provost > 0:
    wainwright_provost = 0
solar_percentage_wainwright = 100*(((wainwright_percentage*wainwrightpower) + (lloydminster_percentage*(-1*wainwright_lloydminster)) + (vegreville_percentage*(-1*wainwright_vegreville)) + (alliance_battle_river_percentage*(-1*wainwright_alliance)) + (provost_percentage*(-1*wainwright_provost)))/(n.loads.p_set[16]))
if solar_percentage_wainwright > 100:
    solar_percentage_wainwright = 100
wainwright_lloydminster = n.lines_t.p0.iloc[0,38]
wainwright_vegreville = n.lines_t.p0.iloc[0,39]
wainwright_alliance = n.lines_t.p0.iloc[0,40]
wainwright_provost = n.lines_t.p0.iloc[0,56]

#solar percentage of Fort Sask
if fortsask_athabasca > 0:
    fortsask_athabasca = 0
if fortsask_vegreville > 0:
    fortsask_vegreville = 0
if fortsask_edmonton > 0:
    fortsask_edmonton = 0
if fortsask_wetaskiwin > 0:
    fortsask_wetaskiwin = 0
solar_percentage_fortsask = 100*(((fort_sask_percentage*fortsaskpower) + (athabasca_percentage*(-1*fortsask_athabasca)) + (vegreville_percentage*(-1*fortsask_vegreville)) + (edmonton_percentage*(-1*fortsask_edmonton)) + (wetaskiwin_percentage*(-1*fortsask_wetaskiwin)))/n.loads.p_set[17])
if solar_percentage_fortsask > 100:
    solar_percentage_fortsask = 100
fortsask_athabasca = n.lines_t.p0.iloc[0,33]
fortsask_vegreville = n.lines_t.p0.iloc[0,34]
fortsask_edmonton = n.lines_t.p0.iloc[0,35]
fortsask_wetaskiwin = n.lines_t.p0.iloc[0,36]

#solar percentage of Abraham Lake 
if hintonedson_abrahamlake < 0:
    hintonedson_abrahamlake
if abrahamlake_draytonvalley > 0:
    abrahamlake_draytonvalley = 0
if abrahamlake_caroline > 0:
    abrahamlake_caroline = 0
if seebe_abrahamlake < 0:
    seebe_abrahamlake = 0
solar_percentage_abrahamlake = 100*(((abraham_lake_percentage*abrahamlakepower) + (hinton_edson_percentage*hintonedson_abrahamlake) + (drayton_valley_percentage*(-1*abrahamlake_draytonvalley)) + (caroline_percentage*(-1*abrahamlake_caroline)) + (seebe_percentage*seebe_abrahamlake))/n.loads.p_set[18])
if solar_percentage_abrahamlake > 100:
    solar_percentage_abrahamlake = 100
hintonedson_abrahamlake = n.lines_t.p0.iloc[0,26]
abrahamlake_draytonvalley = n.lines_t.p0.iloc[0,27]
abrahamlake_caroline = n.lines_t.p0.iloc[0,52]
seebe_abrahamlake = n.lines_t.p0.iloc[0,63]

#solar percentage of Red Deer 
if reddeer_wetaskiwin > 0:
    reddeer_wetaskiwin = 0
if reddeer_alliance > 0:
    reddeer_alliance = 0
if reddeer_hanna > 0:
    reddeer_hanna = 0
if reddeer_didsbury > 0:
    reddeer_didsbury = 0
if reddeer_caroline > 0:
    reddeer_caroline = 0
solar_percentage_reddeer = 100*(((red_deer_percentage*reddeerpower) + (wetaskiwin_percentage*(-1*reddeer_wetaskiwin)) + (alliance_battle_river_percentage*(-1*reddeer_alliance)) + (hanna_percentage*(-1*reddeer_hanna)) + (didsbury_percentage*(-1*reddeer_didsbury)) + (caroline_percentage*(-1*reddeer_caroline)))/n.loads.p_set[19])
if solar_percentage_reddeer > 100:
    solar_percentage_reddeer = 100
reddeer_wetaskiwin = n.lines_t.p0.iloc[0,47]
reddeer_alliance = n.lines_t.p0.iloc[0,48]
reddeer_hanna = n.lines_t.p0.iloc[0,49]
reddeer_didsbury = n.lines_t.p0.iloc[0,50]
reddeer_caroline = n.lines_t.p0.iloc[0,51]

#solar percentage of Alliance/Battle River
if wainwright_alliance < 0:
    wainwright_alliance = 0
if wetaskiwin_alliance < 0:
    wetaskiwin_alliance = 0
if reddeer_alliance < 0:
    reddeer_alliance = 0
if alliance_hanna > 0:
    alliance_hanna = 0
if alliance_provost > 0:
    alliance_provost = 0
solar_percentage_alliance = 100*(((alliance_battle_river_percentage*alliancepower) + (wainwright_percentage*wainwright_alliance) + (wetaskiwin_percentage*wetaskiwin_alliance) + (red_deer_percentage*reddeer_alliance) + (hanna_percentage*(-1*alliance_hanna)) + (provost_percentage*(-1*alliance_provost)))/n.loads.p_set[20])
if solar_percentage_alliance > 100:
    solar_percentage_alliance = 100
wainwright_alliance = n.lines_t.p0.iloc[0,40]
wetaskiwin_alliance = n.lines_t.p0.iloc[0,43]
reddeer_alliance = n.lines_t.p0.iloc[0,48]
alliance_hanna = n.lines_t.p0.iloc[0,54]
alliance_provost = n.lines_t.p0.iloc[0,55]

#solar percentage of Provost
if alliance_provost < 0:
    alliance_provost = 0
if wainwright_provost < 0:
    wainwright_provost = 0
if hanna_provost < 0:
    hanna_provost = 0
solar_percentage_provost = 100*(((provost_percentage*provostpower) + (alliance_battle_river_percentage*alliance_provost) + (wainwright_percentage*wainwright_provost) + (hanna_percentage*hanna_provost))/n.loads.p_set[21])
if solar_percentage_provost > 100:
    solar_percentage_provost = 100
alliance_provost = n.lines_t.p0.iloc[0,55]
wainwright_provost = n.lines_t.p0.iloc[0,56]
hanna_provost = n.lines_t.p0.iloc[0,57]

#solar percentage of Caroline
if caroline_draytonvalley > 0:
    caroline_draytonvalley = 0
if reddeer_caroline < 0:
    reddeer_caroline = 0
if abrahamlake_caroline < 0:
    abrahamlake_caroline = 0
if didsbury_caroline < 0:
    didsbury_caroline = 0
if seebe_caroline < 0:
    seebe_caroline = 0
solar_percentage_caroline = 100*(((caroline_percentage*carolinepower) + (drayton_valley_percentage*(-1*caroline_draytonvalley)) + (red_deer_percentage*reddeer_caroline) + (abraham_lake_percentage*abrahamlake_caroline) + (didsbury_percentage*didsbury_caroline) + (seebe_percentage*seebe_caroline))/n.loads.p_set[22])
if solar_percentage_caroline > 100:
    solar_percentage_caroline = 100
caroline_draytonvalley = n.lines_t.p0.iloc[0,28]
reddeer_caroline = n.lines_t.p0.iloc[0,51]
abrahamlake_caroline = n.lines_t.p0.iloc[0,52]
didsbury_caroline = n.lines_t.p0.iloc[0,53]
seebe_caroline = n.lines_t.p0.iloc[0,64]

#solar percentage of Didsbury
if reddeer_didsbury < 0:
    reddeer_didsbury = 0
if didsbury_caroline > 0:
    didsbury_caroline = 0
if hanna_didsbury < 0:
    hanna_didsbury = 0
if airdrie_didsbury < 0:
    airdrie_didsbury = 0
solar_percentage_didsbury = 100*(((didsbury_percentage*didsburypower) + (red_deer_percentage*reddeer_didsbury) + (caroline_percentage*(-1*didsbury_caroline)) + (hanna_percentage*hanna_didsbury) + (airdrie_percentage*airdrie_didsbury))/n.loads.p_set[23])
if solar_percentage_didsbury > 100:
    solar_percentage_didsbury = 100
reddeer_didsbury = n.lines_t.p0.iloc[0,50]
didsbury_caroline = n.lines_t.p0.iloc[0,53]
hanna_didsbury = n.lines_t.p0.iloc[0,58]
airdrie_didsbury = n.lines_t.p0.iloc[0,68]

#solar percentage of Medicine Hat
if vauxhall_medicinehat < 0:
    vauxhall_medicinehat = 0
if empress_medicinehat < 0:
    empress_medicinehat = 0
if glenwood_medicinehat < 0:
    glenwood_medicinehat = 0
solar_percentage_medicinehat = 100*(((medicine_hat_percentage*medicinehatpower) + (vauxhall_percentage*vauxhall_medicinehat) + (empress_percentage*empress_medicinehat) + (glenwood_percentage*glenwood_medicinehat))/n.loads.p_set[24])
if solar_percentage_medicinehat > 100:
    solar_percentage_medicinehat = 100
vauxhall_medicinehat = n.lines_t.p0.iloc[0,86]
empress_medicinehat = n.lines_t.p0.iloc[0,89]
glenwood_medicinehat = n.lines_t.p0.iloc[0,90]

#solar percentage of Wabamun
if swanhills_wabamun < 0:
    swanhills_wabamun = 0
if hintonedson_wabamun < 0:
    hintonedson_wabamun = 0
if athabasca_wabamun < 0:
    athabasca_wabamun = 0
if draytonvalley_wabamun < 0:
    draytonvalley_wabamun = 0
if wabamun_edmonton > 0:
    wabamun_edmonton = 0
if wabamun_wetaskiwin > 0:
    wabamun_wetaskiwin = 0
solar_percentage_wabamun = 100*(((wabamun_percentage*wabamunpower) + (swan_hills_percentage*swanhills_wabamun) + (hinton_edson_percentage*hintonedson_wabamun) + (athabasca_percentage*athabasca_wabamun) + (drayton_valley_percentage*draytonvalley_wabamun) + (edmonton_percentage*(-1*wabamun_edmonton)) + (wetaskiwin_percentage*(-1*wabamun_wetaskiwin)))/n.loads.p_set[25])
if solar_percentage_wabamun > 100:
    solar_percentage_wabamun = 100
swanhills_wabamun = n.lines_t.p0.iloc[0,20]
hintonedson_wabamun = n.lines_t.p0.iloc[0,22]
athabasca_wabamun = n.lines_t.p0.iloc[0,23]
draytonvalley_wabamun = n.lines_t.p0.iloc[0,24]
wabamun_edmonton = n.lines_t.p0.iloc[0,45]
wabamun_wetaskiwin = n.lines_t.p0.iloc[0,46]

#solar percentage of Hanna 
if reddeer_hanna < 0:
    reddeer_hanna = 0
if alliance_hanna < 0:
    alliance_hanna = 0
if hanna_provost > 0:
    hanna_provost = 0
if hanna_didsbury > 0:
    hanna_didsbury = 0
if hanna_airdrie > 0:
    hanna_airdrie = 0
if hanna_srathmore > 0:
    hanna_srathmore = 0
if hanna_sheerness > 0:
    hanna_sheerness = 0
if hanna_empress > 0:
    hanna_empress = 0
solar_percentage_hanna = 100*(((hanna_percentage*hannapower) + (red_deer_percentage*reddeer_hanna) + (alliance_battle_river_percentage*alliance_hanna) + (provost_percentage*(-1*hanna_provost)) + (didsbury_percentage*(-1*hanna_didsbury)) + (airdrie_percentage*(-1*hanna_airdrie)) + (srathmore_blackie_percentage*(-1*hanna_srathmore)) + (sheerness_percentage*(-1*hanna_sheerness)) + (empress_percentage*(-1*hanna_empress)))/n.loads.p_set[26])
if solar_percentage_hanna > 100:
    solar_percentage_hanna = 100
reddeer_hanna = n.lines_t.p0.iloc[0,49]
alliance_hanna = n.lines_t.p0.iloc[0,54]
hanna_provost = n.lines_t.p0.iloc[0,57]
hanna_didsbury = n.lines_t.p0.iloc[0,58]
hanna_airdrie = n.lines_t.p0.iloc[0,59]
hanna_srathmore = n.lines_t.p0.iloc[0,60]
hanna_sheerness = n.lines_t.p0.iloc[0,61]
hanna_empress = n.lines_t.p0.iloc[0,62]

#solar percentage of Sheerness
if hanna_sheerness < 0:
    hanna_sheerness = 0
if sheerness_empress > 0:
    sheerness_empress = 0
if sheerness_brooks > 0:
    sheerness_brooks = 0
if sheerness_srathmore > 0:
    sheerness_srathmore = 0
solar_percentage_sheerness = 100*(((sheerness_percentage*sheernesspower) + (hanna_percentage*hanna_sheerness) + (empress_percentage*(-1*sheerness_empress)) + (brooks_percentage*(-1*sheerness_brooks)) + (srathmore_blackie_percentage*(-1*sheerness_srathmore)))/n.loads.p_set[27])
if solar_percentage_sheerness > 100:
    solar_percentage_sheerness = 100
hanna_sheerness = n.lines_t.p0.iloc[0,61]
sheerness_empress = n.lines_t.p0.iloc[0,72]
sheerness_brooks = n.lines_t.p0.iloc[0,73]
sheerness_srathmore = n.lines_t.p0.iloc[0,74]

#solar percentage of Seebe
if seebe_abrahamlake > 0:
    seebe_abrahamlake = 0
if seebe_caroline > 0:
    seebe_caroline = 0
if seebe_airdrie > 0:
    seebe_airdrie = 0
if seebe_calgary > 0: 
    seebe_calgary = 0
if seebe_highriver > 0:
    seebe_highriver = 0
solar_percentage_seebe = 100*(((seebe_percentage*seebepower) + (abraham_lake_percentage*(-1*seebe_abrahamlake)) + (caroline_percentage*(-1*seebe_caroline)) + (airdrie_percentage*(-1*seebe_airdrie)) + (calgary_percentage*(-1*seebe_calgary)) + (high_river_percentage*(-1*seebe_highriver)))/n.loads.p_set[28])
if solar_percentage_seebe > 100:
    solar_percentage_seebe = 100
seebe_abrahamlake = n.lines_t.p0.iloc[0,63]
seebe_caroline = n.lines_t.p0.iloc[0,64]
seebe_airdrie = n.lines_t.p0.iloc[0,65]
seebe_calgary =  n.lines_t.p0.iloc[0,66]
seebe_highriver = n.lines_t.p0.iloc[0,67]

#solar percentage of Srathmore
if hanna_srathmore < 0:
    hanna_srathmore = 0
if srathmore_calgary > 0:
    srathmore_calgary = 0
if sheerness_srathmore < 0:
    sheerness_srathmore = 0
if highriver_srathmore < 0:
    highriver_srathmore = 0
if stavely_srathmore < 0:
    stavely_srathmore = 0
if brooks_srathmore < 0:
    brooks_srathmore = 0
solar_percentage_srathmore = 100*(((srathmore_blackie_percentage*srathmorepower) + (hanna_percentage*hanna_srathmore) + (calgary_percentage*(-1*srathmore_calgary)) + (sheerness_percentage*sheerness_srathmore) + (high_level_percentage*highriver_srathmore) + (stavely_percentage*stavely_srathmore) + (brooks_percentage*brooks_srathmore))/n.loads.p_set[29])
if solar_percentage_srathmore > 100:
    solar_percentage_srathmore = 100
hanna_srathmore = n.lines_t.p0.iloc[0,60]
srathmore_calgary = n.lines_t.p0.iloc[0,70]
sheerness_srathmore = n.lines_t.p0.iloc[0,74]
highriver_srathmore = n.lines_t.p0.iloc[0,76]
stavely_srathmore = n.lines_t.p0.iloc[0,78]
brooks_srathmore = n.lines_t.p0.iloc[0,79]

#solar percentage of High River
if seebe_highriver < 0:
    seebe_highriver = 0
if highriver_calgary > 0:
    highriver_calgary = 0
if highriver_fortmacleod > 0:
    highriver_fortmacleod = 0
if highriver_srathmore > 0:
    highriver_srathmore = 0
if highriver_stavely > 0:
    highriver_stavely = 0
solar_percentage_highriver = 100*(((high_river_percentage*highriverpower) + (seebe_percentage*seebe_highriver) + (calgary_percentage*(-1*highriver_calgary)) + (fort_macleod_percentage*(-1*highriver_fortmacleod)) + (srathmore_blackie_percentage*(-1*highriver_srathmore)) + (stavely_percentage*(-1*highriver_stavely)))/n.loads.p_set[30])
if solar_percentage_highriver > 100:
    solar_percentage_highriver = 100
seebe_highriver = n.lines_t.p0.iloc[0,67]
highriver_calgary = n.lines_t.p0.iloc[0,71]
highriver_fortmacleod = n.lines_t.p0.iloc[0,75]
highriver_srathmore = n.lines_t.p0.iloc[0,76]
highriver_stavely = n.lines_t.p0.iloc[0,77]

#solar percentage of Brooks
if sheerness_brooks < 0:
    sheerness_brooks = 0
if brooks_srathmore > 0:
    brooks_srathmore = 0
if brooks_empress > 0:
    brooks_empress = 0
if brooks_stavely > 0:
    brooks_stavely = 0
if brooks_vauxhall > 0:
    brooks_vauxhall = 0
solar_percentage_brooks = 100*(((brooks_percentage*brookspower) + (sheerness_percentage*sheerness_brooks) + (srathmore_blackie_percentage*(-1*brooks_srathmore)) + (empress_percentage*(-1*brooks_empress)) + (stavely_percentage*(-1*brooks_stavely)) + (vauxhall_percentage*(-1*brooks_vauxhall)))/n.loads.p_set[31])
if solar_percentage_brooks > 100:
    solar_percentage_brooks = 100
sheerness_brooks = n.lines_t.p0.iloc[0,73]
brooks_srathmore = n.lines_t.p0.iloc[0,79]
brooks_empress = n.lines_t.p0.iloc[0,80]
brooks_stavely = n.lines_t.p0.iloc[0,81]
brooks_vauxhall = n.lines_t.p0.iloc[0,82]

#solar percentage of Empress
if hanna_empress < 0:
    hanna_empress = 0
if sheerness_empress < 0:
    sheerness_empress = 0
if brooks_empress < 0:
    brooks_empress = 0
if empress_medicinehat > 0:
    empress_medicinehat = 0
solar_percentage_empress = 100*(((empress_percentage*empresspower) + (hanna_percentage*hanna_empress) + (sheerness_percentage*sheerness_empress) + (brooks_percentage*brooks_empress) + (medicine_hat_percentage*(-1*empress_medicinehat)))/n.loads.p_set[32]) 
if solar_percentage_empress > 100:
    solar_percentage_empress = 100
hanna_empress = n.lines_t.p0.iloc[0,62]
sheerness_empress = n.lines_t.p0.iloc[0,72]
brooks_empress = n.lines_t.p0.iloc[0,80]
empress_medicinehat = n.lines_t.p0.iloc[0,89]

#solar percentage of Stavely
if highriver_stavely < 0:
    highriver_stavely = 0
if stavely_srathmore > 0:
    stavely_srathmore = 0
if brooks_stavely < 0:
    brooks_stavely = 0
if fortmacleod_stavely < 0:
    fortmacleod_stavely = 0
if lethbridge_stavely < 0:
    lethbridge_stavely = 0
if vauxhall_stavely < 0:
    vauxhall_stavely = 0
solar_percentage_stavely = 100*(((stavely_percentage*stavelypower) + (high_river_percentage*highriver_stavely) + (srathmore_blackie_percentage*(-1*stavely_srathmore)) + (brooks_percentage*brooks_stavely) + (fort_macleod_percentage*fortmacleod_stavely) + (lethbridge_percentage*lethbridge_stavely) + (vauxhall_percentage*vauxhall_stavely))/n.loads.p_set[33])
if solar_percentage_stavely > 100:
    solar_percentage_stavely = 100
highriver_stavely = n.lines_t.p0.iloc[0,77]
stavely_srathmore = n.lines_t.p0.iloc[0,78]
brooks_stavely = n.lines_t.p0.iloc[0,81]
fortmacleod_stavely = n.lines_t.p0.iloc[0,83]
lethbridge_stavely = n.lines_t.p0.iloc[0,84]
vauxhall_stavely = n.lines_t.p0.iloc[0,85]

#solar percentage of Vauxhall
if brooks_vauxhall < 0:
    brooks_vauxhall = 0
if vauxhall_stavely > 0:
    vauxhall_stavely = 0
if vauxhall_medicinehat > 0:
    vauxhall_medicinehat = 0
if vauxhall_glenwood > 0:
    vauxhall_glenwood = 0
if vauxhall_lethbridge > 0:
    vauxhall_lethbridge = 0
solar_percentage_vauxhall = 100*(((vauxhall_percentage*vauxhallpower) + (brooks_percentage*brooks_vauxhall) + (stavely_percentage*(-1*vauxhall_stavely)) + (medicine_hat_percentage*(-1*vauxhall_medicinehat)) + (glenwood_percentage*(-1*vauxhall_glenwood)) + (lethbridge_percentage*(-1*vauxhall_lethbridge)))/n.loads.p_set[34])
if solar_percentage_vauxhall > 100:
    solar_percentage_vauxhall = 100
brooks_vauxhall = n.lines_t.p0.iloc[0,82]
vauxhall_stavely = n.lines_t.p0.iloc[0,85]
vauxhall_medicinehat = n.lines_t.p0.iloc[0,86]
vauxhall_glenwood = n.lines_t.p0.iloc[0,87]
vauxhall_lethbridge = n.lines_t.p0.iloc[0,88]

#solar percentage of Fort Macleod
if highriver_fortmacleod < 0:
    highriver_fortmacleod = 0
if fortmacleod_stavely > 0:
    fortmacleod_stavely = 0
if fortmacleod_glenwood > 0:
    fortmacleod_glenwood = 0
if fortmacleod_lethbridge > 0:
    fortmacleod_lethbridge = 0
solar_percentage_fortmacleod = 100*(((fort_macleod_percentage*fortmacleodpower) + (high_river_percentage*highriver_fortmacleod) + (stavely_percentage*(-1*fortmacleod_stavely)) + (glenwood_percentage*(-1*fortmacleod_glenwood)) + (lethbridge_percentage*(-1*fortmacleod_lethbridge)))/n.loads.p_set[35])
if solar_percentage_fortmacleod > 100:
    solar_percentage_fortmacleod = 100
highriver_fortmacleod = n.lines_t.p0.iloc[0,75]
fortmacleod_stavely = n.lines_t.p0.iloc[0,83]
fortmacleod_glenwood = n.lines_t.p0.iloc[0,91]
fortmacleod_lethbridge = n.lines_t.p0.iloc[0,92]

#solar percentage of Lethbridge
if lethbridge_stavely > 0:
    lethbridge_stavely = 0
if vauxhall_lethbridge < 0:
    vauxhall_lethbridge = 0
if fortmacleod_lethbridge < 0:
    fortmacleod_lethbridge = 0
if lethbridge_glenwood > 0:
    lethbridge_glenwood = 0
solar_percentage_lethbridge = 100*(((lethbridge_percentage*lethbridgepower) + (stavely_percentage*(-1*lethbridge_stavely)) + (vauxhall_percentage*vauxhall_lethbridge) + (fort_macleod_percentage*fortmacleod_lethbridge) + (glenwood_percentage*(-1*lethbridge_glenwood)))/n.loads.p_set[36])
if solar_percentage_lethbridge > 100:
    solar_percentage_lethbridge = 100
lethbridge_stavely = n.lines_t.p0.iloc[0,84]
vauxhall_lethbridge = n.lines_t.p0.iloc[0,88]
fortmacleod_lethbridge = n.lines_t.p0.iloc[0,92]
lethbridge_glenwood = n.lines_t.p0.iloc[0,93]

#solar percentage of Glenwood
if vauxhall_glenwood < 0:
    vauxhall_glenwood = 0
if glenwood_medicinehat > 0:
    glenwood_medicinehat = 0
if fortmacleod_glenwood < 0:
    fortmacleod_glenwood = 0
if lethbridge_glenwood < 0:
    lethbridge_glenwood = 0
solar_percentage_glenwood = 100*(((glenwood_percentage*glenwoodpower) + (vauxhall_percentage*vauxhall_glenwood) + (medicine_hat_percentage*(-1*glenwood_medicinehat)) + (fort_macleod_percentage*fortmacleod_glenwood) + (lethbridge_percentage*lethbridge_glenwood))/n.loads.p_set[37])
if solar_percentage_glenwood > 100:
    solar_percentage_glenwood = 100
vauxhall_glenwood = n.lines_t.p0.iloc[0,87]
glenwood_medicinehat = n.lines_t.p0.iloc[0,90]
fortmacleod_glenwood = n.lines_t.p0.iloc[0,91]
lethbridge_glenwood = n.lines_t.p0.iloc[0,93]

#solar percentage of Vegreville
if coldlake_vegreville < 0:
    coldlake_vegreville = 0
if fortsask_vegreville < 0:
    fortsask_vegreville = 0
if vegreville_lloydminster > 0:
    vegreville_lloydminster = 0
if wainwright_vegreville < 0:
    wainwright_vegreville = 0
if wetaskiwin_vegreville < 0:
    wetaskiwin_vegreville = 0
solar_percentage_vegreville = 100*(((vegreville_percentage*vegrevillepower) + (cold_lake_percentage*coldlake_vegreville) + (fort_sask_percentage*fortsask_vegreville) + (lloydminster_percentage*(-1*vegreville_lloydminster)) + (wainwright_percentage*wainwright_vegreville) + (wetaskiwin_percentage*wetaskiwin_vegreville))/n.loads.p_set[38])
if solar_percentage_vegreville > 100:
    solar_percentage_vegreville = 100
coldlake_vegreville = n.lines_t.p0.iloc[0,31]
fortsask_vegreville = n.lines_t.p0.iloc[0,34]
vegreville_lloydminster = n.lines_t.p0.iloc[0,37]
wainwright_vegreville = n.lines_t.p0.iloc[0,39]
wetaskiwin_vegreville = n.lines_t.p0.iloc[0,41]

#solar percentage of Airdrie
if hanna_airdrie < 0:
    hanna_airdrie = 0
if seebe_airdrie < 0:
    seebe_airdrie = 0
if airdrie_didsbury > 0:
    airdrie_didsbury = 0
if airdrie_calgary > 0:
    airdrie_calgary = 0
solar_percentage_airdrie = 100*(((airdrie_percentage*airdriepower) + (hanna_percentage*hanna_airdrie) + (seebe_percentage*seebe_airdrie) + (didsbury_percentage*(-1*airdrie_didsbury)) + (calgary_percentage*(-1*airdrie_calgary)))/n.loads.p_set[39])
if solar_percentage_airdrie > 100:
    solar_percentage_airdrie = 100
hanna_airdrie = n.lines_t.p0.iloc[0,59]
seebe_airdrie = n.lines_t.p0.iloc[0,65]
airdrie_didsbury = n.lines_t.p0.iloc[0,68]
airdrie_calgary = n.lines_t.p0.iloc[0,69]

#solar percentage of Calgary
if seebe_calgary < 0:
    seebe_calgary = 0
if airdrie_calgary < 0:
    airdrie_calgary = 0
if srathmore_calgary < 0:
    srathmore_calgary = 0
if highriver_calgary < 0:
    highriver_calgary = 0
solar_percentage_calgary = 100*(((calgary_percentage*calgarypower) + (seebe_percentage*seebe_calgary) + (airdrie_percentage*airdrie_calgary) + (srathmore_blackie_percentage*srathmore_calgary) + (high_river_percentage*highriver_calgary))/n.loads.p_set[40])
if solar_percentage_calgary > 100:
    solar_percentage_calgary = 100
seebe_calgary =  n.lines_t.p0.iloc[0,66]
airdrie_calgary = n.lines_t.p0.iloc[0,69]
srathmore_calgary = n.lines_t.p0.iloc[0,70]
highriver_calgary = n.lines_t.p0.iloc[0,71]

#solar percentage of Edmonton
if fortsask_edmonton < 0:
    fortsask_edmonton = 0
if wetaskiwin_edmonton < 0:
    wetaskiwin_edmonton = 0
if athabasca_edmonton < 0:
    athabasca_edmonton = 0
if wabamun_edmonton < 0:
    wabamun_edmonton = 0
solar_percentage_edmonton = 100*(((edmonton_percentage*edmontonpower) + (fort_sask_percentage*fortsask_edmonton) + (wetaskiwin_percentage*wetaskiwin_edmonton) + (athabasca_percentage*athabasca_edmonton) + (wabamun_percentage*wabamun_edmonton))/n.loads.p_set[41])
if solar_percentage_edmonton > 100:
    solar_percentage_edmonton = 100
fortsask_edmonton = n.lines_t.p0.iloc[0,35]
wetaskiwin_edmonton = n.lines_t.p0.iloc[0,42]
athabasca_edmonton = n.lines_t.p0.iloc[0,44]
wabamun_edmonton = n.lines_t.p0.iloc[0,45]

n.buses_t.marginal_price.iloc[0,0] = solar_percentage_lloydminster
n.buses_t.marginal_price.iloc[0,1] = solar_percentage_rainbowlake
n.buses_t.marginal_price.iloc[0,2] = solar_percentage_highlevel
n.buses_t.marginal_price.iloc[0,3] = solar_percentage_peaceriver
n.buses_t.marginal_price.iloc[0,4] = solar_percentage_grandeprairie
n.buses_t.marginal_price.iloc[0,5] = solar_percentage_highprairie
n.buses_t.marginal_price.iloc[0,6] = solar_percentage_grandecache
n.buses_t.marginal_price.iloc[0,7] = solar_percentage_valleyview
n.buses_t.marginal_price.iloc[0,8] = solar_percentage_foxcreek
n.buses_t.marginal_price.iloc[0,9] = solar_percentage_fortmac
n.buses_t.marginal_price.iloc[0,10] = solar_percentage_swanhills
n.buses_t.marginal_price.iloc[0,11] = solar_percentage_athabasca
n.buses_t.marginal_price.iloc[0,12] = solar_percentage_coldlake
n.buses_t.marginal_price.iloc[0,13] = solar_percentage_hintonedson
n.buses_t.marginal_price.iloc[0,14] = solar_percentage_draytonvalley
n.buses_t.marginal_price.iloc[0,15] = solar_percentage_wetaskiwin
n.buses_t.marginal_price.iloc[0,16] = solar_percentage_wainwright
n.buses_t.marginal_price.iloc[0,17] = solar_percentage_fortsask
n.buses_t.marginal_price.iloc[0,18] = solar_percentage_abrahamlake
n.buses_t.marginal_price.iloc[0,19] = solar_percentage_reddeer
n.buses_t.marginal_price.iloc[0,20] = solar_percentage_alliance
n.buses_t.marginal_price.iloc[0,21] = solar_percentage_provost
n.buses_t.marginal_price.iloc[0,22] = solar_percentage_caroline
n.buses_t.marginal_price.iloc[0,23] = solar_percentage_didsbury
n.buses_t.marginal_price.iloc[0,24] = solar_percentage_medicinehat
n.buses_t.marginal_price.iloc[0,25] = solar_percentage_wabamun
n.buses_t.marginal_price.iloc[0,26] = solar_percentage_hanna
n.buses_t.marginal_price.iloc[0,27] = solar_percentage_sheerness
n.buses_t.marginal_price.iloc[0,28] = solar_percentage_seebe
n.buses_t.marginal_price.iloc[0,29] = solar_percentage_srathmore
n.buses_t.marginal_price.iloc[0,30] = solar_percentage_highriver
n.buses_t.marginal_price.iloc[0,31] = solar_percentage_brooks
n.buses_t.marginal_price.iloc[0,32] = solar_percentage_empress
n.buses_t.marginal_price.iloc[0,33] = solar_percentage_stavely
n.buses_t.marginal_price.iloc[0,34] = solar_percentage_vauxhall
n.buses_t.marginal_price.iloc[0,35] = solar_percentage_fortmacleod
n.buses_t.marginal_price.iloc[0,36] = solar_percentage_lethbridge
n.buses_t.marginal_price.iloc[0,37] = solar_percentage_glenwood
n.buses_t.marginal_price.iloc[0,38] = solar_percentage_vegreville
n.buses_t.marginal_price.iloc[0,39] = solar_percentage_airdrie
n.buses_t.marginal_price.iloc[0,40] = solar_percentage_calgary
n.buses_t.marginal_price.iloc[0,41] = solar_percentage_edmonton

extent = [-130, -55, 36.5, 75]
central_lon = np.mean(extent[:2])
central_lat = np.mean(extent[2:])

plt.figure(figsize=(12, 8))
norm = plt.Normalize(vmin=0, vmax=100)
ax = plt.axes(projection=ccrs.EqualEarth(central_lon, central_lat))
ax.set_extent(extent)
resol = '50m'

n.plot(
    ax=ax,
    margin = 0.2,
    bus_colors=n.buses_t.marginal_price.mean(),
    bus_cmap="RdYlGn",
    bus_norm=norm,
    bus_sizes=0.1,
    bus_alpha=0.7,
    line_colors = "gainsboro"
)

plt.colorbar(
    plt.cm.ScalarMappable(cmap="RdYlGn", norm=norm),
    ax=ax,
    label="Clean Energy Profile [%]",
    shrink=0.6,
)

country_bodr = cartopy.feature.NaturalEarthFeature(category='cultural', 
    name='admin_0_boundary_lines_land', scale=resol, facecolor='none', edgecolor='k')

provinc_bodr = cartopy.feature.NaturalEarthFeature(category='cultural', 
    name='admin_1_states_provinces_lines', scale=resol, facecolor='none', edgecolor='k')

ax.add_feature(country_bodr, linestyle='--', linewidth=0.8, edgecolor="k", zorder=10)  
ax.add_feature(provinc_bodr, linestyle='--', linewidth=0.6, edgecolor="k", zorder=10)

plt.show()

genprofile = {"Clean Energy Profile for Lloydminster: %0.2f" % solar_percentage_lloydminster + "%",
              "Clean Energy Profile for Rainbow Lake: %0.2f" % solar_percentage_rainbowlake + "%",
              "Clean Energy Profile for High Level: %0.2f" % solar_percentage_highlevel + "%",
              "Clean Energy Profile for Peace River: %0.2f" % solar_percentage_peaceriver + "%",
              "Clean Energy Profile for Grande Prairie: %0.2f" % solar_percentage_grandeprairie + "%",
              "Clean Energy Profile for High Prairie: %0.2f" % solar_percentage_highprairie + "%", 
              "Clean Energy Profile for Grande Cache: %0.2f" % solar_percentage_grandecache + "%",
              "Clean Energy Profile for Valleyview: %0.2f" % solar_percentage_valleyview + "%",
              "Clean Energy Profile for Fox Creek: %0.2f" % solar_percentage_foxcreek + "%",
              "Clean Energy Profile for Fort Mac: %0.2f" % solar_percentage_fortmac + "%",
              "Clean Energy Profile for Swan Hills Lake: %0.2f" % solar_percentage_swanhills + "%",
              "Clean Energy Profile for Athabasca: %0.2f" % solar_percentage_athabasca + "%",
              "Clean Energy Profile for Cold Lake: %0.2f" % solar_percentage_coldlake + "%", 
              "Clean Energy Profile for Hinton/Edson: %0.2f" % solar_percentage_hintonedson + "%",
              "Clean Energy Profile for Drayton Valley: %0.2f" % solar_percentage_draytonvalley + "%",
              "Clean Energy Profile for Wetaskiwin: %0.2f" % solar_percentage_wetaskiwin + "%",
              "Clean Energy Profile for Wainwright: %0.2f" % solar_percentage_wainwright + "%",
              "Clean Energy Profile for Fort Sask: %0.2f" % solar_percentage_fortsask + "%",
              "Clean Energy Profile for Abraham Lake: %0.2f" % solar_percentage_abrahamlake + "%", 
              "Clean Energy Profile for Red Deer: %0.2f" % solar_percentage_reddeer + "%",
              "Clean Energy Profile for Alliance/Battle River: %0.2f" % solar_percentage_alliance + "%",
              "Clean Energy Profile for Provost: %0.2f" % solar_percentage_provost + "%",
              "Clean Energy Profile for Caroline: %0.2f" % solar_percentage_caroline + "%",
              "Clean Energy Profile for Didsbury: %0.2f" % solar_percentage_didsbury + "%",
              "Clean Energy Profile for Medicine Hat: %0.2f" % solar_percentage_medicinehat + "%",
              "Clean Energy Profile for Wabamun: %0.2f" % solar_percentage_wabamun + "%",
              "Clean Energy Profile for Hanna: %0.2f" % solar_percentage_hanna + "%",
              "Clean Energy Profile for Sheerness: %0.2f" % solar_percentage_sheerness + "%",
              "Clean Energy Profile for Seebe: %0.2f" % solar_percentage_seebe + "%",
              "Clean Energy Profile for Srathmore/Blackie: %0.2f" % solar_percentage_srathmore + "%",
              "Clean Energy Profile for High River: %0.2f" % solar_percentage_highriver + "%",
              "Clean Energy Profile for Brooks: %0.2f" % solar_percentage_brooks + "%",
              "Clean Energy Profile for Empress: %0.2f" % solar_percentage_empress + "%",
              "Clean Energy Profile for Stavely: %0.2f" % solar_percentage_stavely + "%", 
              "Clean Energy Profile for Vauxhall: %0.2f" % solar_percentage_vauxhall + "%",
              "Clean Energy Profile for Fort Macleod: %0.2f" % solar_percentage_fortmacleod + "%",
              "Clean Energy Profile for Lethbridge: %0.2f" % solar_percentage_lethbridge + "%",
              "Clean Energy Profile for Glenwood Lake: %0.2f" % solar_percentage_glenwood + "%",
              "Clean Energy Profile for Vegreville: %0.2f" % solar_percentage_vegreville + "%",
              "Clean Energy Profile for Airdrie: %0.2f" % solar_percentage_airdrie + "%",
              "Clean Energy Profile for Calgary: %0.2f" % solar_percentage_calgary + "%",
              "Clean Energy Profile for Edmonton: %0.2f" % solar_percentage_edmonton + "%"}

n.buses_t.marginal_price.iloc[0,0] = dl.Income[0]/(solar_percentage_lloydminster*n.loads.p_set[0]*0.01)
n.buses_t.marginal_price.iloc[0,1] = dl.Income[1]/(solar_percentage_rainbowlake*n.loads.p_set[1]*0.01)
n.buses_t.marginal_price.iloc[0,2] = dl.Income[2]/(solar_percentage_highlevel*n.loads.p_set[2]*0.01)
n.buses_t.marginal_price.iloc[0,3] = dl.Income[3]/(solar_percentage_peaceriver*n.loads.p_set[3]*0.01)
n.buses_t.marginal_price.iloc[0,4] = dl.Income[4]/(solar_percentage_grandeprairie*n.loads.p_set[4]*0.01)
n.buses_t.marginal_price.iloc[0,5] = dl.Income[5]/(solar_percentage_highprairie*n.loads.p_set[5]*0.01)
n.buses_t.marginal_price.iloc[0,6] = dl.Income[6]/(solar_percentage_grandecache*n.loads.p_set[6]*0.01)
n.buses_t.marginal_price.iloc[0,7] = dl.Income[7]/(solar_percentage_valleyview*n.loads.p_set[7]*0.01)
n.buses_t.marginal_price.iloc[0,8] = dl.Income[8]/(solar_percentage_foxcreek*n.loads.p_set[8]*0.01)
n.buses_t.marginal_price.iloc[0,9] = dl.Income[9]/(solar_percentage_fortmac*n.loads.p_set[9]*0.01)
n.buses_t.marginal_price.iloc[0,10] = dl.Income[10]/(solar_percentage_swanhills*n.loads.p_set[10]*0.01)
n.buses_t.marginal_price.iloc[0,11] = dl.Income[11]/(solar_percentage_athabasca*n.loads.p_set[11]*0.01)
n.buses_t.marginal_price.iloc[0,12] = dl.Income[12]/(solar_percentage_coldlake*n.loads.p_set[12]*0.01)
n.buses_t.marginal_price.iloc[0,13] = dl.Income[13]/(solar_percentage_hintonedson*n.loads.p_set[13]*0.01)
n.buses_t.marginal_price.iloc[0,14] = dl.Income[14]/(solar_percentage_draytonvalley*n.loads.p_set[14]*0.01)
n.buses_t.marginal_price.iloc[0,15] = dl.Income[15]/(solar_percentage_wetaskiwin*n.loads.p_set[15]*0.01)
n.buses_t.marginal_price.iloc[0,16] = dl.Income[16]/(solar_percentage_wainwright*n.loads.p_set[16]*0.01)
n.buses_t.marginal_price.iloc[0,17] = dl.Income[17]/(solar_percentage_fortsask*n.loads.p_set[17]*0.01)
n.buses_t.marginal_price.iloc[0,18] = dl.Income[18]/(solar_percentage_abrahamlake*n.loads.p_set[18]*0.01)
n.buses_t.marginal_price.iloc[0,19] = dl.Income[19]/(solar_percentage_reddeer*n.loads.p_set[19]*0.01)
n.buses_t.marginal_price.iloc[0,20] = dl.Income[20]/(solar_percentage_alliance*n.loads.p_set[20]*0.01)
n.buses_t.marginal_price.iloc[0,21] = dl.Income[21]/(solar_percentage_provost*n.loads.p_set[21]*0.01)
n.buses_t.marginal_price.iloc[0,22] = dl.Income[22]/(solar_percentage_caroline*n.loads.p_set[22]*0.01)
n.buses_t.marginal_price.iloc[0,23] = dl.Income[23]/(solar_percentage_didsbury*n.loads.p_set[23]*0.01)
n.buses_t.marginal_price.iloc[0,24] = dl.Income[24]/(solar_percentage_medicinehat*n.loads.p_set[24]*0.01)
n.buses_t.marginal_price.iloc[0,25] = dl.Income[25]/(solar_percentage_wabamun*n.loads.p_set[25]*0.01)
n.buses_t.marginal_price.iloc[0,26] = dl.Income[26]/(solar_percentage_hanna*n.loads.p_set[26]*0.01)
n.buses_t.marginal_price.iloc[0,27] = dl.Income[27]/(solar_percentage_sheerness*n.loads.p_set[27]*0.01)
n.buses_t.marginal_price.iloc[0,28] = dl.Income[28]/(solar_percentage_seebe*n.loads.p_set[28]*0.01)
n.buses_t.marginal_price.iloc[0,29] = dl.Income[29]/(solar_percentage_srathmore*n.loads.p_set[29]*0.01)
n.buses_t.marginal_price.iloc[0,30] = dl.Income[30]/(solar_percentage_highriver*n.loads.p_set[30]*0.01)
n.buses_t.marginal_price.iloc[0,31] = dl.Income[31]/(solar_percentage_brooks*n.loads.p_set[31]*0.01)
n.buses_t.marginal_price.iloc[0,32] = dl.Income[32]/(solar_percentage_empress*n.loads.p_set[32]*0.01)
n.buses_t.marginal_price.iloc[0,33] = dl.Income[33]/(solar_percentage_stavely*n.loads.p_set[33]*0.01)
n.buses_t.marginal_price.iloc[0,34] = dl.Income[34]/(solar_percentage_vauxhall*n.loads.p_set[34]*0.01)
n.buses_t.marginal_price.iloc[0,35] = dl.Income[35]/(solar_percentage_fortmacleod*n.loads.p_set[35]*0.01)
n.buses_t.marginal_price.iloc[0,36] = dl.Income[36]/(solar_percentage_lethbridge*n.loads.p_set[36]*0.01)
n.buses_t.marginal_price.iloc[0,37] = dl.Income[37]/(solar_percentage_glenwood*n.loads.p_set[37]*0.01)
n.buses_t.marginal_price.iloc[0,38] = dl.Income[38]/(solar_percentage_vegreville*n.loads.p_set[38]*0.01)
n.buses_t.marginal_price.iloc[0,39] = dl.Income[39]/(solar_percentage_airdrie*n.loads.p_set[39]*0.01)
n.buses_t.marginal_price.iloc[0,40] = dl.Income[40]/(solar_percentage_calgary*n.loads.p_set[40]*0.01)
n.buses_t.marginal_price.iloc[0,41] = dl.Income[41]/(solar_percentage_edmonton*n.loads.p_set[41]*0.01)

#January
if '2024-01' in date:
    df_filtered_solar = df.iloc[0:743]
    plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
    plt.xlabel('DT_MST (Time)')
    plt.ylabel('Solar Generation (MW)')
    plt.title('Solar Generation for January')
    plt.xticks(rotation=30)
    plt.show()

    df_filtered_wind = df.iloc[0:743]
    plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
    plt.xlabel('DT_MST (Time)')
    plt.ylabel('Wind Generation (MW)')
    plt.title('Wind Generation for January')
    plt.xticks(rotation=30)
    plt.show()  
else:
    if '2024-02' in date:
        df_filtered_solar = df.iloc[744:1439]
        plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
        plt.xlabel('DT_MST (Time)')
        plt.ylabel('Solar Generation (MW)')
        plt.title('Solar Generation for February')
        plt.xticks(rotation=30)
        plt.show()  

        df_filtered_wind = df.iloc[744:1439]
        plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
        plt.xlabel('DT_MST (Time)')
        plt.ylabel('Wind Generation (MW)')
        plt.title('Wind Generation for February')
        plt.xticks(rotation=30)
        plt.show()  
    else:
        if '2024-03' in date:
            df_filtered_solar = df.iloc[1440:2183]
            plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
            plt.xlabel('DT_MST (Time)')
            plt.ylabel('Solar Generation (MW)')
            plt.title('Solar Generation for March')
            plt.xticks(rotation=30)
            plt.show()  

            df_filtered_wind = df.iloc[1440:2183]
            plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
            plt.xlabel('DT_MST (Time)')
            plt.ylabel('Wind Generation (MW)')
            plt.title('Wind Generation for March')
            plt.xticks(rotation=30)
            plt.show()  
        else:
            if '2024-04' in date:
                df_filtered_solar = df.iloc[2184:2903]
                plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                plt.xlabel('DT_MST (Time)')
                plt.ylabel('Solar Generation (MW)')
                plt.title('Solar Generation for April')
                plt.xticks(rotation=30)
                plt.show()  

                df_filtered_wind = df.iloc[2184:2903]
                plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                plt.xlabel('DT_MST (Time)')
                plt.ylabel('Wind Generation (MW)')
                plt.title('Wind Generation for April')
                plt.xticks(rotation=30)
                plt.show()  
            else:
                if '2024-05' in date:
                    df_filtered_solar = df.iloc[2904:3647]
                    plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                    plt.xlabel('DT_MST (Time)')
                    plt.ylabel('Solar Generation (MW)')
                    plt.title('Solar Generation for May')
                    plt.xticks(rotation=30)
                    plt.show()  

                    df_filtered_wind = df.iloc[2904:3647]
                    plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                    plt.xlabel('DT_MST (Time)')
                    plt.ylabel('Wind Generation (MW)')
                    plt.title('Wind Generation for May')
                    plt.xticks(rotation=30)
                    plt.show()    
                else: 
                    if '2024-06' in date:
                        df_filtered_solar = df.iloc[3648:4367]
                        plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                        plt.xlabel('DT_MST (Time)')
                        plt.ylabel('Solar Generation (MW)')
                        plt.title('Solar Generation for June')
                        plt.xticks(rotation=30)
                        plt.show()  

                        df_filtered_wind = df.iloc[3648:4367]
                        plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                        plt.xlabel('DT_MST (Time)')
                        plt.ylabel('Wind Generation (MW)')
                        plt.title('Wind Generation for June')
                        plt.xticks(rotation=30)
                        plt.show()   
                    else:
                        if '2024-07' in date:
                            df_filtered_solar = df.iloc[3648:5111]
                            plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                            plt.xlabel('DT_MST (Time)')
                            plt.ylabel('Solar Generation (MW)')
                            plt.title('Solar Generation for July')
                            plt.xticks(rotation=30)
                            plt.show()  

                            df_filtered_wind = df.iloc[3648:5111]
                            plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                            plt.xlabel('DT_MST (Time)')
                            plt.ylabel('Wind Generation (MW)')
                            plt.title('Wind Generation for July')
                            plt.xticks(rotation=30)
                            plt.show()   
                        else:
                            if '2024-08' in date:
                                df_filtered_solar = df.iloc[5112:5855]
                                plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                                plt.xlabel('DT_MST (Time)')
                                plt.ylabel('Solar Generation (MW)')
                                plt.title('Solar Generation for August')
                                plt.xticks(rotation=30)
                                plt.show()  

                                df_filtered_wind = df.iloc[5112:5855]
                                plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                                plt.xlabel('DT_MST (Time)')
                                plt.ylabel('Wind Generation (MW)')
                                plt.title('Wind Generation for August')
                                plt.xticks(rotation=30)
                                plt.show()   
                            else:
                                if '2024-09' in date:
                                    df_filtered_solar = df.iloc[5856:6575]
                                    plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                                    plt.xlabel('DT_MST (Time)')
                                    plt.ylabel('Solar Generation (MW)')
                                    plt.title('Solar Generation for September')
                                    plt.xticks(rotation=30)
                                    plt.show()  

                                    df_filtered_wind = df.iloc[5856:6575]
                                    plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                                    plt.xlabel('DT_MST (Time)')
                                    plt.ylabel('Wind Generation (MW)')
                                    plt.title('Wind Generation for September')
                                    plt.xticks(rotation=30)
                                    plt.show()  
                                else:
                                    if '2024-10' in date: 
                                        df_filtered_solar = df.iloc[6576:7319]
                                        plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                                        plt.xlabel('DT_MST (Time)')
                                        plt.ylabel('Solar Generation (MW)')
                                        plt.title('Solar Generation for October')
                                        plt.xticks(rotation=30)
                                        plt.show()  

                                        df_filtered_wind = df.iloc[6576:7319]
                                        plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                                        plt.xlabel('DT_MST (Time)')
                                        plt.ylabel('Wind Generation (MW)')
                                        plt.title('Wind Generation for October')
                                        plt.xticks(rotation=30)
                                        plt.show()  
                                    else:
                                        if '2024-11' in date:
                                            df_filtered_solar = df.iloc[7320:8039]
                                            plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                                            plt.xlabel('DT_MST (Time)')
                                            plt.ylabel('Solar Generation (MW)')
                                            plt.title('Solar Generation for November')
                                            plt.xticks(rotation=30)
                                            plt.show()  

                                            df_filtered_wind = df.iloc[7320:8039]
                                            plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                                            plt.xlabel('DT_MST (Time)')
                                            plt.ylabel('Wind Generation (MW)')
                                            plt.title('Wind Generation November')
                                            plt.xticks(rotation=30)
                                            plt.show()
                                        else:   
                                            df_filtered_solar = df.iloc[8040:8783]
                                            plt.plot(df_filtered_solar['DT_MST'], (df_filtered_solar['solar_percentage']*1105), color = 'green')
                                            plt.xlabel('DT_MST (Time)')
                                            plt.ylabel('Solar Generation (MW)')
                                            plt.title('Solar Generation for December')
                                            plt.xticks(rotation=30)
                                            plt.show()  

                                            df_filtered_wind = df.iloc[8040:8783]
                                            plt.plot(df_filtered_wind['DT_MST'], (df_filtered_wind['wind_percentage']*1443), color = 'orange')
                                            plt.xlabel('DT_MST (Time)')
                                            plt.ylabel('Wind Generation (MW)')
                                            plt.title('Wind Generation for December')
                                            plt.xticks(rotation=30)
                                            plt.show()   

