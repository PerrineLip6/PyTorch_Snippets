import torch
import gym
import random
import torch.optim as optim
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt


import util
from models import DQN
from policies import EpsDecay, Greedy
from deep_agent import Agent, QBuffer


env = gym.make("LunarLander-v2")
state_size = env.observation_space.shape[0]
action_size = env.action_space.n

device = torch.device("cpu")

seed = 1651
np.random.seed(seed)
random.seed(seed)
torch.manual_seed(seed)
env.seed(seed)

nb_epi_max = 5000
max_step = 1000
gamma = .99

alpha = 5e-4
eps_start = 1
eps_decay = 0.995
eps_min = 0.01

batch_size = 64
memory_size = int(1e5)

average_goal = 200
goal_size = 200

model = DQN(net_structure=(state_size, 128, 128, action_size), gamma=gamma, optim=optim.Adam, optim_param=[alpha],
            loss_function=nn.MSELoss(), tau=1, device=device)

buffer = QBuffer(memory_size, batch_size, device)
learning_policy = EpsDecay(eps_start, eps_min, eps_decay, env.action_space.n)
playing_policy = Greedy()
agent = Agent(model=model, buffer=buffer, learn_every=4, update_every=4, policy_learning=learning_policy,
              policy_playing=playing_policy)

scores = util.learn(env, goal_size, average_goal, agent, max_step, nb_epi_max, gamma, learning_policy)

print(len(buffer))
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(np.arange(len(scores)), scores)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.show()


for i in range(10):
    state = env.reset()
    score = 0
    env.render()
    for j in range(max_step):
        action = agent.act(state)
        env.render()
        state, reward, done, _ = env.step(action)
        score += reward
        if done:
            break
    print(score)

env.close()


def play_dqn(filename, n=10, seed=0):
    env = gym.make("CartPole-v0")
    env.seed(seed)
    env.reset()
    model = DQN(net_structure=(state_size, 64, 64, action_size), gamma=gamma, optim=optim.Adam, optim_param=[alpha],
                loss_function=nn.MSELoss(), tau=0.1, device=device)

    buffer = ReplayBuffer(memory_size, batch_size, device)
    learning_policy = EpsDecay(eps_start, eps_min, eps_decay, env.action_space.n)
    playing_policy = Greedy()
    agent = Agent(model=model, buffer=buffer, learn_every=4, update_every=4, policy_learning=learning_policy,
                  policy_playing=playing_policy)
    model.predict.load_state_dict(torch.load(filename))
    agent.playing()
    for i in range(n):
        state = env.reset()
        score = 0
        env.render()
        for j in range(99999999999):
            action = agent.act(state)
            env.render()
            state, reward, done, _ = env.step(action)
            score += reward
            if done:
                break
        print(score)
    env.close()
