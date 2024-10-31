# Fleet Management Simulation with Reinforcement Learning

This project is designed to simulate fleet management for a transportation company using a reinforcement learning environment. It leverages `gymnasium` for environment management and `stable-baselines3` for training an agent to minimize emissions, manage vehicle demands, and optimize costs. The environment simulates purchasing, selling, and utilizing various vehicle types, taking into account demand, emissions, and other factors. 


## Overview
The goal of the fleet management simulation is to train an agent to optimize the fleet's usage while adhering to demand and emission requirements. Vehicles in the fleet vary by size, distance capacity, and fuel type, and each action has an impact on overall cost, emissions, and demand satisfaction.

- **cost.py**: Defines classes for data handling (DF), vehicle management, cost management, and emissions tracking.
- **custom_env.py**: Defines the custom gym environment CustomEnv, which the RL agent interacts with.
- **main.py**: Script to run the training and testing of the RL agent using stable-baselines3.
- **dataset/CSV_Files**: Directory containing required datasets as CSV files.

## Explanation of Files
**cost.py**

The main file for data processing and vehicle management:

    DF: Loads all CSV files into Pandas DataFrames for easy access within other classes.
    Model: Manages the entire simulation model, including vehicle purchasing, using, and selling. Calculates total costs and emissions based on actions performed.
        YearlyRequirements: Sets up yearly demand and emissions limits.
        Vehicle: Class for vehicle attributes (size, fuel type, purchase year, etc.).
        purchase_vehicle, use_vehicle, sell_vehicle: Methods to manage the fleet.
        calculate_resale_value, add_cost: Utility methods for cost and depreciation management.

**custom_env.py**

Defines a custom environment based on gymnasium:

    CustomEnv: Gym environment for training agents. Defines:
        Action space: Vehicle selection, fuel type, and action type (purchase, use, sell).
        Observation space: State of demand, emissions, and costs.
        Reward system: Rewards the agent for optimizing fleet usage to meet demand and emission targets.

**main.py**

The main entry point:

    Loads the environment and initializes a PPO model using stable-baselines3.
    Runs the training and testing loop for 10,000 timesteps, outputting results at the end of each episode.

