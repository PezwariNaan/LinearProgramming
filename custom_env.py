#!/usr/bin/env python3

import random
import gymnasium as gym
import pandas as pd
import numpy as np
from collections import Counter
from gymnasium import spaces
from cost import DF, Model
from pathlib import Path
from os import getenv

class CustomEnv(gym.Env):
    metadata = {'render_modes': ['ansi']}

    def __init__(self):
        super(CustomEnv, self).__init__()

        # Load dataframes
        self.dataframes = DF()
        self.model = Model(self.dataframes)

        # Define action and observation space
        vehicles = self.model.vehicles_df
        year = self.model.current_year
        num_vehicles = len(vehicles[vehicles['Year'] == year]['ID'].unique())
        num_fuels = 2
        num_moves = 3
        self.action_space = spaces.MultiDiscrete([num_vehicles, num_fuels, num_moves])  # 0: purchase, 1: sell, 2: use

        obs_shape = self._get_obs().shape
        self.observation_space = spaces.Box(low=0, 
                                            high=3.4028235e+38, 
                                            shape=obs_shape,
                                            dtype=np.float32)

    def _get_obs(self):
        obs = np.array([
            self.model.total_costs,
            self.model.total_emissions,
            self.model.yearly_requirements.demand_left,
        ], dtype=np.float32)
        return obs

    def reset(self, seed=None, options = None):
        super().reset(seed=seed)
        self.dataframes = DF()
        self.model = Model(self.dataframes)
        return self._get_obs(), {}

    def step(self, action):
        vehicle_index, fuel_index, action_type = action

        vehicles = self.model.vehicles_df[self.model.vehicles_df['Year'] == \
                self.model.current_year]['ID'].values

        selected_vehicle = vehicles[int(vehicle_index)]
        fuels = self.model.vehicle_fuels_df[self.model.vehicle_fuels_df['ID'] == \
                selected_vehicle]['Fuel'].values

        if selected_vehicle.startswith('BEV'):
            selected_fuel = fuels[0]
        else:
            selected_fuel = fuels[int(fuel_index)]

        selected_vehicle = self.model.Vehicle(selected_vehicle, 
                                     selected_fuel,
                                     self.model.vehicles_df)

        # Execute one time step within the environment
        if action_type == 0:
            self.model.purchase_vehicle(selected_vehicle.ID,
                                        selected_vehicle.fuel_type)
            print(f"Purchased: {selected_vehicle.ID}")
        elif action_type == 1:
            self.model.use_vehicle(selected_vehicle.ID, 
                                   selected_vehicle.fuel_type, 
                                   selected_vehicle.yearly_range)
            print(f"Used: {selected_vehicle.ID}")
        elif action_type == 2:
            self.model.sell_vehicle(selected_vehicle.ID,
                                    selected_vehicle.fuel_type)
            print(f"Sold: {selected_vehicle.ID}")

        obs = self._get_obs()
        reward = self._calculate_reward()
        done = self._is_done()
        info = {}

        # `done` now splits into `terminated` and `truncated`
        terminated = done
        truncated = False  # Set this based on your specific termination logic

        if terminated:
            print("Episode Done")
            self.model.list_fleet()

        return obs, reward, terminated, truncated, info

    def _calculate_reward(self):
        # Define reward function

        reward = -self.model.total_costs  # Example: reward could be based on minimizing costs
        reward = -self.model.yearly_requirements.demand_left
        return reward

    def _is_done(self):
        # Define the condition for completing the episode
        done = (self.model.total_emissions > self.model.yearly_requirements.emission_limit)
        done = (self.model.yearly_requirements.demand_left <= 0)
            
        return done

    def render(self, mode='ansi', close=False):
        # Render the environment to the screen
        self.model.list_fleet()

    def close(self):
        pass

