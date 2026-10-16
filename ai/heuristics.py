from game.board import LINES, play, other, legal_moves, winner

def threats(board, side):
    return [i for i in legal_moves(board) if winner(play(board,i,side)) == side]
def forks(board, side):
    return [i for i in legal_moves(board) if len(threats(play(board,i,side), side)) >= 2]
def ordered_moves(board, side):
    wins, blocks = set(threats(board,side)), set(threats(board,other(side)))
    own_forks, enemy_forks = set(forks(board,side)), set(forks(board,other(side)))
    def priority(i):
        return (0 if i in wins else 1 if i in blocks else 2 if i in own_forks else 3 if i in enemy_forks else 4 if i == 4 else 5 if i in (0,2,6,8) else 6, i)
    return sorted(legal_moves(board), key=priority)
def evaluate(board):
    score = 0
    for line in LINES:
        cells = [board[i] for i in line]
        if 'X' not in cells: score += (0, 1, 6, 0)[cells.count('O')]
        if 'O' not in cells: score -= (0, 1, 6, 0)[cells.count('X')]
    score += 2 * ((board[4] == 'O') - (board[4] == 'X'))
    score += sum((board[i] == 'O') - (board[i] == 'X') for i in (0,2,6,8))
    score += 3 * (len(forks(board,'O')) - len(forks(board,'X')))
    return max(-50, min(50, score))
