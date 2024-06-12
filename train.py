#!/usr/bin/env python3

import gymnasium as gym
from stable_baselines3 import PPO
from custom_env import CustomEnv

def main():
    # Create the environment
    env = CustomEnv()

    # Wrap the environment
    env = gym.wrappers.RecordEpisodeStatistics(env, deque_size = 10)
    env = gym.vector.SyncVectorEnv([lambda: env])

    # Create the agent
    model = PPO('MlpPolicy', env, verbose=1)

    # Train the agent
    model.learn(total_timesteps=10000)

    # Save the agent
    #model.save("ppo_custom_env")

    # Test the agent
    obs, _ = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            obs, _ = env.reset()

if __name__ == '__main__':
    main()
