import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import numpy as np

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.bn_input = nn.BatchNorm1d(input_size)
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        if x.dim() == 1:
            x = x.unsqueeze(0)
        # apply batch-norm to the raw inputs
        x = self.bn_input(x)
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, file_name="model.pth"):
        model_folder_path = f'./models'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

    def load(self, file_name="model.pth"):
        model_folder_path = f'./models'
        file_path = os.path.join(model_folder_path, file_name)
        self.load_state_dict(torch.load(file_path))
        self.eval()  # set model to inference mode

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float) #these types may need to change
        next_state = torch.tensor(next_state, dtype=torch.float) #these types may need to change
        action = torch.tensor(action, dtype=torch.long) #these types may need to change
        reward = torch.tensor(reward, dtype=torch.float) #these types may need to change

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        # 1: predicted Q values with current state TODO: figure out what a Q value is
        pred = self.model(state)

        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            a = action[idx]  # get just the one action vector
            if isinstance(a, (list, tuple, np.ndarray)):
                a = torch.tensor(a, dtype=torch.float)
            action_idx = torch.argmax(a).item()
            if action_idx < target[idx].shape[0]:
                target[idx][action_idx] = Q_new
            else:
                print(f"⚠️ Invalid action index: {action_idx} for target shape {target[idx].shape}")
            


        # 2: Q_new = r + y * max(next_predicted Q value)
        #  pred.clone()
        #  preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()

