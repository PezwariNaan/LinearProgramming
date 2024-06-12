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
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(CustomEnv, self).__init__()

        # Load dataframes
        self.dataframes = DF()
        self.model = Model(self.dataframes)

        # Define action and observation space
        vehicles = self.model.vehicles_df
        num_vehicles = len(vehicles['ID'].unique())
        num_fuels = 2
        self.action_space = spaces.MultiDiscrete([num_vehicles, 2, 3])  # 0: purchase, 1: sell, 2: use
        
        obs_shape = self._get_obs().shape
        self.observation_space = spaces.Box(low=0, 
                                            high=1, 
                                            shape=obs_shape,
                                            dtype=np.float32)

    def _get_obs(self):
        obs = np.array([
            self.model.total_costs,
            self.model.total_emissions
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

        # Execute one time step within the environment
        if action_type == 0:
            self.model.purchase_vehicle(selected_vehicle,
                                        selected_fuel)
        elif action_type == 1:
            self.model.sell_vehicle(selected_vehicle,
                                    selected_fuel)
        elif action_type == 2:
            self.model.use_vehicle(selected_vehicle, 
                                   selected_fuel, 
                                   1000)
        
        obs = self._get_obs()
        reward = self._calculate_reward()
        done = self._is_done()
        info = {}

        # `done` now splits into `terminated` and `truncated`
        terminated = done
        truncated = False  # Set this based on your specific termination logic

        return obs, reward, terminated, truncated, info

    def _calculate_reward(self):
        # Define reward function
        reward = -self.model.total_costs  # Example: reward could be based on minimizing costs
        return reward

    def _is_done(self):
        # Define the condition for completing the episode
        done = (self.model.total_emissions > self.model.yearly_requirements.emission_limit)
        return done

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        self.model.list_fleet()

    def close(self):
        pass

