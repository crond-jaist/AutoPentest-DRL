import sys

import gym
import numpy as np
import gym.spaces
import torch

from io import StringIO

from generateMap import generateMap

class dqnEnvironment(gym.Env):
    metadata = {'render.modes': ['human', 'ansi']}
    MAP = np.loadtxt('../processdata/newmap.txt')
    line = len(MAP)
    observation_map = np.zeros((line,line), dtype=float)


    def __init__(self):
        super().__init__()
        self.action_space = gym.spaces.Discrete(self.line) 
        self.reset()

    def reset(self):
        # parameters initialize
        self.pos = 0
        self.goal = self.line - 1
        self.done = False
        self.steps = 0
        return self._observe(self.pos)

    def step(self, action):
        global next_state
        self.next_state = action
        self.state = [self.pos, self.next_state]

        self.pos = self.next_state
        self.steps = self.steps + 1

        observation = self._observe(self.next_state)
        reward = self._get_reward(self.state)

        self.done = self._is_done()
        total_steps = self.steps

        return observation, reward, self.done, total_steps

    def _close(self):
        pass

    def _seed(self, seed=None):
        pass

    def _get_reward(self, state):
        self.reward = self.MAP[tuple(state)]
        return self.reward

    def _observe(self, state):
        self.observation = state

        return self.observation

    def _is_done(self):
        if (self.pos == self.goal):
            return True
        else:
            return False

    def _start_state(self):
        return self._find_pos('S')[0]
