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

        number_purchased = {vehicle: pl.LpVariable(f"num_purchased_{vehicle}", lowBound=0, cat="Integer") \
                for vehicle in list_of_vehicles}
        
        number_used = {vehicle: pl.LpVariable(f"num_used_{vehicle}", lowBound= 0, cat="Integer") \
                for vehicle in list_of_vehicles}

        number_sold = {vehicle: pl.LpVariable(f"num_sold_{vehicle}", lowBound=0, cat="Integer") \
                for vehicle in list_of_vehicles}

        vehicle_cost = self.vehicles[self.vehicles['Year'] == \
                self.year].set_index('ID')['Cost ($)'].to_dict()

        #fueltype = {ID: {fuel: consumption_rate}}
        vehicle_fueltype = self.vehicle_fuels[self.vehicle_fuels['ID'].str.contains(str(self.year))].groupby('ID').apply(
            lambda x: x.set_index('Fuel')['Consumption (unit_fuel/km)'].to_dict(),
            include_groups = False
        ).to_dict()

        fuel_price  = self.fuels[self.fuels['Year'] == self.year]\
                .set_index('Fuel')['Cost ($/unit_fuel)'].to_dict()

        fuel_emission_rate = self.fuels[self.fuels['Year'] == self.year]\
                .set_index('Fuel')['Emissions (CO2/unit_fuel)'].to_dict()
        
        distance_covered = 0

        carbon_limit = self.carbon_emissions[self.carbon_emissions['Year'] == \
                self.year]['Carbon emission CO2/kg'].item()

        cost_to_insure   = None # Probably a function 
        cost_to_maintain = None # Probably a function 
        sale_price       = None # Probably a function 
        
        # Set up constraints
        """
        problem += distance_covered * fuel_emission_rate  * \
                fuel_consumption_rate  <= carbon_limit
        """
        # Must sell less than 20% of fleet per year
        percentage_of_fleet_sold = None

        # Make sure vehicles used and sold are owned
        for vehicle in list_of_vehicles:
            problem += number_used[vehicle] <= number_purchased[vehicle], f"Use_Constraint_{vehicle}"
            problem += number_sold[vehicle] <= number_purchased[vehicle], f"Sell_Constraint_{vehicle}"

        self.number_purchased = number_purchased
        self.number_used = number_used
        self.number_sold = number_sold

        # Ensure distance vehicle travels is less than the yearly_range
        vehicle_max_range = self.vehicles[self.vehicles['Year'] == self.year]\
                .set_index('ID')['Yearly range (km)'].to_dict()
        
        print(problem)
        exit()

        # Define objective function
        total_cost               = None

        return problem
    
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

