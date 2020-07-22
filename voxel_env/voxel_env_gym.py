import cv2
import gym
import numpy as np

from gym.spaces import Discrete

# noinspection PyUnresolvedReferences
from voxel_env.extension.voxel_env import VoxelEnvGym


class VoxelEnv(gym.Env):
    def __init__(self, num_agents=2):
        self.img_w = 128
        self.img_h = 72

        self.num_agents = num_agents
        self.env = VoxelEnvGym(self.img_w, self.img_h, self.num_agents)
        self.action_space = self.generate_action_space()

        self.empty_infos = [{} for _ in range(self.num_agents)]

    @staticmethod
    def generate_action_space():
        """
        Left = 1 << 1,
        Right = 1 << 2,

        Forward = 1 << 3,
        Backward = 1 << 4,

        LookLeft = 1 << 5,
        LookRight = 1 << 6,

        LookDown = 1 << 7,
        LookUp = 1 << 8,
        """
        space = gym.spaces.Tuple((
            Discrete(3),  # noop, go left, go right
            Discrete(3),  # noop, forward, backward
            Discrete(3),  # noop, look left, look right

            # TODO: use other actions
        ))

        return space

    def seed(self, seed=None):
        if seed is None:
            return

        assert isinstance(seed, int), 'Expect seed to be an integer'
        self.env.seed(seed)

    def observations(self):
        obs = []
        for i in range(self.num_agents):
            o = self.env.get_observation(i)
            o = o[:, :, :3]
            obs.append(o)

        return obs

    def reset(self):
        self.env.reset()
        return self.observations()

    def set_agent_actions(self, agent_idx, actions):
        action_idx = 0
        action_mask = 0
        spaces = self.action_space.spaces
        for i, action in enumerate(actions):
            if action > 0:
                action_mask = action_mask | (1 << (action_idx + action))
            num_non_idle_actions = spaces[i].n - 1
            action_idx += num_non_idle_actions

        self.env.set_action_mask(agent_idx, action_mask)

    def step(self, actions):
        for i, agent_actions in enumerate(actions):
            self.set_agent_actions(i, agent_actions)

        done = self.env.step()
        dones = [done for _ in range(self.num_agents)]
        rewards = [self.env.get_last_reward(i) for i in range(self.num_agents)]

        if done:
            obs = self.reset()
        else:
            obs = self.observations()

        return obs, rewards, dones, self.empty_infos

    def convert_obs(self, obs):
        obs = cv2.flip(obs, 0)
        obs = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)

        aspect_ratio = self.img_w / self.img_h
        render_w = 600
        obs = cv2.resize(obs, (render_w, int(render_w / aspect_ratio)))
        return obs

    def render(self, mode='human'):
        obs = [self.convert_obs(self.env.get_observation(i)) for i in range(self.num_agents)]
        obs_concat = np.concatenate(obs, axis=1)
        cv2.imshow(f'agent_{0}_{id(self)}', obs_concat)
        cv2.waitKey(1)

    def close(self):
        if self.env:
            self.env.close()