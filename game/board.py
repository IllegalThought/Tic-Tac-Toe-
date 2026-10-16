"""Immutable board and rules; indices 0..8, row-major."""
EMPTY = ('',) * 9
LINES = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
def winning_line(board):
    return next((line for line in LINES if board[line[0]] and len({board[i] for i in line}) == 1), None)
def winner(board):
    line = winning_line(board)
    return board[line[0]] if line else None
def terminal(board):
    return winner(board) is not None or all(board)
def legal_moves(board):
    return [] if terminal(board) else [i for i, cell in enumerate(board) if not cell]
def play(board, move, side):
    if side not in ('X','O') or move not in legal_moves(board):
        raise ValueError('Illegal move')
    return board[:move] + (side,) + board[move+1:]
def other(side):
    return 'X' if side == 'O' else 'O'
def terminal_score(board):
    # Absolute occupied-cell count makes faster wins preferred, cache-safe.
    win = winner(board)
    magnitude = 100 - sum(bool(c) for c in board)
    return magnitude if win == 'O' else -magnitude if win == 'X' else 0
