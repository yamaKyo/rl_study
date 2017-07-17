import numpy as np
import gomoku
import AI

ALPHA = 0.1
GAMMA = 0.99
SCALE = 9

def learn(n_rounds, env, eps=0.1):
    Q = {}
    nb_actions = env.action_space.n
    for i in range(n_rounds):
        state = env._reset()
        state_str = state_to_string(state)
        if not state_str in Q:
            # 未到達の状態の場合，Q値をランダムで設定する．
            Q[state_str] = np.random.random(env.action_space.n)
        finish = False
        print("---start---")
        while not finish :
            print(state_str)
            if np.random.uniform() < eps:
                # epsの確率で，ランダムに選択する
                state = env._board.get_state()
                tmp = np.array(range(state.shape[0]))
                tmp = tmp[state == 0]
                if tmp.shape[0] == 0:
                    # 引き分け時でも呼ばれる可能性があるので，そのときは，-1をかえす
                    action = -1
                else:
                    action = np.random.choice(tmp)
            else:
                tmp = np.zeros(Q[state_str].shape[0]) + float("-inf")
                tmp[env._board.get_state() == 0] = Q[state_str][env._board.get_state() == 0]
                action = np.argmax(tmp)

            next_state, reward, finish, tmp = env._step(action)

            next_state_str = state_to_string(next_state)

            if not next_state_str in Q:
                # 未到達の状態の場合，Q値をランダムで設定する．
                Q[next_state_str] = np.random.random(nb_actions)

            Q[state_str][action]+=ALPHA *(reward + GAMMA*Q[next_state_str].max() - Q[state_str][action])
            state = next_state
            state_str = state_to_string(state)
    print("---end---")

def state_to_string(state):
    return ''.join(map(str, state))

if __name__ == "__main__":
    l_count = 100
    board = gomoku.Board(SCALE)
    env = AI.GomokuEnv(board)
    other = gomoku.RandomPlayer()
    other.set_board(board)
    env.set_other(other)
    learn(l_count, env)