import torch
import random
import numpy as np
from main import Main
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 64
LR = 5e-4

class Agent:

    def __init__(self, training=True):
        self.n_games = 0
        self.epsilon = 1 #randomness
        self.epsilon_end = 0.1
        self.epsilon_decay = 0.995
        self.gamma = 0.99 # discount rate?
        self.training = training
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()?
        self.model = Linear_QNet(19, 128, 3) #TODO: count inputs and change "11" to the inputs
        self.trainer = QTrainer(self.model, lr=LR, gamma = self.gamma) if training else None
        self.short_buffer = []
        self.short_batch_size = 8
        
    def run_trained_model(self, game, lvl, name):
        self.model.load(name)  # Load saved model weights
        self.model.eval()

        total_score = 0
        total_time = 0
        game_count = 0

        while True:
            state = self.get_state(game)
            action = self.get_action(state)  # uses the trained model
            state_new, reward, done, won, score, time = game.step(action)

            if done:
                game.res()
                game = Main(lvl, False)
                game_count += 1
                total_score += score
                total_time += time
                #print(f"[Game {game_count}] Score: {score} | Time: {time/1000:.2f}s | Won: {won}")

    def get_state(self, game):
        return game.gameState
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached 
    
    def train_long_term_memory(self):
        if len(self.memory) > BATCH_SIZE:
            # TODO : UNDERSTAND THIS LINE BELOW
            mini_sample = random.sample(self.memory, BATCH_SIZE) 
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, next_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)
    
    def train_short_term_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        """
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if (random.randint(0, 200) < self.epsilon or random.randint(0, 200) == 42) and self.training:
            if self.epsilon > 50 and random.randint(0, 1) == 0:
                move = 0
            else:
                move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0) # THIS MAY NEED TO CHANGE
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
        """
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        if random.random() < self.epsilon:
            move = random.randint(0,2)
        else:
            with torch.no_grad():
                move = torch.argmax(self.model(torch.tensor(state,dtype=torch.float))).item()
        final_move = [0,0,0]
        final_move[move] = 1
        return final_move
    
def train(model_name = "model"):
    plot_scores = []
    plot_mean_scores = []
    plot_score_times = []
    plot_mean_score_times = []
    plot_times = []
    plot_mean_times = []
    total_score = 0
    total_time = 0
    total_score_time = 0
    record = 1000000
    recordScore = 0
    recordScoreTime = 0
    agent = Agent()
    agent.model.train()
    game = Main(0, False, display=False)
    while True:
        #print(level)
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        state_new, reward, done, won, score, time = game.step(final_move)

        # train short term memory
        agent.train_short_term_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        

        
        if done:
            # train long memory, plot
            game.res()
            #print(level)
            game = Main(0, False, display=False)
            agent.n_games += 1
            agent.train_long_term_memory()

            # TODO: we want to save the model that got the best score ever
            # so we have to return a score at the end of each.
            if (score > recordScore):
                agent.model.save(model_name)
                recordScore = score
                print("yippee")
            """
            if (recordScoreTime < score / time and won):
                agent.model.save(model_name)
                record = time
                recordScoreTime = score / time
            elif (score > recordScore and not won):
                recordScore = score
                agent.model.save(model_name)"""
            #elif (score / time > recordScoreTime and not won):
            #    recordScoreTime = score / time
            #    agent.model.save(model_name)
                
            

            #print("Game: " + str(agent.n_games) + ", Score: " + str(score) + ", Time: " + str(time) + ", Won: " + str(won))
            #print("Game: " + str(agent.n_games) + ", Record Score: " + str(recordScore) + ", Record Score / Time: " + str(recordScoreTime / 1000) + ", Record Time: " + str(record))
        
            print("Game: " + str(agent.n_games) + ", Best Score: " + str(recordScore) + ", Score: " + str(score))
            
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)

            #plot_score_times.append(score / time)
            #total_score_time += score / time
            #mean_score_time = total_score_time / agent.n_games
            #plot_mean_score_times.append(mean_score_time)

            #if not won:
            #    time = 100
            #plot_times.append(time)
            #total_time += time
            #mean_time = total_time / agent.n_games
            #plot_mean_times.append(mean_time)

            plot(plot_scores, plot_mean_scores)
        



if __name__ == "__main__":
    #agent = Agent(training=False)
    #game = Main(3, False)
    #agent.run_trained_model(game, 3, "level_3")
    
    # Uncomment only one:
    train("to infinity and beyond")
    