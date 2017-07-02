# coding: utf-8
import gym
import gym.spaces
import numpy as np
import gomoku
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory
from datetime import datetime
from copy import deepcopy

SCALE = 9


def create_dqn(env, param_file=None):
    """
    DQNエージェントを生成する関数
    """
    nb_actions = env.action_space.n
    # DQNのネットワーク定義
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    print(model.summary())
    memory = SequentialMemory(limit=50000, window_length=1)
    # 行動方策はオーソドックスなepsilon-greedy。ほかに、各行動のQ値によって確率を決定するBoltzmannQPolicyが利用可能
    policy = GomokuEpsPolicy(env._board, eps=0.1)
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=100,
                   target_model_update=1e-2, policy=policy)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])
    if param_file:
        dqn.load_weights(param_file)

    return dqn


class GomokuEpsPolicy(EpsGreedyQPolicy):
    """
    epsilon-greedy + 置けない場所はフィルタリング
    すなわち，1-epsの確率で置ける場所のうち，q値が最大の場所を選ぶ
    """
    def __init__ (self, board, eps=.1):
        super(GomokuEpsPolicy, self).__init__(eps)
        self._board = board

    def select_action(self, q_values):
        """
        Q値に基づいて，行動を選択する関数
        :param q_values:
        :return:行動
        """
        if np.random.uniform() < self.eps:
            # epsの確率で，ランダムに選択する
            state = self._board.get_state()
            tmp = np.array(range(state.shape[0]))
            tmp = tmp[state == 0]
            if tmp.shape[0] == 0:
                # 引き分け時でも呼ばれる可能性があるので，そのときは，-1をかえす
                action = -1
            else:
                action = np.random.choice(tmp)
        else:
            assert self._board.get_state().shape[0] == q_values.shape[0]
            tmp = deepcopy(q_values)
            # 置けないところは，報酬を最小化
            if tmp[self._board.get_state() == 0].shape[0] == 0:
                action = -1
            else:
                tmp[self._board.get_state() != 0] = float("-inf")
                action = np.argmax(tmp)

        return action


class GomokuEnv(gym.core.Env):
    """
    五目並べの環境クラス
    """
    def __init__(self, board):
        self._board = board

        # 実行可能なアクションの空間らしい
        self.action_space = gym.spaces.Discrete(self._board._scale**2)

        # 碁盤を観測可能な状態とする
        # 観測対象の状態空間らしい
        high = np.zeros(self._board._scale**2)+2
        low = np.zeros(self._board._scale**2)
        self.observation_space = gym.spaces.Box(low=low, high=high)
        # 対戦相手
        self._other = None
        # 一番最初は，自分が先手で相手が後手
        # 実験ごとに，ランダムで入れ替える．
        self._color = 2

    def set_other(self, other):
        self._other = other
        self._other.set_color(1)

    def _step(self, action):
        """
        行動によって，状態を変更する関数
        """

        if action == -1:
            print ("unexpected output")
            self._board.output_status()
            assert False

        x, y = self._board.index_to_point(action)
        assert self._board.can_put_stone(x, y)

        self._board.put(x, y, self._color)
        ret = self._board.judge_game()
        if ret == self._color:
            return self._board.get_state(), 1, True, {}
        elif ret == 3:
            return self._board.get_state(), 0, True, {}
        else:
            x, y,color = self._other.action()
            self._board.put(x, y, color)
            ret = self._board.judge_game()
            if ret == self._other.get_color():
                return self._board.get_state(), -1, True, {}
            elif ret == 3:
                return self._board.get_state(), 0, True, {}
        return self._board.get_state(),0, False, {}

    def _reset(self):
        """
        初期状態を返す関数(?)
        """
        self._board.reset()
        self._other.reset()

        x, y, color = self._other.action()
        self._board.put(x, y , color)

        return self._board.get_state()


def learning(lcount, scount, in_file=None, out_file=None):
    """
    五目並べの学習をする関数
    """
    board = gomoku.Board(SCALE)
    env = GomokuEnv(board)

    if in_file is None:
        # 対戦相手が指定されない場合，ランダム
        other = gomoku.RandomPlayer()
    else:
        other = gomoku.AIPlayer(create_dqn(env, in_file))

    other.set_board(board)
    env.set_other(other)
    dqn = create_dqn(env, in_file)

    # AIの学習
    history = dqn.fit(env, nb_steps=lcount, visualize=False, verbose=2)
    print(history)
    if out_file:
        dqn.save_weights(out_file, True)

    # 学習結果に基づいて勝負
    return dqn, simulate(scount, dqn, other, True)

def simulate(count, dqn, other, change):
    """
    指定された回数だけ五目並べを繰り返す関数
    (先手での勝利数，後手での勝利数，AIで対応できなかった回数のリストを返す)
    """
    first_win = 0
    second_win = 0
    miss_count_list = []
    ai = gomoku.AIPlayer(dqn)
    ai.set_board(other.get_board())
    game = gomoku.Game(ai, other)
    game.reset()
    for i in range(count):
        print ("start simulation " + str(i))
        result = game.play(False)
        miss_count_list.append(ai.get_miss_count())
        if result == 1 and ai.get_color() == 1:
            first_win = first_win + 1
            print("AI is win")
        elif result == 2 and ai.get_color() == 2:
            second_win = second_win + 1
            print("AI is win")
        elif result == 3:
            print ("draw")
        else:
            print("AI is lose")
        game.reset()
        if change:
            game.change()

    return first_win, second_win, miss_count_list

if __name__ == "__main__":
    l_count = 1000000
    s_count = 100000

    dqn, result = learning(l_count, s_count,out_file=datetime.now().strftime("%Y%m%d%H%M%S"))
    first_win, second_win, miss = result
    print("---学習結果---")
    print("先手勝利:" + str(first_win))
    print("後手勝利:" + str(second_win))
    print("平均誤り：" + str(sum(miss)/len(miss)))
    print("最大誤り：" + str(max(miss)))
    print("--------------")
