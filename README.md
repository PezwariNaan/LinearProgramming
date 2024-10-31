# Fleet Optimization with Rolling Horizon Approach

This repository contains an optimization model for managing a vehicle fleet with a focus on sustainability and cost-effectiveness. Using `pulp`, the linear programming library for Python, this code implements a rolling horizon optimization to determine the optimal purchase, usage, and sale of fleet vehicles over multiple years. The goal is to minimize costs while meeting demand, respecting carbon emissions limits, and taking fuel and maintenance expenses into account.

## 📁 Project Structure

- `Model` Class: Defines the primary components of the model and manages vehicle and fuel data, demand, cost profiles, and carbon emissions.
  - `Vehicle` Class: Models each vehicle, storing attributes like ID and fuel type.
  - `create_problem()`: Sets up the linear programming problem.
  - `rolling_horizon_optimisation()`: Runs the rolling horizon approach from a given start to end year, solving the problem iteratively.
  - Helper functions (`extract_results()` and `print_results()`): Handle results extraction and display.

## 🛠️ Technologies Used

- **Python 3**: Primary language for implementing the model.
- **pandas**: Manages and processes data files.
- **pulp**: Linear programming library for setting up and solving the optimization problem.
- **NumPy**: Used for numerical operations, if required by the model.

## 📊 Data Files

The model uses several CSV data files. Make sure they are located in the `dataset/CSV_Files` folder as follows:

- **demand.csv**: Yearly demand by vehicle size and distance.
- **vehicles.csv**: Fleet vehicle information, including costs and yearly range.
- **vehicle_fuels.csv**: Fuel types and consumption rates for each vehicle.
- **fuels.csv**: Fuel prices, emission rates, and cost uncertainties.
- **carbon_emissions.csv**: Carbon emission limits per year.
- **cost_profiles.csv**: Cost profile data, including insurance, maintenance, and resale values based on vehicle age.
