"""Independent search engines with per-decision cold transposition tables."""
from dataclasses import dataclass, field
from time import perf_counter
from game.board import terminal, terminal_score, legal_moves, play, other
from ai.heuristics import ordered_moves, evaluate, threats
from ai.symmetry import canonical
MODES = ('Standard Minimax', 'Minimax + Alpha-Beta', 'Fully Optimized AI', 'Experimental Depth-Limited AI')
@dataclass
class Statistics:
    nodes: int = 0
    terminals: int = 0
    heuristic_leaves: int = 0
    cutoffs: int = 0
    skipped: int = 0
    max_depth: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    unique_states: int = 0
    elapsed_ms: float = 0
    achieved_depth: int = 0
@dataclass
class Result:
    move: int | None
    score: int
    alternatives: dict
    stats: Statistics
    mode: str
    board: tuple
    side: str
    exact: bool
    trace: list = field(default_factory=list)
    def explanation(self):
        if self.move is None: return 'Terminal position: no legal move remains.'
        r,c = divmod(self.move,3)
        action = 'Wins immediately.' if self.move in threats(self.board,self.side) else 'Blocks an immediate opponent threat.' if self.move in threats(self.board,other(self.side)) else 'Selected the best searched value.'
        outcome = ('O can force a win' if self.score > 0 else 'X can force a win' if self.score < 0 else 'a draw under optimal play') if self.exact else 'a depth-limited estimate; perfect play is not guaranteed'
        return f'Row {r+1}, column {c+1}. {action} Score {self.score:+d}: {outcome}.'
class Engine:
    def __init__(self, mode, use_symmetry=True):
        if mode not in MODES: raise ValueError('Unknown search mode')
        self.mode = mode
        self.pruning = mode != MODES[0]
        self.optimized = mode == MODES[2]
        self.use_symmetry = use_symmetry
        self.stats, self.table, self.trace = Statistics(), {}, []
    def visit(self, board, side, remaining, alpha, beta, depth, path):
        s = self.stats
        s.nodes += 1
        s.max_depth = max(s.max_depth, depth)
        event = None
        if depth <= 2 and len(self.trace) < 100:
            event = {'path':path, 'side':side, 'score':None, 'kind':'searched'}
            self.trace.append(event)
        def done(value, kind='searched'):
            if event is not None: event.update(score=value,kind=kind)
            return value
        if terminal(board):
            s.terminals += 1
            return done(terminal_score(board), 'terminal')
        if remaining == 0:
            s.heuristic_leaves += 1
            return done(evaluate(board), 'heuristic')
        a0,b0 = alpha,beta
        key = (canonical(board) if self.use_symmetry else board, side, remaining)
        if self.optimized:
            entry = self.table.get(key)
            if entry is not None:
                s.cache_hits += 1
                value,flag = entry
                if flag == 'EXACT': return done(value,'cache exact')
                if flag == 'LOWER': alpha = max(alpha,value)
                if flag == 'UPPER': beta = min(beta,value)
                if alpha >= beta: return done(value,'cache bound')
            else: s.cache_misses += 1
        moves = ordered_moves(board,side) if self.optimized else legal_moves(board)
        best = -1000 if side == 'O' else 1000
        for n,move in enumerate(moves):
            value = self.visit(play(board,move,side),other(side),remaining-1,alpha,beta,depth+1,path+(move,))
            best = max(best,value) if side == 'O' else min(best,value)
            if self.pruning:
                if side == 'O': alpha = max(alpha,best)
                else: beta = min(beta,best)
                if alpha >= beta:
                    s.cutoffs += 1
                    s.skipped += len(moves)-n-1
                    if event is not None: event['cutoff'] = True
                    break
        if self.optimized:
            flag = 'UPPER' if best <= a0 else 'LOWER' if best >= b0 else 'EXACT'
            self.table[key] = (best,flag)
        return done(best)
    def solve(self, board, side='O', depth_limit=3, iterative=False):
        board = tuple(board)
        if len(board) != 9 or any(c not in ('','X','O') for c in board) or side not in ('X','O'):
            raise ValueError('Invalid board or side')
        self.stats, self.table, self.trace = Statistics(), {}, []
        start = perf_counter()
        full = board.count('')
        experimental = self.mode == MODES[3]
        target = min(full,max(1,int(depth_limit))) if experimental else full
        depths = range(1,target+1) if experimental and iterative else [target]
        alternatives, chosen, best = {},None,terminal_score(board)
        if terminal(board):
            self.visit(board,side,0,-1000,1000,0,())
        else:
            for limit in depths:
                self.stats.nodes += 1 # the root for each iteration
                self.trace = []
                alternatives = {}
                moves = ordered_moves(board,side) if self.optimized else legal_moves(board)
                # Full window per root candidate: each displayed alternative is exact
                # for this horizon. Table can still share reusable subtrees.
                for move in moves:
                    alternatives[move] = self.visit(play(board,move,side),other(side),limit-1,-1000,1000,1,(move,))
                best = (max if side == 'O' else min)(alternatives.values())
                chosen = next(i for i in moves if alternatives[i] == best)
                self.stats.achieved_depth = limit
        self.stats.unique_states = len(self.table)
        self.stats.elapsed_ms = (perf_counter()-start)*1000
        return Result(chosen,best,alternatives,self.stats,self.mode,board,side,not experimental or target == full,list(self.trace))
def choose_move(board, mode=MODES[2], side='O', depth_limit=3, iterative=False):
    return Engine(mode).solve(board,side,depth_limit,iterative)
