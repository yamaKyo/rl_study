# coding: utf-8
import numpy as np

class Player(object):
    """
    五目並べのプレイヤークラス
    """
    def __init__(self):
        self._color = None
        self._board = None

    def reset(self):
        """
        状態を初期化する関数
        """
        pass

    def action(self):
        """
        置く場所を返す関数
        :return (x座標,y座標,色）のタプルを返す
        """
        pass

    def get_color(self):
        """
        設定されている色を返す関数
        :return 設定されている色
        """
        return self._color

    def set_color(self, color):
        """
        色を設定する
        :param color: 設定する色
        """
        self._color = color

    def set_board(self, board):
        """
        対戦に使う碁盤を設定する関数
        :param board:碁盤
        """
        self._board = board

    def get_board(self):
        """
        現在使っている碁盤を返す関数
        :return: 碁盤
        """
        return self._board


class HumanPlayer(Player):
    """
    プレイヤーの入力に従って石を配置するクラス
    """
    def __init__(self):
        super(HumanPlayer, self).__init__()

    def action(self):
        x = None
        y = None
        while x is None or y is None:
            # 置ける座標が指定されるまでループ
            print("あなたのターンです:")
            text = input()
            if not (text is None):
                pos = text.split(" ")
                if len(pos) == 2:
                    pos_x = int(pos[0])
                    pos_y = int(pos[1])
                if self._board.can_put_stone(pos_x, pos_y):
                    x = pos_x
                    y = pos_y
        return x, y, self.get_color()

    def reset(self):
        pass


class RandomPlayer(Player):
    """
    ランダムに石を配置するクラス
    """
    def __init__(self):
        super(RandomPlayer, self).__init__()

    def reset(self):
        pass

    def action(self):
        # 置ける場所のIndexを取得
        tmp = self.get_board().get_valid_cells_index()
        index = int(np.random.choice(tmp[0]))
        x, y = self.get_board().index_to_point(index)
        return x, y, self.get_color()


class AIPlayer(Player):
    """
    AIを使って置く位置を決めるプレイヤー
    置けないとこを出力された時のことを考えて，
　　内部には，ランダムプレイヤーも持っておく
    """
    def __init__(self, ai):
        super(AIPlayer, self).__init__()
        self._ai = ai
        # 置けなかった時のために，ランダムプレイヤーを保持
        # ランダムに頼った回数を記録
        self._miss_count = 0

    def get_miss_count(self):
        """
        AIが置けない場所を出力した回数を返す関数
        """
        return self._miss_count

    def action(self):
        index = self._ai.forward(self.get_board().getState())
        x, y = self.get_board().index_to_point(index)
        if self._board.can_put_stone(x, y):
            return x, y,self.get_color()
        else:
            # 置ける場所のIndexを取得
            tmp = self.get_board().get_valid_cells_index()
            index = np.random.choice(tmp)
            x, y = self.get_board().index_to_point(index)
            return x, y, self.get_color()

    def reset(self):
        self._miss_count = 0


