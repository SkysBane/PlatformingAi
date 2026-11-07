import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from main import Main

# Constants you can tweak
LEARNING_RATE = 1e-3
GAMMA = 0.99
EPSILON = 0.2
BATCH_SIZE = 64
NUM_EPOCHS = 10

class PolicyNetwork(nn.Module):
    def __init__(self, input_dim, action_dim):
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
            nn.Tanh()  # Outputs between -1 and 1
        )

    def forward(self, x):
        return self.fc(x)
    

class ValueNetwork(nn.Module):
    def __init__(self, input_dim):
        super(ValueNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.fc(x)

def calculate_ppo_loss(policy_net, value_net, states, actions, rewards, next_states, dones):
    states = torch.tensor(states, dtype=torch.float32)
    actions = torch.tensor(actions, dtype=torch.float32)
    rewards = torch.tensor(rewards, dtype=torch.float32)
    next_states = torch.tensor(next_states, dtype=torch.float32)
    dones = torch.tensor(dones, dtype=torch.float32)

    # Calculate advantages
    values = value_net(states).squeeze()
    next_values = value_net(next_states).squeeze()
    advantages = rewards + GAMMA * next_values * (1 - dones) - values

    # Normalize advantages
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    # Policy loss
    new_log_probs = torch.log(policy_net(next_states).gather(-1, actions.long().unsqueeze(-1)).squeeze())
    old_log_probs = torch.log(policy_net(states).gather(-1, actions.long().unsqueeze(-1)).squeeze())
    ratios = torch.exp(new_log_probs - old_log_probs)
    surr1 = ratios * advantages
    surr2 = torch.clamp(ratios, 1 - EPSILON, 1 + EPSILON) * advantages
    policy_loss = -torch.min(surr1, surr2).mean()

    # Value loss
    value_loss = nn.MSELoss()(values, rewards + GAMMA * next_values * (1 - dones))

    return policy_loss + value_loss

def update_networks(policy_net, value_net, optimizer, states, actions, rewards, next_states, dones):
    optimizer.zero_grad()
    loss = calculate_ppo_loss(policy_net, value_net, states, actions, rewards, next_states, dones)
    loss.backward()
    optimizer.step()

# Modify this function to change training parameters
def train_ppo(env, policy_net, value_net, optimizer, num_episodes):
    for episode in range(num_episodes):
        state = env.res()
        done = False
        while not done:
            state_tensor = torch.tensor(state).float().unsqueeze(0)
            action_tensor = policy_net(state_tensor)
            action = action_tensor.detach().numpy()[0]

            new_state, reward, done = env.step(action)
            reward = np.array([reward])
            done = np.array([done], dtype=np.float32)

            # Store data for training
            states = state
            actions = action
            rewards = reward
            next_states = new_state
            dones = done

            # Update networks
            update_networks(policy_net, value_net, optimizer, states, actions, rewards, next_states, dones)

            state = new_state
            #num_episodes = 64

        if episode % 10 == 0:
            print(f"Episode {episode} complete")

# Entry point for running the training
#if __name__ == "__main__":
#    # Example usage
#    input_dim = 65  # Change this to match your input size
#    action_dim = 2  # Change this to match your output size
#    policy_net = PolicyNetwork(input_dim, action_dim)
#    value_net = ValueNetwork(input_dim)
#    optimizer = optim.Adam(list(policy_net.parameters()) + list(value_net.parameters()), lr=LEARNING_RATE)

    # Placeholder for your environment
    #class DummyEnv:
    #    def reset(self):
    #        return np.zeros(input_dim)
    #    
    #    def step(self, action):
    #       new_state = np.random.rand(input_dim)
    #       reward = np.random.rand()
    #        done = np.random.rand() > 0.95
    #       return new_state, reward, done, {}

#    env = Main(0, False)
#    train_ppo(env, policy_net, value_net, optimizer, num_episodes=1000)
