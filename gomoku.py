# coding: utf-8

import random


class Computer(object):

    def __init__(self, color):
        # 実行した手の履歴
        self.history = []
        # 刺した手に対する報酬
        self.fee = []
        self._color = color

    def put(self, status):
        """
        盤面の情報に基づいて，次に置く位置を返す関数
        """
        pass

    def learn(self, win):
        """
        勝利したかどうかに基づいて，学習するクラス
        """
        pass


class Board(object):

    def __init__(self, scale):
        self._scale = scale
        self._cells = cells=[[0 for i in xrange(self._scale)] for j in xrange(self._scale)]
        self._latestX = None
        self._latestY = None
        self._latestColor = None
        self._turnCount = 0

    def put(self, x, y, color):
        """
        指定された箇所に指定された石を置く関数
        """
        self._cells[x][y] = color

        # 終了判定判定に使うので，最後においたところを記録しておく．
        self._latestX = x
        self._latestY = y
        self._latestColor = color
        self._turnCount = self._turnCount+1

    def isOutOfBoard(self, x, y):
        """
        指定された座標がボードの外かどうかを返す関数
        """
        return (0 > x) or (x > self._scale - 1) or (0 > y) or (y > self._scale - 1)

    def puttable(self, x, y):
        """
        指定された座標に，石をおくことができるかどうか返す関数
        """
        if self.isOutOfBoard(x, y):
            return False
        if self._cells[x][y] != 0:
            return False
        return True

    def judgeGame(self):
        """
        ゲームが終了したかどうかを返す関数
        """

        # 引き分け判定
        # 全部チェックは馬鹿らしいのでおいた数でチェック
        if(self._turnCount >= self._scale**2):
            return 3

        # 横方向の探索
        line = 1
        # 右方向に同じ色が続いてるかを調べる
        for i in range(self._latestX+1, self._scale, 1):
            if self._cells[i][self._latestY] == self._latestColor:
                line = line + 1
            else:
                break
        # 左方向に同じ色が続いているかを調べる
        for i in range(self._latestX-1, -1, -1):
            if self._cells[i][self._latestY] == self._latestColor:
                line = line + 1
            else:
                break
        print("[DEBUG]横方向:" + str(line))

        if line >= 5:
            return self._latestColor

        # 縦方向の探索
        line = 1
        # 下方向に同じ色が続いてるかを調べる
        for i in range(self._latestY+1, self._scale, 1):
            if self._cells[self._latestX][i] == self._latestColor:
                line = line + 1
            else:
                break
        # 上方向に同じ色が続いてるかを調べる
        for i in range(self._latestY-1, -1, -1):
            if self._cells[self._latestX][i] == self._latestColor:
                line = line + 1
            else:
                break
        print("[DEBUG]縦方向:" + str(line))
        if line >= 5:
            return self._latestColor

        # 右斜め方向の探索
        line = 1
        # 右上方向に同じ色が続いてるかを調べる
        for x, y in [(self._latestX+i, self._latestY-i) for i in range(1, min(self._latestY+1, self._scale - self._latestX),1) ]:
            if self._cells[x][y] == self._latestColor:
                line = line + 1
            else:
                break
        # 左下方向に同じ色が続いてるかを調べる
        for x, y in [(self._latestX-i, self._latestY+i) for i in range(1, min(self._latestX+1, self._scale - self._latestY),1)]:
            if self._cells[x][y] == self._latestColor:
                line = line + 1
            else:
                break
        print("[DEBUG]右斜め:" + str(line))
        if line >= 5:
            return self._latestColor

        # 左斜め方向の探索
        line = 1
        # 左上方向に同じ色が続いてるかを調べる
        for x, y in [(self._latestX-i, self._latestY-i) for i in range(1, min(self._latestY+1, self._latestX+1), 1)]:
            if self._cells[x][y] == self._latestColor:
                line = line + 1
            else:
                break
        # 右下方向に同じ色が続いてるかを調べる
        for x , y in [(self._latestX+i, self._latestY+i) for i in range(1, min(self._scale - self._latestX , self._scale - self._latestY), 1)]:
            if self._cells[x][y] == self._latestColor:
                line = line + 1
            else:
                break
        print("[DEBUG]左斜め方向:" + str(line))
        if line >= 5:
            return self._latestColor

        return 0

    def drawBoard(self):
        """
        碁盤を描画する
        """
        raw = ["|" for i in xrange(self._scale+1)]
        raw[self._scale] = " ====="
        underline = "-" + ("-" * (self._scale * 4))
        print(underline)
        for i in xrange(self._scale):
            for j in xrange(self._scale):
                if self._cells[j][i] == 0:
                    raw[i] += "   "
                if self._cells[j][i] == 1:
                    raw[i] += " o "
                if self._cells[j][i] == 2:
                    raw[i] += " * "
                raw[i] += "|"
            print raw[i]
            print underline
        print raw[self._scale]

if __name__ == "__main__":
    scale = 19
    board = Board(scale)
    result = 0
    turn = True
    board.drawBoard()
    while (result == 0):
        if turn:
            # 人間のターン
            print "Your Turn:"
            input = raw_input()
            if not (input is None):
                input = input.split(" ")
                if len(input) == 2:
                    posX = int(input[0])
                    posY = int(input[1])
                    if board.puttable(posX, posY):
                        board.put(posX, posY, 1)
                        result = board.judgeGame()
                        board.drawBoard()
                        turn = not turn
        else:
            # CPUのターン(ランダム配置)
            eposX = random.randint(0, scale)
            eposY = random.randint(0, scale)
            if board.puttable(eposX, eposY):
                print "CPU:" + str(eposX)+" "+str(eposY)
                board.put(eposX, eposY, 2)
                result = board.judgeGame()
                board.drawBoard()
                turn = not turn

    # 結果の出力
    if result == 1:
        print "1 WIN"
    if result == 2:
        print "2 WIN"
    if result == 3:
        print "DRAW"
