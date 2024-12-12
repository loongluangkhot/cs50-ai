"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None
cache = {}


def get_cache_key(board):
    return "".join(i if i is not None else "-" for i in flatten_board(board))


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_x = 0
    count_o = 0
    for row in board:
        for i in row:
            if i == X:
                count_x += 1
            elif i == O:
                count_o += 1
    return X if count_x == count_o else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.append([i, j])
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    result_board = copy.deepcopy(board)
    curr_player = player(result_board)
    if result_board[action[0]][action[1]] == EMPTY:
        result_board[action[0]][action[1]] = curr_player
    else:
        raise Exception("Action is invalid!")
    return result_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    Assume there will be at most one winner.
    """
    def is_three_in_a_row(elems):
        return len(set(elems)) == 1 and elems[0] != EMPTY

    # Check rows
    for i in range(3):
        row = board[i]
        if is_three_in_a_row(row):
            return row[0]
    # Check cols
    for i in range(3):
        col = [board[0][i], board[1][i], board[2][i]]
        if is_three_in_a_row(col):
            return col[0]
    # Check diagonals
    diag_down = [board[0][0], board[1][1], board[2][2]]
    if is_three_in_a_row(diag_down):
        return diag_down[0]
    diag_up = [board[2][0], board[1][1], board[0][2]]
    if is_three_in_a_row(diag_up):
        return diag_up[0]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    def is_full_board():
        return len([i for i in flatten_board(board) if i == EMPTY]) == 0
    return winner(board) or is_full_board()


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    Assume function is only called on terminal board.
    """
    curr_winner = winner(board)
    if curr_winner == X:
        return 1
    elif curr_winner == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    elif player(board) == X:
        curr_actions = actions(board)
        curr_actions_min_values = [min_value(result(board,i)) for i in curr_actions]
        curr_max_value = max(curr_actions_min_values)
        for i in zip(curr_actions_min_values, curr_actions):
            if i[0] == curr_max_value:
                return i[1]
    else:
        curr_actions = actions(board)
        curr_actions_max_values = [max_value(result(board,i)) for i in curr_actions]
        curr_min_value = min(curr_actions_max_values)
        for i in zip(curr_actions_max_values, curr_actions):
            if i[0] == curr_min_value:
                return i[1]
    

def min_value(board):
    cache_key = get_cache_key(board)
    if cache_key in cache:
        return cache[cache_key]
    elif terminal(board):
        util = utility(board)
        cache[cache_key] = util
        return util
    else:
        v = math.inf
        curr_actions = actions(board)
        for i in curr_actions:
            i_max_value = max_value(result(board, i))
            v = min(v, i_max_value)
        cache[cache_key] = v
        return v


def max_value(board):
    cache_key = get_cache_key(board)
    if cache_key in cache:
        return cache[cache_key]
    elif terminal(board):
        util = utility(board)
        cache[cache_key] = util
        return util
    else:
        v = -math.inf
        curr_actions = actions(board)
        for i in curr_actions:
            i_min_value = min_value(result(board, i))
            v = max(v, i_min_value)
        cache[cache_key] = v
        return v


def flatten_board(board):
    return [i for row in board for i in row]