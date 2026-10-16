from game.board import EMPTY, play, other, terminal, winner
class GameManager:
    def __init__(self):
        self.scores = {'X':0, 'O':0, 'Draw':0}
        self.restart()
    def restart(self, starter='X'):
        self.board, self.turn, self.finished = EMPTY, starter, False
    def move(self, index):
        if self.finished:
            raise ValueError('Game is over')
        self.board = play(self.board, index, self.turn)
        if terminal(self.board):
            self.finished = True
            self.scores[winner(self.board) or 'Draw'] += 1
        else:
            self.turn = other(self.turn)
    def reset_scores(self):
        self.scores = dict.fromkeys(self.scores, 0)
