#!/usr/bin/env python3

import pandas as pd
import pulp as pl
import numpy as np

class Model:
    # Load data
    def __init__(self):
        # Cost profiles isn't returned because we don't need it yet
        dir = '/home/haxor/Documents/Competitions/Shell/dataset/CSV_Files/'
        self.demand = pd.read_csv(dir + 'demand.csv')
        self.vehicles = pd.read_csv(dir + 'vehicles.csv')
        self.vehicle_fuels = pd.read_csv(dir + 'vehicle_fuels.csv')
        self.fuels = pd.read_csv(dir + 'fuels.csv')
        self.carbon_emissions = pd.read_csv(dir + 'carbon_emissions.csv')
        self.cost_profiles = pd.read_csv(dir + 'cost_profiles.csv')
        self.year = 2023
        return 

    def create_problem(self):
        problem = pl.LpProblem(f"Fleet_Optimization_{self.year}", pl.LpMinimize)
        
        # Define decision variables
        list_of_vehicles = self.vehicles[self.vehicles['Year'] == \
                self.year]['ID'].values

        vehicle_cost             = self.vehicles[self.vehicles['Year'] == \
                self.year].set_index('ID')['Cost ($)'].to_dict()
        print(vehicle_cost)
        exit()

        number_purchased         = None # Number Purchased
        number_used              = None # Second Variable 
        number_sold              = None # Third Variable

        vehicle_name             = None 
        vehicle_fueltype         = None
        vehicle_range            = None

        fuel_price               = 0
        fuel_consumption_rate    = 0
        fuel_emission_rate       = 0

        cost_to_insure           = None # Probably a function 
        cost_to_maintain         = None # Probably a function 
        
        distance_covered         = 0
        carbon_emissions         = self.carbon_emissions[self.carbon_emissions['Year'] == \
                self.year]['Carbon emission CO2/kg'].item()
        

        # Set up constraints
        problem += distance_covered * fuel_emission_rate  * \
                fuel_consumption_rate  <= carbon_emissions
        percentage_of_fleet_sold = None

        # Define objective function
        total_cost               = None

        return problem
    
    def update_fleet(self):
        pass

    # Implement rolling horizon approach
    def rolling_horizon_optimization(self, start_year, end_year, horizon):
        fleet = {} # Dictionary  = Vehicle : Count
        for year in range(start_year, end_year + 1):
            model = self.create_problem()
            model.solve()
            self.update_fleet()

# Main function
def main():
    model = Model()
    model.rolling_horizon_optimization(2023, 2038, 5)

if __name__ == "__main__":
    main()
