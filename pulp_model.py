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
        
        self.list_of_vehicles = []

        #fueltype = {ID: {fuel: consumption_rate}}
        vehicle_fueltype = self.vehicle_fuels[self.vehicle_fuels['ID'].str.contains(str(self.year))].groupby('ID').apply(
            lambda x: x.set_index('Fuel')['Consumption (unit_fuel/km)'].to_dict(),
            include_groups = False
        ).to_dict()

        for vehicle in vehicle_fueltype:
            for fuel in vehicle_fueltype[vehicle]:
                self.list_of_vehicles.append(self.Vehicle(vehicle, fuel))

        ######################## DEFINE DECISION VARIABLES #############################
        self.number_purchased = {vehicle: pl.LpVariable(f"num_purchased_{vehicle}", lowBound=0, cat="Integer") \
                for vehicle in self.list_of_vehicles}

        self.number_used = {vehicle: pl.LpVariable(f"num_used_{vehicle}", lowBound= 0, cat="Integer") \
                for vehicle in self.list_of_vehicles}

        self.number_sold = {vehicle: pl.LpVariable(f"num_sold_{vehicle}", lowBound=0, cat="Integer") \
                for vehicle in self.list_of_vehicles}

        #percentage_used = {vehicle: pl.LpVariable(f"percentage_used_{vehicle}", lowBound=0, upBound=100, cat="Integer") \
        #        for vehicle in self.list_of_vehicles}

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

        #yearly_demand = demand_matrix.sum().sum()

        ############################# YEARLY FLEET COSTS ###############################

        cost_to_insure   = {vehicle: vehicle_cost[vehicle.id] * self.cost_profiles[self.cost_profiles['End of Year'] == \
                vehicle_age[vehicle.id]]['Insurance Cost %'].item() / 100 for vehicle in self.list_of_vehicles}

        cost_to_maintain = {vehicle: vehicle_cost[vehicle.id] * self.cost_profiles[self.cost_profiles['End of Year'] == \
                vehicle_age[vehicle.id]]['Maintenance Cost %'].item() / 100 for vehicle in self.list_of_vehicles} 

        sale_price = {vehicle: vehicle_cost[vehicle.id] * self.cost_profiles[self.cost_profiles['End of Year'] == \
                vehicle_age[vehicle.id]]['Resale Value %'].item() / 100 for vehicle in self.list_of_vehicles} 
        
        total_emissions = pl.lpSum([self.number_used[vehicle] * vehicle_fueltype[vehicle.id][vehicle.fuel] * \
                 fuel_emission_rate[vehicle.fuel] for vehicle in self.list_of_vehicles])

        ############################ CONSTRAINTS ###################################

        # Use / Sell constraints - Can't use / sell more than owned
        for vehicle in self.list_of_vehicles:
            problem += self.number_used[vehicle] <= self.number_purchased[vehicle], f"Use_Constraint_{vehicle}"
            problem += self.number_sold[vehicle] <= self.number_purchased[vehicle], f"Sell_Constraint_{vehicle}"

        problem += total_emissions <= carbon_limit, "Total_Emission_Constraint"

        """
        for size in demand_matrix.index:
            for distance in demand_matrix.columns:
                demand = demand_matrix.at[size, distance]
                problem += pl.lpSum([self.number_used[vehicle] * vehicle_max_range[vehicle.id] 
                                     for vehicle in self.list_of_vehicles if vehicle_size[vehicle.id] == size and vehicle_distance[vehicle.id] >= distance]) == \
                            demand, f"Demand_Constraint_{size}_{distance}"
        exit()
        """
        # Must sell vehicle at ten year point
        for vehicle in self.list_of_vehicles:
                    if vehicle_age[vehicle.id] >= 10:
                        problem += self.number_sold[vehicle] ==\
                                self.number_purchased[vehicle], f"Age_Limit_Constraint_{vehicle.id}"

        # Must sell less than 20% of fleet per year
        problem += pl.lpSum(self.number_sold.values()) <= 0.2 * \
                pl.lpSum(self.number_purchased.values()), "Fleet_Sell_Constraint"

        ############################# OBJECTIVE FUNCTION ###############################
        # Need to add fuel usage to total_cost
        total_cost = pl.lpSum([self.number_purchased[vehicle] * vehicle_cost[vehicle.id] + 
                                   self.number_used[vehicle] * (sum(fuel_price[vehicle.fuel] * vehicle_fueltype[vehicle.id][vehicle.fuel] \
                                           for vehicle in self.list_of_vehicles) + cost_to_maintain[vehicle] + cost_to_insure[vehicle]) - \
                                   self.number_sold[vehicle] * sale_price[vehicle] for vehicle in self.list_of_vehicles])

        problem += total_cost, "Total Cost"

        self.problem = problem

        return self.problem
    
    ######################### IMPLEMENT ROLLING HORIZON APPROACH ####################
    def rolling_horizon_optimization(self, start_year, end_year, horizon):
        fleet = {} # Dictionary  = Vehicle : Count
        for year in range(start_year, end_year + 1):
            model = self.create_problem()
            model.solve()
        return 

    ######################## GET RESULTS ######################
    def solve_problem(self):
        self.problem.solve()
        return self.problem.status

    def save_results(self, filepath):
        results = []

        for vehicle in self.list_of_vehicles:
            results.append({
                'vehicle_id': vehicle.id,
                'fuel': vehicle.fuel,
                'number_purchased': self.number_purchased[vehicle].varValue,
                'number_used': self.number_used[vehicle].varValue,
                'number_sold': self.number_sold[vehicle].varValue
            })

        results_df = pd.DataFrame(results)
        results_df.to_csv(filepath, index=False)

# Main function
def main():
    model = Model()
    model.create_problem()
    status = model.solve_problem()

    if status == pl.LpStatusOptimal:
        model.save_results('/home/haxor/Documents/Competitions/Shell/Code/Python/src/Model/results.csv')
    else:
        print("The problem does not have an optimal solution.")

if __name__ == "__main__":
    main()

