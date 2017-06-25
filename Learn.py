import gym
import gym.spaces
import numpy as np
import gomoku
import itertools
import random


class OtherPlayer(object):
    def __init__(self, scale):
        self._scale = scale
        self._actions = set([])
        self._color = None

        # 置くことができる場所を集合として持っておく
        for x in range(0, self._scale):
            for y in range(0, self._scale):
                self._actions.add((x, y))

    def reset(self):
        """
        おける場所をリセットする
        """
        self._actions = []
        for x in range(0, self._scale):
            for y in range(0, self._scale):
                self._actions.add((x, y))

    def delete(self, action):
        """
        相手の行った手をおける場所から削除する
        """
        self._actions.remove(action)

    def put(self):
        """
        ランダムに置く場所を選択する．
        """
        x, y = random.choice(self._actions)
        self._actions.remove((x, y))
        return (x, y)

    def getColor(self):
        """
        色を取得する
        """
        return self._color

    def SetColor(self, color):
        """
        色を設定する
        """
        self._color = color


class GomokuEnv(gym.core.Env):
    """
    五目並べの環境クラス
    """
    def __init__(self, scale, other):
        self._board = gomoku.Board(self._scale)
        xs = range(0, self._scale)
        ys = range(0, self._scale)
        # 座標1次元配列として保持しておく．
        self._actionIndex = list(itertools.product(xs, ys))

        # 実行可能なアクションの空間らしい
        self.action_space = gym.spaces.Discrete(len(self._actionIndex))

        # 碁盤を観測可能な状態とする
        # 観測対象の状態空間らしい
        self.observation_space = gym.spaces.Box(low=0, high=self._scale-1)
        self._color = 1

        # 対戦相手
        self._other = other
        self._other.SetColor(2)

    def _step(self, action):
        """
        行動によって，状態を変更する関数
        """
        x, y = self._actionIndex[action]
        # 報酬：
        # -1：置けない場所に置こうとした
        #  0：置いて，勝敗付かず
        #  0：置いて，勝った
        #  0: 置いて，負け
        reward = 0
        done = False
        if(self._board.puttable(x, y)):
            # 自分がおけるなら，置く
            self._board.put(x, y, self._color)
            reward = 0
            if self._board.judgeGame() != 0:
                done = True
            else:
                # 相手が置く
                x, y = self._other.put()
                self._board.put(x, y, self._other.getColor())
                if self._board.judgeGame() != 0:
                    done = True
        else:
            reward = -1

        return np.array(self._board._cells), reward, done, {}

    def _reset(self):
        """
        初期状態を返す関数(?)
        """
        self._board = gomoku.Board(self._scale)
        colors = set([1, 2])
        # 対戦相手の色を設定
        otherCol = random.choice(colors)
        self._other.reset()
        self._other.SetColor(otherCol)
        # 自分の色を設定
        colors.remove(otherCol)
        myCol = colors[0]
        self._color = myCol

        # 対戦相手が先手のとき
        if otherCol < myCol:
            x, y = self._other.put()
            self._board.put(x, y)

        return np.array(self._board._cells)
