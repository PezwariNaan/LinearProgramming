#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
from os import getenv
from collections import Counter

class Vehicle:
    def __init__(self, ID:str, fuel_type:str):
        self.fuel_type = fuel_type
        self.ID = ID
        return 

    def __hash__(self):
        return hash((self.ID, self.fuel_type))
    
    def __eq__(self, other):
        return (self.ID, self.fuel_type == other.ID, other.fuel_type)

class Model:
    def __init__(self):
        # Load dataframes on initialisation
        self.load_dataframes()

        # Set inital conditions
        self.fleet = Counter({}) # Dictionary of Vehicles & Number Owned
        self.spent = 0

        return

    def purchase_vehicle(self, vehicle_ID:str, fuel_type:str):
        df_vehicles = self.df['vehicles']
        vehicle = Vehicle(vehicle_ID, fuel_type)
        vehicle_details = df_vehicles[df_vehicles['ID'] == vehicle_ID]
        self.spent += vehicle_details['Cost ($)'].values[0]
        self.fleet.update({vehicle : 1})
        return 
         
    def list_fleet(self):
        print("Vehicles Currently in Fleet:")
        for vehicle in self.fleet.items():
            print(f"{vehicle[0].ID}: {vehicle[1]} ({vehicle[0].fuel_type})")
        return

    def list_df_keys(self):
        for key in self.df.keys():
            print(key)
        return

    def get_df(self, df_key):
        return self.df[df_key]

    def load_dataframes(self):
        self.user = getenv('USER')
        self.dir = Path(f"/home/{self.user}/Documents/Competitions/Shell/dataset/CSV_Files/")
        self.file_list = [file for file in self.dir.iterdir()]
        self.file_list.remove(self.file_list[0])
        self.df = {}
        for file in self.file_list:
            # Set the filename as the key, and the dataframe as the value
            self.df[str(file.name).replace('.csv' , '')] = pd.read_csv(file)
            self.df[str(file.name).replace('.csv' , '')].reset_index(
                                                           inplace = True,
                                                           drop = True)
        return 

def main():
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.max_rows', 200)

    model = Model()
    vehicle = model.purchase_vehicle('BEV_S3_2023', 'Electricity') 
    vehicle = model.purchase_vehicle('BEV_S3_2023', 'Electricity') 
    vehicle = model.purchase_vehicle('BEV_S3_2023', 'Banana') 
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

