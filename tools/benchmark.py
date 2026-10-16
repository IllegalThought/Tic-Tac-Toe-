"""Reproducible cold-cache comparison; run from project root."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ai.search import MODES, choose_move
from game.board import EMPTY, play

def benchmark():
    rows=[]
    for name,board in [('Empty board',EMPTY),('Human center',play(EMPTY,4,'X')),('Midgame',('X','O','','','X','','O','',''))]:
        for mode in MODES[:3]:
            r=choose_move(board,mode,'O'); s=r.stats
            rows.append((name,mode,s.nodes,s.terminals,s.cutoffs,s.skipped,s.cache_hits,s.unique_states,f'{s.elapsed_ms:.3f}',r.score))
    header=('Position','Algorithm','Nodes','Terminal evaluations','Cutoffs','Skipped children','Cache hits','Stored keys','Milliseconds','Value')
    md='| '+' | '.join(header)+' |\n| '+' | '.join(['---']*len(header))+' |\n'
    md+='\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)
    return md
if __name__=='__main__': print(benchmark())
