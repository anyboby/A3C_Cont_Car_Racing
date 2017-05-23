import gym
import numpy as np
from config import WorldConfig


def crop(frame, length=12):
    """
    crop 96 by 96 to 84 by 84
    """
    h = len(frame)
    w = len(frame[0])
    return frame[0:h - length, length/2:w - length/2]

def rgb2gray(frame):
    return 0.2989 * frame[:,:,0] + 0.5879 * frame[:,:,1] + 0.1140 * frame[:,:,2]

def edge_detection(frame):
    return frame

def zero_center(frame):
    return np.divide(frame - 127, 127.0)

class World(object):
    """
    World class that represents a single instance of the openAi env.
    This class handles all operations regarding the interaction / 
    background processing of the game environment.
    """

    def __init__(self, world_name, render=False):
        """
        Create the specified world and make it blank-slate
        """
        self.env = gym.make(world_name)
        self._env_state = self.env.reset()
        self._frame_stack = [self._process_frame(self._env_state)] * \
                        (WorldConfig.NUM_FRAMES_IN_STATE + 1)
        self.actions = WorldConfig.ACTIONS
        self.terminal = False
        self.num_tiles = 0
        self.rewards = 0.0
        self.render = render

    def _process_frame(self, frame):
        """
        preprocess a state which is given as : (96, 96, 3)
        """
        frame = rgb2gray(frame) # squash to 96 x 96
        frame = zero_center(frame)
        frame = crop(frame)
        return frame

    def get_state(self):
        """
        returns a 3-d (after last action)state array of size (84, 84, 5)
        """
        return np.stack(self_frame_stack[1:], axis=2)

    def get_prev_state(self):
        """
        returns a 3-d (before last action)state array of size (84, 84, 5)
        """
        return np.stack(self._frame_stack[:-1], axis=2)

    def is_terminal(self):
        return self.terminal

    def get_num_tiles(self):
        return self.num_tiles

    def get_rewards(self):
        return self.rewards

    def reset(self):
        self._env_state = self.env.reset()
        self.terminal = False
        self.num_tiles = 0
        self.rewards = 0.0
        self._frame_stack = [self._process_frame(self._env_state)] * \
                        (WorldConfig.NUM_FRAMES_IN_STATE + 1)

    def step(self, action_num, certainty=1.0):
        """
        action_num : GAS, BRAKE, LEFT, RIGHT in order 0123
        certainty : the softmax score of the chosen action.
        """
        action = np.multiply(self.actions[action_num], certainty)

        # Take step in the world
        self._env_state, r, self.terminal, _ = self.env.step(action)

        # Update frame stack
        self._frame_stack.pop(0)
        self._frame_stack.append(self._env_state)

        # Update cumulative reward R
        self.rewards += r

        # If we moved forward, increment num_tiles
        if r >= 0.0: self.num_tiles += 1

        if self.render: self.env.render()

    def print_stats(self):
        print "Rewards:"+str(self.rewards)+"| Num Tiles: "+str(self.num_tiles)

if __name__ == "__main__":
    """
    For compile testing
    """
    world = World(WorldConfig.NAME, render=True)
    while not world.is_terminal():
        world.step(0)

    world.print_stats()