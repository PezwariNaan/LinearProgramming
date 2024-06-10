#!/usr/bin/env python3

from shell import DF
import pulp as p

DATAFRAMES = DF()

def getAge(ID:str, year:int) -> int:
    vehicles = DATAFRAMES.vehicles
    vehicle_year = vehicles.loc[vehicles['ID'] == ID]['Year'].item()
    return year - vehicle_year + 1

def ownershipCosts(ID:str, cost_type:str, year:int) -> int:
    """
        Insurance Cost
        Resale Value
        Maintenance Cost
    """
    cost_profiles = DATAFRAMES.cost_profiles
    age = getAge(ID, year)
    values = cost_profiles.loc[cost_profiles['End of Year'] == age]
    return values[cost_type].item() / 100

def main():
    year = 2023
    #end_year = 2038
    demand = 869181
    emission_limit = 11677957

    vehicles = DATAFRAMES.vehicles
    vehicles = vehicles[vehicles['Year'] == year]

    vehicle_fuels = DATAFRAMES.vehicle_fuels
    vehicle_fuels = vehicle_fuels[vehicle_fuels['ID'].str.contains(".*_2023")]

    fuels = DATAFRAMES.fuels
    fuels = fuels[fuels['Year'] == year]

    vehicle_fuels_dict = {}

    # Extract relevant data
    vehicle_ids = vehicles['ID'].tolist()
    for id in vehicle_ids:
        vehicle_fuels_dict[id] = vehicle_fuels.loc[vehicle_fuels['ID'] == id]\
                .set_index('Fuel')['Consumption (unit_fuel/km)'].to_dict()
    vehicle_fuels = vehicle_fuels_dict

    vehicle_costs = vehicles.set_index('ID')['Cost ($)'].to_dict()
    vehicle_range = vehicles.set_index('ID')['Yearly range (km)'].to_dict()
    fuel_costs = fuels.set_index('Fuel')['Cost ($/unit_fuel)'].to_dict()
    emission_rates = fuels.set_index('Fuel')['Emissions (CO2/unit_fuel)'].to_dict()
    insurance_costs = {}
    maintenance_costs = {}
    resale_value = {}

    for vehicle in vehicle_ids:
        insurance_costs[vehicle]   = vehicle_costs[vehicle] * ownershipCosts(vehicle, 'Insurance Cost %' , year)
        maintenance_costs[vehicle] = vehicle_costs[vehicle] * ownershipCosts(vehicle, 'Maintenance Cost %' , year)
        resale_value[vehicle]      = vehicle_costs[vehicle] * ownershipCosts(vehicle, 'Resale Value %' , year)
    
    # Define the problem
    problem = p.LpProblem("Shell_V1", p.LpMinimize)

    vehicle_vars = p.LpVariable.dicts("Vehicle", vehicle_ids, lowBound=0, cat='Integer')

    # Define the objective function: Minimize total cost
    total_cost = p.lpSum([vehicle_vars[v_id] * vehicle_costs[v_id] for v_id in vehicle_ids]) + \
                 p.lpSum([vehicle_vars[v_id] * vehicle_range[v_id] * vehicle_fuels[v_id][fuel] * \
                 fuel_costs[fuel] for v_id in vehicle_ids for fuel in vehicle_fuels[v_id]]) + \
                 p.lpSum([vehicle_vars[v_id] * insurance_costs[v_id] for v_id in insurance_costs]) + \
                 p.lpSum([vehicle_vars[v_id] * maintenance_costs[v_id] for v_id in maintenance_costs]) - \
                 p.lpSum([vehicle_vars[v_id] * resale_value[v_id] for v_id in resale_value]) 


    problem += total_cost, "Total Cost"
    print(problem)

    total_demand_met = p.lpSum([vehicle_vars[v_id] * vehicle_range[v_id] for v_id in vehicle_ids])
    problem += total_demand_met >= demand, "Demand Constraint"

    total_emissions = p.lpSum([vehicle_vars[v_id] * vehicle_range[v_id] * vehicle_fuels[v_id][fuel] * \
            emission_rates[fuel] for v_id in vehicle_ids for fuel in vehicle_fuels[v_id]])
    problem += total_emissions <= emission_limit, "Emission Constraint"
    print(problem)

    # Solve the problem
    problem.solve()

    # Print the results
    print(f"Status: {p.LpStatus[problem.status]}")
    for v_id in vehicle_ids:
        print(f"{v_id}: {p.value(vehicle_vars[v_id])}")
    print(f"Total Cost: ${p.value(problem.objective):.2f}")

if __name__ == '__main__':
    main()

