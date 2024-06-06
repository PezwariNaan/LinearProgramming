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
    class YearlyRequirements:
        def __init__(self, demand_df, carbon_emissions_df, current_year):
            self.distance_km = demand_df[demand_df['Year'] == \
                    current_year]['Demand (km)'].values

            self.distance = demand_df[demand_df['Year'] == \
                    current_year]['Distance'].values

            self.size = demand_df[demand_df['Year'] == \
                    current_year]['Size'].values

            self.emission_limit = carbon_emissions_df[
                    carbon_emissions_df['Year'] == current_year]\
            .values[0][1]
            return

    def __init__(self, dataframes: DF):
        # Easy Access to dataframes
        self.vehicles_df = dataframes.vehicles
        self.vehicle_fuels_df = dataframes.vehicle_fuels
        self.fuels_df = dataframes.fuels
        self.demand_df = dataframes.demand
        self.cost_profiles_df = dataframes.cost_profiles
        self.carbon_emissions_df = dataframes.carbon_emissions

        # Set inital conditions
        self.current_year = 2023
        self.fleet = Counter({}) # Dictionary of Vehicles & Number Owned
        self.yearly_requirements = self.YearlyRequirements(
                                                self.demand_df,
                                                self.carbon_emissions_df,
                                                self.current_year
                                                )
        self.total_costs = 0
        self.total_emissions = 0
        return

    def purchase_vehicle(self, vehicle_ID: str, fuel_type: str):
        try:
            vehicle_details = self.vehicles_df[self.vehicles_df['ID'] == vehicle_ID]

            if vehicle_details.empty:
                print(f"Vehicle {vehicle_ID} not found.")
                return 

            vehicle = Vehicle(vehicle_ID, fuel_type)
            self.total_costs += vehicle_details['Cost ($)'].values[0]
            self.fleet.update({vehicle : 1})
            return 

        except Exception as e:
            print(f"Error: {e}")
            return 

    def sell_vehicle(self, vehicle_ID: str, fuel_type: str):
        try:
            vehicle = Vehicle(vehicle_ID, fuel_type)
            if vehicle in self.fleet:
                vehicle_details = self.vehicles_df[self.vehicles_df['ID'] == vehicle_ID]

                vehicle_purchase_year = vehicle_details['Year'].values[0]

                vehicle_age = self.current_year - vehicle_purchase_year

                vehicle_purchase_price = vehicle_details['Cost ($)'].values[0]

                # Retrieve the devalue rate from the cost_profiles dataframe
                # Based on the age of the vehicle. 
                resale_rate = self.cost_profiles_df[self.cost_profiles_df\
                        ['End of Year'] == vehicle_age + 1]\
                        ['Resale Value %'].item()

                resale_value = (resale_rate / 100) * vehicle_purchase_price
                self.total_costs -= resale_value
            else:
                print("Vehicle is not in Fleet")
                return 

        except Exception as e:
            print(f"Error: {e}")
            return 

    def use_vehicle(self, vehicle_ID: str, fuel_type: str, distance: int):
        try:
            # Check vehicle is valid
            vehicle = Vehicle(vehicle_ID, fuel_type)
            if vehicle not in self.fleet:
                print(f"Vehicle {vehicle_ID} not in fleet.")
                return 

            vehicle_fuel_details = self.vehicle_fuels_df[
                (self.vehicle_fuels_df['ID'] == vehicle_ID) &
                (self.vehicle_fuels_df['Fuel'] == fuel_type)
            ]

            if vehicle_fuel_details.empty:
                print(f"No fuel details found for{vehicle_ID} with {fuel_type}.")
                return 

            # Units and variabels
            consumption_rate = \
                    vehicle_fuel_details['Consumption (unit_fuel/km)'].item()

            # Fuel Price = filter(current year + fuel)
            fuel_price = self.fuels_df[
                    (self.fuels_df['Fuel'] == fuel_type) &
                    (self.fuels_df['Year'] == self.current_year)
            ].values[0][3] # Index the returned matrix

            # Emission Rate = (current year + fuel)
            emission_rate = self.fuels_df[
                    (self.fuels_df['Fuel'] == fuel_type) &
                    (self.fuels_df['Year'] == self.current_year)
            ].values[0][2] # Index the returned matrix

            fuel_used = consumption_rate * distance

            fuel_cost = fuel_used * fuel_price

            emissions = emission_rate * distance

            # Add to totals
            self.total_costs += fuel_cost
            self.total_emissions += emissions
            return

        except Exception as e:
            print(f"Error: {e}")
            return 
        
    def insure(self, vehicle_ID: str):
        vehicle_details = self.vehicles_df[self.vehicles_df['ID'] == vehicle_ID]

        vehicle_purchase_year = vehicle_details['Year'].values[0]

        vehicle_age = self.current_year - vehicle_purchase_year

        vehicle_purchase_price = vehicle_details['Cost ($)'].values[0]

        # Retrieve the insurance rate from the cost_profiles dataframe
        # Based on the age of the vehicle. 
        insurance_rate = self.cost_profiles_df[self.cost_profiles_df\
                ['End of Year'] == vehicle_age + 1]\
                ['Insurance Cost %'].item()

        insurance_cost = (insurance_rate / 100) * vehicle_purchase_price
        self.total_costs += insurance_cost
        return
        
    def maintain(self, vehicle_ID: str):
        vehicle_details = self.vehicles_df[self.vehicles_df['ID'] == vehicle_ID]

        vehicle_purchase_year = vehicle_details['Year'].values[0]

        vehicle_age = self.current_year - vehicle_purchase_year

        vehicle_purchase_price = vehicle_details['Cost ($)'].values[0]

        # Retrieve the maintenance rate from the cost_profiles dataframe
        # Based on the age of the vehicle. 
        maintenance_rate = self.cost_profiles_df[self.cost_profiles_df\
                ['End of Year'] == vehicle_age + 1]\
                ['Maintenance Cost %'].item()

        maintenance_cost = (maintenance_rate / 100) * vehicle_purchase_price
        self.total_costs += maintenance_cost 
        return

##################### CLASS HELPER FUNCTIONS #######################
    def list_fleet(self):
        print("Vehicles Currently in Fleet:")
        for vehicle, count in self.fleet.items():
            print(f"{vehicle.ID}: {count} ({vehicle.fuel_type})")
        return

    def tidy_fleet(self):
        # Remove any item in self.fleet that's value is 0
        self.fleet = Counter({k: v for k, v in self.fleet.items() if v != 0})
        return 

####################################################################
def main():
    dataframes = DF()
    model = Model(dataframes)
    #yearly_requirements = model.yearly_requirements
    print(model.yearly_requirements.distance_km)
    print(model.yearly_requirements.distance)
    print(model.yearly_requirements.size)
    print(model.yearly_requirements.emission_limit)

    """
    model.purchase_vehicle('BEV_S2_2023', 'Electricity')
    print(model.total_costs, model.total_emissions)
    model.use_vehicle('BEV_S2_2023', 'Electricity', 500000)
    print(model.total_costs, model.total_emissions)
    model.sell_vehicle('BEV_S2_2023', 'Electricity')
    print(model.total_costs, model.total_emissions)
    model.insure('BEV_S2_2023')
    model.maintain('BEV_S2_2023')
    print(model.total_costs, model.total_emissions)
    model.purchase_vehicle('BEV_S2_2023', 'Electrical')
    model.sell_vehicle('BEV_S2_2023', 'Electrical')

    Considerations | Implementations:
        end_year = 2038
        How to calculate distance? 
    """

if __name__ == '__main__':
    main()

