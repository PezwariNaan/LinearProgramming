#!/usr/bin/env python3

import pandas as pd
import pulp as pl
import numpy as np

class Model:
    class Vehicle:
        def __init__(self, id, fuel):
            self.id = id
            self.fuel = fuel

        def __hash__(self):
            return hash((self.id, self.fuel))

        def __str__(self):
            return f"{self.id}_{self.fuel}"

        def __repr__(self): 
            return self.__str__()

        def __eq__(self, other):
            if isinstance(other, Model.Vehicle):
                return self.id == other.id and self.fuel == other.fuel
            return False

    ######################## LOAD DATA #########################
    def __init__(self):
        dir = '/home/haxor/Documents/Competitions/Shell/dataset/CSV_Files/'
        self.demand = pd.read_csv(dir + 'demand.csv')
        self.vehicles = pd.read_csv(dir + 'vehicles.csv')
        self.vehicle_fuels = pd.read_csv(dir + 'vehicle_fuels.csv')
        self.fuels = pd.read_csv(dir + 'fuels.csv')
        self.carbon_emissions = pd.read_csv(dir + 'carbon_emissions.csv')
        self.cost_profiles = pd.read_csv(dir + 'cost_profiles.csv')
        self.year = 2023

    def create_problem(self):
        ######################### SETUP #############################
        problem = pl.LpProblem(f"Fleet_Optimization_{self.year}", pl.LpMinimize)
        
        list_of_vehicles = []

        #fueltype = {ID: {fuel: consumption_rate}}
        vehicle_fueltype = self.vehicle_fuels[self.vehicle_fuels['ID'].str.contains(str(self.year))].groupby('ID').apply(
            lambda x: x.set_index('Fuel')['Consumption (unit_fuel/km)'].to_dict(),
            include_groups = False
        ).to_dict()

        for vehicle in vehicle_fueltype:
            for fuel in vehicle_fueltype[vehicle]:
                list_of_vehicles.append(self.Vehicle(vehicle, fuel))

        ######################## DEFINE DECISION VARIABLES #############################
        number_purchased = {vehicle: pl.LpVariable(f"num_purchased_{vehicle}", lowBound=0, cat="Integer") \
                for vehicle in list_of_vehicles}

        number_used = {vehicle: pl.LpVariable(f"num_used_{vehicle}", lowBound= 0, cat="Integer") \
                for vehicle in list_of_vehicles}

        number_sold = {vehicle: pl.LpVariable(f"num_sold_{vehicle}", lowBound=0, cat="Integer") \
                for vehicle in list_of_vehicles}

        ################################# VEHICLE | FUEL VALUES #############################

        vehicle_cost = self.vehicles[self.vehicles['Year'] == \
                self.year].set_index('ID')['Cost ($)'].to_dict()

        vehicle_age = (self.vehicles.set_index('ID')['Year'] - self.year + 1).to_dict()

        vehicle_max_range = self.vehicles[self.vehicles['Year'] == self.year]\
                .set_index('ID')['Yearly range (km)'].to_dict()

        vehicle_distance = self.vehicles[self.vehicles['Year'] == self.year]\
                .set_index('ID')['Distance'].to_dict()

        vehicle_size = self.vehicles[self.vehicles['Year'] == self.year]\
                .set_index('ID')['Size'].to_dict()

        fuel_price = self.fuels[self.fuels['Year'] == self.year]\
                .set_index('Fuel')['Cost ($/unit_fuel)'].to_dict()

        fuel_emission_rate = self.fuels[self.fuels['Year'] == self.year]\
                .set_index('Fuel')['Emissions (CO2/unit_fuel)'].to_dict()

        ############################# DEMANDS ##############################

        carbon_limit = self.carbon_emissions[self.carbon_emissions['Year'] == \
                self.year]['Carbon emission CO2/kg'].item()

        demand_matrix = self.demand[self.demand['Year'] == self.year]\
                .pivot(index='Size', columns='Distance', values='Demand (km)')
        yearly_demand = demand_matrix.sum().sum()

        ############################# YEARLY FLEET COSTS ###############################

        cost_to_insure   = {vehicle: vehicle_cost[vehicle.id] * self.cost_profiles[self.cost_profiles['End of Year'] == \
                vehicle_age[vehicle.id]]['Insurance Cost %'].item() / 100 for vehicle in list_of_vehicles}

        cost_to_maintain = {vehicle: vehicle_cost[vehicle.id] * self.cost_profiles[self.cost_profiles['End of Year'] == \
                vehicle_age[vehicle.id]]['Maintenance Cost %'].item() / 100 for vehicle in list_of_vehicles} 

        sale_price = {vehicle: vehicle_cost[vehicle.id] * self.cost_profiles[self.cost_profiles['End of Year'] == \
                vehicle_age[vehicle.id]]['Resale Value %'].item() / 100 for vehicle in list_of_vehicles} 
        
        ############################ CONSTRAINTS ###################################

        # Use / Sell constraints - Can't use / sell more than owned
        for vehicle in list_of_vehicles:
            problem += number_used[vehicle] <= number_purchased[vehicle], f"Use_Constraint_{vehicle}"
            problem += number_sold[vehicle] <= number_purchased[vehicle], f"Sell_Constraint_{vehicle}"

         # Emission constraint
        total_emissions = pl.lpSum([number_used[vehicle] * vehicle_fueltype[vehicle.id][vehicle.fuel] * fuel_emission_rate[vehicle.fuel] 
                                    for vehicle in list_of_vehicles])

        problem += total_emissions <= carbon_limit, "Total_Emission_Constraint"

        # Demand must reach 0

        # Must sell vehicle at ten year point
        for vehicle in list_of_vehicles:
                    if vehicle_age[vehicle.id] >= 10:
                        problem += number_sold[vehicle] ==\
                                number_purchased[vehicle], f"Age_Limit_Constraint_{vehicle.id}"


        # Must sell less than 20% of fleet per year
        problem += pl.lpSum(number_sold.values()) <= 0.2 * \
                pl.lpSum(number_purchased.values()), "Fleet_Sell_Constraint"

        ############################# OBJECTIVE FUNCTION ###############################
        total_cost = pl.lpSum([number_purchased[vehicle] * vehicle_cost[vehicle.id] + 
                                   number_used[vehicle] * (sum(fuel_price[vehicle.fuel] * vehicle_fueltype[vehicle.id][vehicle.fuel] \
                                           for vehicle in list_of_vehicles) + cost_to_maintain[vehicle] + cost_to_insure[vehicle]) - \
                                   number_sold[vehicle] * sale_price[vehicle] for vehicle in list_of_vehicles])

        problem += total_cost, "Total Cost"

        self.problem = problem
        print(self.problem)
        exit()

        return self.problem
    
    ######################### IMPLEMENT ROLLING HORIZON APPROACH ####################
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

