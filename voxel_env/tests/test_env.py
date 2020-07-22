import time

import numpy as np

from unittest import TestCase

from voxel_env.voxel_env_gym import VoxelEnv


def sample_actions(e):
    return [e.action_space.sample() for _ in range(e.num_agents)]


class TestEnv(TestCase):
    def test_env(self):
        e = VoxelEnv()
        o = e.reset()
        o = e.step(sample_actions(e))
        e.close()

    def test_two_envs_same_process(self):
        e1 = VoxelEnv()
        e2 = VoxelEnv()

        e1.reset()
        e2.reset()

        e1.close()
        e2.close()

    def test_seeds(self):
        e1 = VoxelEnv()
        e1.seed(42)
        e2 = VoxelEnv()
        e2.seed(42)

        obs1 = e1.reset()
        obs2 = e2.reset()

        self.assertTrue(np.array_equal(obs1, obs2))

        for i in range(100):
            actions = sample_actions(e1)
            obs1, rews1, dones1, infos1 = e1.step(actions)
            obs2, rews2, dones2, infos2 = e2.step(actions)

            self.assertTrue(np.array_equal(obs1, obs2))
            self.assertEqual(rews1, rews2)
            self.assertEqual(dones1, dones2)
            self.assertEqual(infos1, infos2)

    def test_render(self):
        e1 = VoxelEnv()
        e2 = VoxelEnv()

        e1.reset()
        e2.reset()

        e1.render()
        e2.render()

        for i in range(100):
            e1.step(sample_actions(e1))
            e1.render()
            e2.step(sample_actions(e2))
            e2.render()

        e1.close()
        e2.close()

    @staticmethod
    def performance_num_envs(n, n_steps=5000):
        envs = [VoxelEnv() for _ in range(n)]
        for e in envs:
            e.reset()

        actions = sample_actions(e)
        start = time.time()
        for step in range(n_steps):
            for i, e in enumerate(envs):
                obs, rew, dones, infos = e.step(actions)
                if all(dones):
                    print(f'Episode boundary env {i}')
        end = time.time()
        elapsed = end - start
        fps = envs[0].num_agents * n * n_steps / elapsed
        print(f'Time {elapsed:.3f}, fps: {fps:.1f}')

        for e in envs:
            e.close()
        return fps

    def test_performance(self):
        fps1 = self.performance_num_envs(1)
        fps2 = self.performance_num_envs(2)
        fps4 = self.performance_num_envs(4)

        print(fps1, fps2, fps4)