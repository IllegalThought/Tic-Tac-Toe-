import unittest
from functools import lru_cache
from game.board import EMPTY, legal_moves, play, winner, terminal, terminal_score, other, LINES
from game.game_manager import GameManager
from ai.search import Engine, choose_move, MODES
from ai.symmetry import orientations, canonical
from ai.heuristics import evaluate
@lru_cache(None)
def oracle(board,side):
    if terminal(board): return terminal_score(board)
    return (max if side=='O' else min)(oracle(play(board,i,side),other(side)) for i in legal_moves(board))
def positions(starter):
    seen=set()
    def visit(board,side):
        if (board,side) in seen: return
        seen.add((board,side))
        if not terminal(board):
            for i in legal_moves(board): visit(play(board,i,side),other(side))
    visit(EMPTY,starter)
    return seen
class RulesTests(unittest.TestCase):
    def test_empty_and_legal(self):
        self.assertEqual(len(EMPTY),9); self.assertEqual(legal_moves(EMPTY),list(range(9)))
        board=play(EMPTY,4,'X'); self.assertEqual(board[4],'X'); self.assertEqual(EMPTY[4],'')
        for i in (4,-1,9):
            with self.assertRaises(ValueError): play(board,i,'O')
    def test_all_win_lines(self):
        for line in LINES:
            for side in ('X','O'):
                board=tuple(side if i in line else '' for i in range(9))
                self.assertEqual(winner(board),side); self.assertTrue(terminal(board)); self.assertEqual(legal_moves(board),[])
    def test_draw_and_game_over(self):
        board=tuple('XOXXOOOXX'); self.assertIsNone(winner(board)); self.assertTrue(terminal(board))
        game=GameManager()
        for i in (0,3,1,4,2): game.move(i)
        self.assertTrue(game.finished); self.assertEqual(game.scores['X'],1)
        with self.assertRaises(ValueError): game.move(8)
        game.restart('O'); self.assertEqual(game.turn,'O'); self.assertEqual(game.board,EMPTY)
        game.reset_scores(); self.assertEqual(sum(game.scores.values()),0)
class SearchTests(unittest.TestCase):
    def test_win_block_and_terminal(self):
        for mode in MODES[:3]:
            self.assertEqual(choose_move(('O','O','','X','X','','X','',''),mode).move,2)
            self.assertEqual(choose_move(('X','X','','','O','','','',''),mode).move,2)
            result=choose_move(('X','X','X','O','O','','','',''),mode)
            self.assertIsNone(result.move); self.assertLess(result.score,0)
    def test_baseline_equivalence_samples(self):
        for board,side in [(EMPTY,'O'),(play(EMPTY,4,'X'),'O'),(('X','O','X','','O','','','',''),'X')]:
            for mode in MODES[:3]:
                result=choose_move(board,mode,side)
                self.assertIn(result.move,legal_moves(board)); self.assertEqual(result.score,oracle(board,side))
    def test_all_reachable_values_and_candidates(self):
        for board,side in positions('X') | positions('O'):
            if terminal(board): continue
            result=choose_move(board,MODES[2],side)
            self.assertEqual(result.score,oracle(board,side),(board,side))
            for i,score in result.alternatives.items():
                self.assertEqual(score,oracle(play(board,i,side),other(side)),(board,side,i))
    def test_full_modes_never_lose_any_human_sequence(self):
        for mode in MODES[:3]:
            for starter in ('X','O'):
                seen=set()
                def visit(board,side):
                    if (board,side) in seen: return
                    seen.add((board,side))
                    if terminal(board):
                        self.assertNotEqual(winner(board),'X',(mode,board)); return
                    moves=[choose_move(board,mode,side).move] if side=='O' else legal_moves(board)
                    for i in moves: visit(play(board,i,side),other(side))
                visit(EMPTY,starter)
    def test_symmetry_and_optimizations(self):
        board=('X','','','O','O','','X','','')
        self.assertEqual(len({canonical(b) for b in orientations(board)}),1)
        self.assertEqual(len(orientations(board)),8)
        for b in orientations(board):
            result=choose_move(b); self.assertEqual(result.score,oracle(b,'O')); self.assertIn(result.move,legal_moves(b))
        self.assertEqual(Engine(MODES[2],False).solve(board).score,oracle(board,'O'))
    def test_statistics_and_cold_caches(self):
        board=('X','O','X','X','O','O','O','X','')
        for mode in MODES[:3]:
            r=choose_move(board,mode,'X')
            self.assertEqual(r.stats.nodes,2); self.assertEqual(r.stats.terminals,1)
            self.assertEqual(r.stats.max_depth,1); self.assertEqual(r.stats.skipped,0)
        engine=Engine(MODES[2]); a=engine.solve(EMPTY); b=engine.solve(EMPTY)
        self.assertEqual(a.stats.nodes,b.stats.nodes); self.assertGreater(a.stats.cache_hits,0)
        self.assertLess(a.stats.nodes,choose_move(EMPTY,MODES[0]).stats.nodes)
        self.assertTrue(all(e[1] in ('EXACT','UPPER','LOWER') for e in engine.table.values()))
    def test_depth_limits_and_iterative(self):
        board=play(EMPTY,4,'X')
        for depth in (1,2,4):
            a=choose_move(board,MODES[3],depth_limit=depth); b=choose_move(board,MODES[3],depth_limit=depth,iterative=True)
            self.assertEqual(a.score,b.score); self.assertEqual(a.alternatives,b.alternatives)
            self.assertEqual(b.stats.achieved_depth,depth); self.assertLessEqual(a.stats.max_depth,depth)
            self.assertFalse(a.exact); self.assertIn(a.move,legal_moves(board))
        self.assertEqual(choose_move(board,MODES[3],depth_limit=9).score,oracle(board,'O'))
        for b,_ in positions('X'):
            if not terminal(b): self.assertLessEqual(abs(evaluate(b)),50)
if __name__=='__main__': unittest.main()