class Board(object):

    def __init__(self, scale):
        """
        碁盤オブジェクトのコンストラクタ
        :param scale: 碁盤のサイズ
        """
        self._scale = scale
        # 学習高速化のため，1次元配列として，碁盤の方法を保持
        self._cells = np.zeros(self._scale ** 2)
        self._history = []

    def get_state(self):
        return self._cells

    def get_valid_cells_index(self):
        return np.where(self._cells == 0)

    def set_val(self, x,y, val):
        """
        碁盤の指定座標に値を指定する関数
        :param x: x座標
        :param y: y座標
        :param val: 設定する状態
        """
        self._cells[self.point_to_index(x, y)] = val

    def get_val(self, x, y):
        """
        碁盤の指定座標の値を取得する関数
        :param x:x座標
        :param y:y座標
        :return:指定座標の状態
        """
        return self._cells[self.point_to_index(x, y)]

    def index_to_point(self, index):
        """
        配列インデックスを配列に変換する関数
        :param index:
        :return:
        """
        y = index // self._scale
        x = index % self._scale
        return int(x),int(y)

    def point_to_index(self, x,y):
        """
        座標を配列のインデックスに変換する関数
        :param x: x座標
        :param y: y座標
        :return: インデックス
        """
        return y * self._scale + x

    def get_last_action(self):
        """
        最後に置かれた石の情報を返す関数
        :return (x座標, y座標, 石の色)のタプル
        """
        if len(self._history) > 0:
            return self._history[-1]
        else:
            None

    def reset(self):
        """
        碁盤の状態を初期化する関数
        """
        self._cells = np.zeros(self._scale ** 2)
        self._history = []

    def get_turn_count(self):
        """
        現在のターン数を返す関数
        :return ターン数
        """
        return len(self._history)

    def put(self, x, y, color):
        """
        指定された座標に指定された石を置く関数
        :param x:x座標
        :param y:y座標
        :param color:石の色
        """
        self.set_val(x,y,color)
        # 終了判定判定に使うので，最後においたところを記録しておく．
        self._history.append((x, y, color))

    def is_out_of_board(self, x, y):
        """
        指定された座標がボードの外かどうかを返す関数
        """
        return (0 > x) or (x > self._scale - 1) or (0 > y) or (y > self._scale - 1)

    def can_put_stone(self, x, y):
        """
        指定された座標に，石がおけるか返す関数
        :param x:x座標
        :param y:y座標
        :return:置けるならTrue/置けないならFalse
        """

        if self.is_out_of_board(x, y):
            return False
        if self.get_val(x,y) != 0:
            return False
        return True

    def judge_game(self, debug=False):
        """
        ゲームが終了したかどうかを返す関数
        :param debug:デバッグ情報を出力するかどうか
        :return 継続(0)，引き分け(3),勝った方の色を返す
        """
        last_x, last_y, last_color = self._history[-1]
        # 引き分け判定
        # 全部チェックは馬鹿らしいのでおいた数でチェック
        if self.get_turn_count() >= self._scale**2 :
            return 3

        # 横方向の探索
        line = 1
        # 右方向に同じ色が続いてるかを調べる
        for i in range(last_x+1, self._scale, 1):
            if self.get_val(i,last_y) == last_color:
                line = line + 1
            else:
                break
        # 左方向に同じ色が続いているかを調べる
        for i in range(last_x-1, -1, -1):
            if self.get_val(i, last_y) ==last_color:
                line = line + 1
            else:
                break
        if debug:
            print("[DEBUG]横方向:" + str(line))

        if line >= 5:
            return last_color

        # 縦方向の探索
        line = 1
        # 下方向に同じ色が続いてるかを調べる
        for i in range(last_y+1, self._scale, 1):
            if self.get_val(last_x,i) == last_color:
                line = line + 1
            else:
                break
        # 上方向に同じ色が続いてるかを調べる
        for i in range(last_y-1, -1, -1):
            if self.get_val(last_x,i) == last_color:
                line = line + 1
            else:
                break
        if debug:
            print("[DEBUG]縦方向:" + str(line))
        if line >= 5:
            return last_color

        # 右斜め方向の探索
        line = 1
        # 右上方向に同じ色が続いてるかを調べる
        for x, y in [(last_x+i, last_y-i) for i in range(1, min(last_y+1, self._scale - last_x),1) ]:
            if self.get_val(x,y) == last_color:
                line = line + 1
            else:
                break
        # 左下方向に同じ色が続いてるかを調べる
        for x, y in [(last_x-i, last_y+i) for i in range(1, min(last_x+1, self._scale - last_y),1)]:
            if self.get_val(x,y) == last_color:
                line = line + 1
            else:
                break
        if debug:
            print("[DEBUG]右斜め:" + str(line))
        if line >= 5:
            return last_color

        # 左斜め方向の探索
        line = 1
        # 左上方向に同じ色が続いてるかを調べる
        for x, y in [(last_x-i, last_y-i) for i in range(1, min(last_y+1, last_x+1), 1)]:
            if self.get_val(x,y) == last_color:
                line = line + 1
            else:
                break
        # 右下方向に同じ色が続いてるかを調べる
        for x , y in [(last_x+i, last_y+i) for i in range(1, min(self._scale - last_x , self._scale - last_y), 1)]:
            if self.get_val(x,y) == last_color:
                line = line + 1
            else:
                break
        if debug:
            print("[DEBUG]左斜め方向:" + str(line))
        if line >= 5:
            return last_color

        return 0

    def show_board(self):
        """
        碁盤を描画する
        """
        raw = ["|" for i in range(self._scale+1)]
        raw[self._scale] = " ====="
        underline = "-" + ("-" * (self._scale * 4))
        print(underline)
        for i in range(self._scale):
            for j in range(self._scale):
                if self.get_val(j,i) == 0:
                    raw[i] += "   "
                if self.get_val(j,i) == 1:
                    raw[i] += " o "
                if self.get_val(j,i) == 2:
                    raw[i] += " * "
                raw[i] += "|"
            print(raw[i])
            print(underline)
        print(raw[self._scale])


class Game(object):
    """
    五目並べのゲームクラス
    """
    def __init__(self, first, second, board):
        """
        ゲームクラスのコンストラクタ
        :param first:先手
        :param second:後手
        :param board:碁盤
        """
        self._first = first
        self._first.set_color(1)
        self._first.set_board(board)
        self._board = board
        self._second = second
        self._second.set_color(2)
        self._second.set_board(board)

    def play(self, display):
        """
        五目並べをプレイする関数
        :param display:画面に進行状況を出力するかどうか
        :return 試合の結果
        """
        result = 0
        actor = self._first
        while result == 0:
            if display:
                if actor == self._first:
                    print("先手のターン")
                else:
                    print("後手のターン")

            if display:
                self._board.show_board()
            # 勝敗が決まるまでループ
            x, y,col = actor.action()
            self._board.put(x, y, col)

            if display:
                print("%d 手目：%d , %d , %d" % (self._board.get_turn_count(), x, y, col))

            result = self._board.judge_game()
            if actor == self._first:
                actor = self._second
            else:
                actor = self._first

        return result

    def reset(self):
        """
        プレイヤーや碁盤の状態をリセットする関数
        """
        self._first.reset()
        self._second.reset()
        self._board.reset()

    def change(self):
        """
        先手/後手を入れ替える関数
        """
        first_col = self._first.get_color()
        second_col = self._second.get_color()

        tmp = self._first
        self._first = self._second
        self._first.set_color(first_col)
        self._second = tmp
        self._second.set_color(second_col)


if __name__ == "__main__":
    scale = 9
    board = Board(scale)
    player1 = HumanPlayer()
    player2 = RandomPlayer()
    game = Game(player1, player2, board)
    result = game.play(True)
    # 結果の出力
    if result == 1:
        print("先手の勝利")
    if result == 2:
        print("後手の処理")
    if result == 3:
        print("引き分け")
