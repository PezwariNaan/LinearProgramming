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

###################################################################
class Model:
    class YearlyRequirements:
        def __init__(self, demand_df, carbon_emissions_df, current_year):
            ######## Distance Demands #########
            self.demand = demand_df[demand_df['Year'] == current_year]
            self.demand_km = self.demand['Demand (km)'].values
            # Pivot Table to create demand_matrix
            self.demand_matrix = self.demand.pivot(index='Size', columns='Distance', values='Demand (km)')
            self.demand_left = 0

            ######## Carbon Emission Limits ########
            self.emission_limit = carbon_emissions_df[
                    carbon_emissions_df['Year']== 2023]['Carbon emission CO2/kg'
                                                        ].item()
            self.get_demand()
            return

        def get_demand(self):
            """
                The assumption is that for every Dx < vehicle Dx
                The corresponding vehicle Sx will decrement

                E.g If a vehicle D4 S1 travels one mile, 
                D1, D2, D3, D4 will decrement.
            """
            total = 0
            for demand in self.demand_matrix:
                total  += sum(self.demand_matrix[demand].values)
            self.demand_left = total

    class Vehicle:
        def __init__(self, ID: str, fuel_type: str, vehicles_df):
            self.ID = ID
            self.fuel_type = fuel_type
            self.details = vehicles_df[vehicles_df['ID'] == ID]

            self.purchase_year = self.details['Year'].item() \
                    if not self.details.empty else None

            self.purchase_price = self.details['Cost ($)'].item() \
                    if not self.details.empty else None

            self.yearly_range = self.details['Yearly range (km)'].item() \
                    if not self.details.empty else None

            self.size_bucket = self.details['Size'].item() \
                    if not self.details.empty else None

            self.distance_bucket = self.details['Distance'].item() \
                    if not self.details.empty else None

        def __hash__(self):
            return hash((self.ID, self.fuel_type))
        
        def __eq__(self, other):
            return (self.ID, self.fuel_type == other.ID, other.fuel_type)

    def __init__(self, dataframes: DF):
        # Easy Access to dataframes
        self.vehicles_df = dataframes.vehicles
        self.vehicle_fuels_df = dataframes.vehicle_fuels
        self.fuels_df = dataframes.fuels
        self.demand_df = dataframes.demand
        self.cost_profiles_df = dataframes.cost_profiles
        self.carbon_emissions_df = dataframes.carbon_emissions

        # Set initial conditions
        self.current_year = 2023
        self.fleet = Counter({})
        self.yearly_requirements = self.YearlyRequirements(
                                   self.demand_df, 
                                   self.carbon_emissions_df, 
                                   self.current_year)
        self.total_costs = 0
        self.total_emissions = 0
        return

    def purchase_vehicle(self, vehicle_ID: str, fuel_type: str):
        try:
            vehicle_details = self.vehicles_df[self.vehicles_df['ID'] == vehicle_ID]

            if vehicle_details.empty:
                print(f"Vehicle {vehicle_ID} not found.")
                return 

            vehicle = self.Vehicle(vehicle_ID, fuel_type, self.vehicles_df)
            self.total_costs += vehicle.purchase_price
            self.fleet.update({vehicle: 1})
            #print(f"Purchased: {vehicle.ID}: {vehicle.fuel_type}")
            return 

        except Exception as e:
            print(f"Error: {e}")
            return 

    def sell_vehicle(self, vehicle_ID: str, fuel_type: str):
        try:
            vehicle = self.Vehicle(vehicle_ID, fuel_type, self.vehicles_df)
            if vehicle in self.fleet:
                resale_value = self.calculate_resale_value(vehicle)
                self.total_costs -= resale_value
                self.fleet.subtract({vehicle: 1})
                if self.fleet[vehicle] == 0:
                    del self.fleet[vehicle]
                #print(f"Sold: {vehicle.ID}: {vehicle.fuel_type}")
            else:
                print(f"Cannot Sell {vehicle.ID}: is not in Fleet")
                return 

        except Exception as e:
            print(f"Error: {e}")
            return 

    def use_vehicle(self, vehicle_ID: str, fuel_type: str, distance: int):
        try:
            vehicle = self.Vehicle(vehicle_ID, fuel_type, self.vehicles_df)
            if vehicle not in self.fleet:
                print(f"Connot Use {vehicle_ID}: not in fleet.")
                return 

            vehicle_fuel_details = self.vehicle_fuels_df[
                (self.vehicle_fuels_df['ID'] == vehicle_ID) & 
                (self.vehicle_fuels_df['Fuel'] == fuel_type)
            ]

            if vehicle_fuel_details.empty:
                print(f"No fuel details found for {vehicle_ID} with {fuel_type}.")
                return 

            # Subtract distance traveled from yearly demand
            # Based on size and distance buckets

            # Size must == to
            # Distace must >= than
            
            matrix = self.yearly_requirements.demand_matrix

            for distance_bucket in matrix:
                if distance_bucket <= vehicle.distance_bucket:
                    matrix.loc[vehicle.size_bucket,
                                     distance_bucket] -= distance
            self.yearly_requirements.get_demand()

            consumption_rate = vehicle_fuel_details['Consumption (unit_fuel/km)'].item()
            fuel_price = self.fuels_df[(self.fuels_df['Fuel'] == fuel_type) & \
                    (self.fuels_df['Year'] == self.current_year)].values[0][3]
            emission_rate = self.fuels_df[(self.fuels_df['Fuel'] == fuel_type) & \
                    (self.fuels_df['Year'] == self.current_year)].values[0][2]

            fuel_used = consumption_rate * distance
            fuel_cost = fuel_used * fuel_price
            emissions = emission_rate * distance

            self.total_costs += fuel_cost
            self.total_emissions += emissions
            #print("Used: {vehicle.ID}: {vehicle.fuel_type}")
            return

        except Exception as e:
            print(f"Error: {e}")
            return 

    def insure(self, vehicle_ID: str):
        self.add_cost(vehicle_ID, 'Insurance Cost %')
        return
        
    def maintain(self, vehicle_ID: str):
        self.add_cost(vehicle_ID, 'Maintenance Cost %')
        return

    ##################### CLASS HELPER FUNCTIONS #######################
    def list_fleet(self):
        print("Vehicles Currently in Fleet:")
        for vehicle, count in self.fleet.items():
            print(f"{vehicle.ID}: {count} ({vehicle.fuel_type})")
        return

    def add_cost(self, vehicle_ID: str, cost_type: str):
        vehicle_details = self.vehicles_df[self.vehicles_df['ID'] == vehicle_ID]
        vehicle_purchase_year = vehicle_details['Year'].values[0]
        vehicle_age = self.current_year - vehicle_purchase_year
        vehicle_purchase_price = vehicle_details['Cost ($)'].values[0]
        rate = self.cost_profiles_df[self.cost_profiles_df['End of Year'] == vehicle_age + 1][cost_type].item()
        cost = (rate / 100) * vehicle_purchase_price
        self.total_costs += cost

    def calculate_resale_value(self, vehicle):
        vehicle_age = self.current_year - vehicle.purchase_year
        resale_rate = self.cost_profiles_df[self.cost_profiles_df['End of Year'] == vehicle_age + 1]['Resale Value %'].item()
        resale_value = (resale_rate / 100) * vehicle.purchase_price
        return resale_value


####################################################################
def main():
    """
    dataframes = DF()
    model = Model(dataframes)

    print("Episode Done")
    print(f"Demand Left: {model.yearly_requirements.demand_left}")
    print(f"Carbon Emissions: {model.total_emissions}")

    for i in range(0, 3):
        model.purchase_vehicle('LNG_S2_2023', 'LNG')
    model.list_fleet()
    model.use_vehicle('LNG_S2_2023', 'LNG', 106000)
    print(f"Demand Left: {model.yearly_requirements.demand_left}")
    print(f"Carbon Emissions: {model.total_emissions}")
    """
if __name__ == '__main__':
    main()

