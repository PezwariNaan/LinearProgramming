#!/usr/bin/env python3

from cost import Model, DF

def main():
    dataframes = DF()
    model = Model(dataframes)

    print(f"Demand Left: {model.yearly_requirements.demand_left}")
    print(f"Carbon Emissions: {model.total_emissions}")
    """
    for i in range(0, 3):
        model.purchase_vehicle('LNG_S2_2023', 'LNG')
    model.list_fleet()
    model.use_vehicle('LNG_S2_2023', 'LNG', 106000)
    print(f"Demand Left: {model.yearly_requirements.demand_left + (106000 * 4)}")
    print(f"Demand Left: {model.yearly_requirements.demand_left}")
    print(f"Carbon Emissions: {model.total_emissions}")
    """

    all_vehicles = model.vehicles_df[model.vehicles_df['Year'] == 2023]['ID'].values
    for vehicle in all_vehicles:
        if vehicle.startswith('BEV'):
            model.purchase_vehicle(vehicle, 'Electricity')
        if vehicle.startswith('LNG'):
            model.purchase_vehicle(vehicle, 'LNG')
            model.purchase_vehicle(vehicle, 'BioLNG')
        if vehicle.startswith('Diesel'):
            model.purchase_vehicle(vehicle, 'HVO')
            model.purchase_vehicle(vehicle, 'B20')

    for vehicle in model.fleet:
        print(vehicle.ID, vehicle.fuel_type)
        model.use_vehicle(vehicle.ID, vehicle.fuel_type, vehicle.yearly_range)
    print(f"Demand Left: {model.yearly_requirements.demand_left}")
    print(f"Carbon Emissions: {model.total_emissions}")

    return 0

if __name__ == '__main__':
    main()

