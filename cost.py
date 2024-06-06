#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
from os import getenv
from collections import Counter

###################################################################
class DF:
    def __init__(self):
        self.create_df()
        pd.set_option('display.max_columns', 10)
        pd.set_option('display.max_rows', 200)
        return 

    def create_df(self):
        user = getenv('USER')
        dir = Path(f"/home/{user}/Documents/Competitions/Shell/dataset/CSV_Files/")
        file_list = [file for file in dir.iterdir()]
        file_list.remove(file_list[0])
        for file in file_list:
            df_name = str(file.stem) # Filename no extension
            df = pd.read_csv(file)
            df.reset_index(inplace = True, drop = True)
            setattr(self, df_name, df)
        return 

    def list_df_keys(self):
        attributes = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        for attr in attributes:
            print(attr)
        return

###################################################################
class Vehicle:
    def __init__(self, ID:str, fuel_type:str):
        self.fuel_type = fuel_type
        self.ID = ID
        return 

    def __hash__(self):
        return hash((self.ID, self.fuel_type))
    
    def __eq__(self, other):
        return (self.ID, self.fuel_type == other.ID, other.fuel_type)

###################################################################
class Model:
    def __init__(self, dataframes: DF):
        # Set inital conditions
        self.fleet = Counter({}) # Dictionary of Vehicles & Number Owned
        self.purchase_costs = 0
        self.dataframes = dataframes
        return

    def purchase_vehicle(self, vehicle_ID:str, fuel_type:str):
        df_vehicles = self.dataframes.vehicles
        vehicle = Vehicle(vehicle_ID, fuel_type)
        vehicle_details = df_vehicles[df_vehicles['ID'] == vehicle_ID]
        self.purchase_costs += vehicle_details['Cost ($)'].values[0]
        self.fleet.update({vehicle : 1})
        return 
         
    def list_fleet(self):
        print("Vehicles Currently in Fleet:")
        for vehicle in self.fleet.items():
            print(f"{vehicle[0].ID}: {vehicle[1]} ({vehicle[0].fuel_type})")
        return

####################################################################
def main():

    dataframes = DF()
    model = Model(dataframes)
    model.purchase_vehicle('BEV_S2_2023', 'Electrical')
    model.purchase_vehicle('BEV_S2_2023', 'Electrical')
    model.purchase_vehicle('BEV_S4_2023', 'Electrical')
    model.purchase_vehicle('BEV_S4_2023', 'Banana')
    model.list_fleet()

    """
    Variables to Consider / Implement:
        start_year = 2023
        current_year = year
        end_year = 2038

        cost_of_purchasing_vehicles = vehicle_price * number_of_vehicles
        cost of insurace = age * insurance(age)
    """

if __name__ == '__main__':
    main()

