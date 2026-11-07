import torch
import numpy as np
from ppo import PolicyNetwork, ValueNetwork
from main import Main


# Constants you can tweak
INPUT_DIM = 64  # Change this to match your input size
ACTION_DIM = 2  # Change this to match your output size

# Initialize networks
policy_net = PolicyNetwork(INPUT_DIM, ACTION_DIM)

def run_ai(envv, policy_net):
    state = env.res()
    done = False
    while not done:
        state_tensor = torch.tensor(state).float().unsqueeze(0)
        action_tensor = policy_net(state_tensor)
        action = action_tensor.detach().numpy()[0]

        new_state, reward, done = envv.step(action)
        state = new_state

        print(f"Action: {action}, Reward: {reward}")

# Placeholder for your environment
#class DummyEnv:
#    def reset(self):
#        return np.zeros(INPUT_DIM)
#    
#   def step(self, action):
#       new_state = np.random.rand(INPUT_DIM)
#        reward = np.random.rand()
#        done = np.random.rand() > 0.95
#       return new_state, reward, done, {}

env = Main(0, False)
run_ai(env, policy_net)
