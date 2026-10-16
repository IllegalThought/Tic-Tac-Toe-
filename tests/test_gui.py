"""Real Tk lifecycle tests; skip when dependencies or display are absent."""
import unittest
import time
try:
    import tkinter as tk
    import customtkinter
    GUI_DEPENDENCY = True
except ImportError:
    GUI_DEPENDENCY = False
from game.board import EMPTY
from ai.search import MODES

@unittest.skipUnless(GUI_DEPENDENCY,'CustomTkinter is not installed')
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            root=tk.Tk(); root.destroy()
        except tk.TclError as exc: raise unittest.SkipTest(f'No desktop display: {exc}')
    def setUp(self):
        from gui.app import App
        self.app=App(); self.app.update()
    def tearDown(self):
        self.app.close()
    def wait_until(self,predicate,timeout=15):
        end=time.monotonic()+timeout
        while not predicate():
            self.app.update()
            if time.monotonic()>end: self.fail('GUI worker did not complete')
            time.sleep(0.01)
        self.app.update()
    def test_play_restart_scores_and_dashboard(self):
        app=self.app
        app.cells[4].invoke()
        self.assertTrue(app.busy)
        snapshot=app.game.board
        app.human_move(0); self.assertEqual(app.game.board,snapshot)
        self.wait_until(lambda:not app.busy)
        self.assertEqual(app.game.board.count('O'),1)
        self.assertIsNotNone(app.latest)
        self.assertNotEqual(app.metrics['nodes'].cget('text'),'—')
        app.show_tree(); app.show_info()
        app.compare()
        self.wait_until(lambda:app.compare_button.cget('state')=='normal')
        self.assertIn('Game value',app.comparison.get('1.0','end'))
        app.game.scores['O']=3; app.reset_scores(); self.assertEqual(app.game.scores['O'],0)
        app.restart(); self.assertEqual(app.game.board,EMPTY); self.assertIsNone(app.latest)
        self.assertEqual(app.mode.cget('state'),'normal')
    def test_terminal_input_and_modes(self):
        app=self.app
        app.game.board=('X','X','X','O','O','','','',''); app.game.finished=True; app.render()
        before=app.game.board; app.human_move(5); self.assertEqual(app.game.board,before)
        app.restart()
        for mode in MODES:
            app.mode.set(mode); app.settings_changed()
            self.assertEqual(app.depth_menu.cget('state'),'normal' if mode==MODES[3] else 'disabled')
        app.depth.set('2'); app.iterative.set(True); app.cells[0].invoke()
        self.wait_until(lambda:not app.busy)
        self.assertEqual(app.latest.mode,MODES[3]); self.assertEqual(app.latest.stats.achieved_depth,2)
    def test_stale_result_after_restart(self):
        app=self.app
        from ai.search import choose_move
        old=app.generation
        result=choose_move(('X','','','','','','','',''))
        app.restart()
        app.results.put((old,'ai',result,None)); app.poll()
        self.assertEqual(app.game.board,EMPTY)
        app.starter.set('AI starts (O)'); app.change_starter()
        self.wait_until(lambda:not app.busy)
        self.assertEqual(app.game.board.count('O'),1); self.assertEqual(app.game.turn,'X')
if __name__=='__main__': unittest.main()
