"""All Tk calls stay on the main thread; workers communicate through a queue."""
import queue
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from ai.search import choose_move, MODES
from game.board import winner, winning_line, terminal
from game.game_manager import GameManager
BG, PANEL, CARD = '#0F172A', '#1E293B', '#263449'
TEXT, MUTED, CYAN, CORAL, GREEN = '#F8FAFC','#94A3B8','#38BDF8','#FB7185','#22C55E'
METRICS = [('nodes','Nodes visited'),('terminals','Terminal evaluations'),('cutoffs','Pruning cutoffs'),('skipped','Child branches skipped'),('max_depth','Maximum depth'),('elapsed_ms','Decision time (ms)'),('cache_hits','Cache hits'),('unique_states','Unique states stored')]
class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode('dark')
        super().__init__()
        self.title('Tic Tac Toe AI • Adversarial Search Lab')
        self.geometry('1180x860')
        self.minsize(1000,820)
        self.configure(fg_color=BG)
        self.game = GameManager()
        self.results = queue.Queue()
        self.generation = 0
        self.busy = False
        self.latest = None
        self.closed = False
        self.protocol('WM_DELETE_WINDOW',self.close)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)
        head = ctk.CTkFrame(self,fg_color=BG)
        head.grid(row=0,column=0,sticky='ew',padx=28,pady=(20,12))
        self.label(head,'TIC TAC TOE AI',26,True).pack(anchor='w')
        self.label(head,'Intelligent Game Agent  /  Adversarial Search Lab',13,color=MUTED).pack(anchor='w',pady=(3,12))
        controls = ctk.CTkFrame(head,fg_color=BG)
        controls.pack(fill='x')
        self.mode = ctk.CTkOptionMenu(controls,values=list(MODES),width=310,command=self.settings_changed,fg_color=CARD,button_color='#334155')
        self.mode.set(MODES[2]); self.mode.pack(side='left',padx=(0,12))
        self.starter = ctk.CTkOptionMenu(controls,values=['Human starts (X)','AI starts (O)'],width=170,command=self.change_starter,fg_color=CARD)
        self.starter.pack(side='left',padx=(0,16))
        self.depth = tk.StringVar(value='3')
        self.depth_menu = ctk.CTkOptionMenu(controls,values=[str(i) for i in range(1,10)],variable=self.depth,width=60)
        self.depth_menu.pack(side='right')
        self.label(controls,'Depth',12,color=MUTED).pack(side='right',padx=8)
        self.iterative = tk.BooleanVar(value=False)
        self.iterative_check = ctk.CTkCheckBox(controls,text='Iterative deepening',variable=self.iterative,width=170)
        self.iterative_check.pack(side='right',padx=14)
        body = ctk.CTkFrame(self,fg_color=BG)
        body.grid(row=1,column=0,sticky='nsew',padx=28,pady=(0,20))
        body.grid_columnconfigure(0,weight=4)
        body.grid_columnconfigure(1,weight=5)
        body.grid_rowconfigure(0,weight=1)
        left = ctk.CTkFrame(body,fg_color=PANEL,corner_radius=18)
        left.grid(row=0,column=0,sticky='nsew',padx=(0,18))
        self.label(left,'01  /  PLAY',13,True,color=MUTED).pack(anchor='w',padx=24,pady=(20,12))
        score_row = ctk.CTkFrame(left,fg_color=PANEL)
        score_row.pack(fill='x',padx=20)
        self.score_labels = {}
        for key,title,color in [('X','YOU  /  X',CYAN),('Draw','DRAWS',MUTED),('O','AGENT  /  O',CORAL)]:
            card=ctk.CTkFrame(score_row,fg_color=CARD,corner_radius=12)
            card.pack(side='left',expand=True,fill='x',padx=4)
            self.label(card,title,11,True,color=color).pack(pady=(12,4))
            self.score_labels[key] = self.label(card,'0',25,True)
            self.score_labels[key].pack(pady=(0,12))
        self.status = self.label(left,'Your move',19,True)
        self.status.pack(pady=(18,4))
        self.mode_note = self.label(left,'Perfect play • Full search',12,color=MUTED)
        self.mode_note.pack(pady=(0,14))
        board_frame = ctk.CTkFrame(left,fg_color=PANEL)
        board_frame.pack(padx=24,pady=4)
        self.cells=[]
        for i in range(9):
            button=ctk.CTkButton(board_frame,text='',width=100,height=100,corner_radius=14,fg_color=CARD,hover_color='#334155',font=('Arial',50,'bold'),command=lambda i=i:self.human_move(i))
            button.grid(row=i//3,column=i%3,padx=4,pady=4)
            self.cells.append(button)
        buttons=ctk.CTkFrame(left,fg_color=PANEL)
        buttons.pack(fill='x',padx=24,pady=(22,8))
        ctk.CTkButton(buttons,text='New game',height=40,fg_color='#0284C7',command=self.restart).pack(side='left',fill='x',expand=True,padx=(0,8))
        ctk.CTkButton(buttons,text='Reset scores',height=40,fg_color=CARD,command=self.reset_scores).pack(side='left',fill='x',expand=True)
        footer=self.label(left,'X goes first by default. Select a starter above.\nSwitch algorithms between turns. Scores last for this session.',12,color=MUTED)
        footer.configure(wraplength=380)
        footer.pack(padx=20,pady=8)
        right=ctk.CTkScrollableFrame(body,fg_color=PANEL,corner_radius=18)
        right.grid(row=0,column=1,sticky='nsew')
        self.label(right,'02  /  SEARCH ANALYSIS',13,True,color=MUTED).pack(anchor='w',padx=14,pady=(14,10))
        metrics=ctk.CTkFrame(right,fg_color=PANEL)
        metrics.pack(fill='x',padx=10)
        metrics.grid_columnconfigure((0,1),weight=1)
        self.metrics={}
        for i,(key,title) in enumerate(METRICS):
            card=ctk.CTkFrame(metrics,fg_color=CARD,corner_radius=10)
            card.grid(row=i//2,column=i%2,sticky='ew',padx=4,pady=4)
            self.label(card,title,11,color=MUTED).pack(anchor='w',padx=14,pady=(10,0))
            self.metrics[key]=self.label(card,'—',21,True)
            self.metrics[key].pack(anchor='w',padx=14,pady=(0,8))
        self.label(right,'Why did the AI choose this move?',16,True).pack(anchor='w',padx=14,pady=(16,8))
        self.explanation=ctk.CTkTextbox(right,height=125,fg_color=CARD,font=('Arial',12),wrap='word')
        self.explanation.pack(fill='x',padx=14)
        self.set_text(self.explanation,'Play a move to inspect the agent’s decision. Full search assumes optimal opposition. Experimental search can make mistakes.')
        actions=ctk.CTkFrame(right,fg_color=PANEL)
        actions.pack(fill='x',padx=14,pady=12)
        self.compare_button=ctk.CTkButton(actions,text='Compare algorithms',command=self.compare,width=170,fg_color='#0284C7')
        self.compare_button.pack(side='left',padx=(0,8))
        ctk.CTkButton(actions,text='View search tree',command=self.show_tree,width=150,fg_color=CARD).pack(side='left')
        self.comparison=ctk.CTkTextbox(right,height=145,fg_color=CARD,font=('Courier',11),wrap='none')
        self.comparison.pack(fill='x',padx=14)
        self.set_text(self.comparison,'Compare the latest AI decision position.\nBefore the first decision, use the current board.\nAll comparisons use independent cold caches.')
        self.chart=tk.Canvas(right,height=100,bg=PANEL,highlightthickness=0)
        self.chart.pack(fill='x',padx=14,pady=(8,0))
        ctk.CTkButton(right,text='Metric definitions & syllabus',fg_color=CARD,command=self.show_info).pack(anchor='w',padx=14,pady=(12,14))
        self.settings_changed()
        self.render()
        self.after(40,self.poll)
    @staticmethod
    def label(parent,text,size=13,bold=False,color=TEXT):
        return ctk.CTkLabel(parent,text=text,text_color=color,font=('Arial',size,'bold' if bold else 'normal'),justify='left')
    @staticmethod
    def set_text(widget,value):
        widget.configure(state='normal'); widget.delete('1.0','end'); widget.insert('1.0',value); widget.configure(state='disabled')
    def settings_changed(self,*args):
        experimental=self.mode.get()==MODES[3]
        self.depth_menu.configure(state='normal' if experimental else 'disabled')
        self.iterative_check.configure(state='normal' if experimental else 'disabled')
        self.mode_note.configure(text='Experimental • Heuristic estimates' if experimental else 'Perfect play • Full search')
    def change_starter(self,*args): self.restart()
    def render(self):
        line=winning_line(self.game.board) or ()
        for i,button in enumerate(self.cells):
            mark=self.game.board[i]
            button.configure(text=mark,text_color=CYAN if mark=='X' else CORAL,text_color_disabled=CYAN if mark=='X' else CORAL,fg_color='#14532D' if i in line else CARD,state='normal' if not self.busy and not self.game.finished and self.game.turn=='X' and not mark else 'disabled')
        for key,label in self.score_labels.items(): label.configure(text=str(self.game.scores[key]))
        if self.game.finished:
            win=winner(self.game.board)
            text='You win!' if win=='X' else 'Agent wins' if win=='O' else 'Draw • well played'
        else: text='Agent is thinking…' if self.busy else 'Your move  /  X' if self.game.turn=='X' else 'Agent to move  /  O'
        self.status.configure(text=text)
    def human_move(self,index):
        if self.busy or self.game.finished or self.game.turn!='X': return
        try: self.game.move(index)
        except ValueError: return
        self.render()
        if not self.game.finished: self.start_ai()
    def restart(self):
        self.generation+=1
        self.busy=False
        self.mode.configure(state='normal')
        self.latest=None
        self.game.restart('O' if self.starter.get().startswith('AI') else 'X')
        for label in self.metrics.values(): label.configure(text='—')
        self.set_text(self.explanation,'New game. Waiting for the next AI decision.')
        self.set_text(self.comparison,'No comparison for this game yet.')
        self.chart.delete('all')
        self.compare_button.configure(state='normal')
        self.render()
        if self.game.turn=='O': self.start_ai()
    def reset_scores(self): self.game.reset_scores(); self.render()
    def launch(self,kind,func):
        generation=self.generation
        def worker():
            try: self.results.put((generation,kind,func(),None))
            except Exception as exc: self.results.put((generation,kind,None,str(exc)))
        threading.Thread(target=worker,daemon=True).start()
    def start_ai(self):
        board,mode,depth,iterative=self.game.board,self.mode.get(),int(self.depth.get()),self.iterative.get()
        self.busy=True
        self.mode.configure(state='disabled')
        self.compare_button.configure(state='disabled')
        self.render()
        self.launch('ai',lambda:choose_move(board,mode,'O',depth,iterative))
    def poll(self):
        if self.closed: return
        try:
            while True:
                generation,kind,result,error=self.results.get_nowait()
                if generation!=self.generation: continue
                if kind=='ai':
                    self.busy=False; self.mode.configure(state='normal'); self.compare_button.configure(state='normal')
                else: self.compare_button.configure(state='disabled' if self.busy else 'normal')
                if error:
                    messagebox.showerror('Search error',error); self.render(); continue
                if kind=='ai':
                    self.latest=result
                    if result.move is not None: self.game.move(result.move)
                    self.show_decision(result); self.render()
                else: self.show_comparison(result)
        except queue.Empty: pass
        self.after(40,self.poll)
    def show_decision(self,result):
        for key,label in self.metrics.items():
            na=(key in ('cache_hits','unique_states') and result.mode!=MODES[2]) or (key in ('cutoffs','skipped') and result.mode==MODES[0])
            value=getattr(result.stats,key)
            label.configure(text='N/A' if na else f'{value:.2f}' if key=='elapsed_ms' else str(value))
        choices=', '.join(f'{i//3+1},{i%3+1}: {score:+d}' for i,score in sorted(result.alternatives.items()))
        self.set_text(self.explanation,result.explanation()+f'\n\nCandidate scores (row,column): {choices}\nCompleted horizon: {result.stats.achieved_depth}; heuristic leaves: {result.stats.heuristic_leaves}.')
    def compare(self):
        if self.busy: return
        board=self.latest.board if self.latest else self.game.board
        side=self.latest.side if self.latest else self.game.turn
        self.compare_button.configure(state='disabled')
        self.set_text(self.comparison,'Computing three searches on the same snapshot…')
        self.launch('comparison',lambda:[choose_move(board,mode,side) for mode in MODES[:3]])
    def show_comparison(self,results):
        lines=['Metric          Minimax   Alpha-beta  Optimized']
        for key,title in [('nodes','Nodes'),('elapsed_ms','Time (ms)'),('cutoffs','Cutoffs'),('cache_hits','Cache hits')]:
            values=['N/A' if key=='cutoffs' and r.mode==MODES[0] or key=='cache_hits' and r.mode!=MODES[2] else f'{getattr(r.stats,key):.2f}' if key=='elapsed_ms' else str(getattr(r.stats,key)) for r in results]
            lines.append(f'{title:<15} {values[0]:>8} {values[1]:>11} {values[2]:>10}')
        lines.append(f"{'Game value':<15} {results[0].score:>8} {results[1].score:>11} {results[2].score:>10}")
        base=results[0].stats.nodes
        lines.append(f'Optimized node reduction: {100*(1-results[2].stats.nodes/base):.1f}%')
        lines.append('Cold caches. Timings vary with system load.')
        self.set_text(self.comparison,'\n'.join(lines))
        self.chart.delete('all')
        width=max(330,self.chart.winfo_width())
        for i,(result,color) in enumerate(zip(results,[MUTED,CYAN,CORAL])):
            y=8+i*30
            self.chart.create_text(4,y+9,text=['Minimax','Alpha-beta','Optimized'][i],anchor='w',fill=TEXT,font=('Arial',10))
            size=max(2,(width-200)*result.stats.nodes/base)
            self.chart.create_rectangle(95,y,95+size,y+18,fill=color,outline='')
            self.chart.create_text(width-6,y+9,text=str(result.stats.nodes),anchor='e',fill=TEXT,font=('Arial',10))
    def popup_text(self,title,text):
        window=ctk.CTkToplevel(self); window.title(title); window.geometry('790x570')
        box=ctk.CTkTextbox(window,font=('Courier',13),wrap='word')
        box.pack(fill='both',expand=True,padx=18,pady=18); self.set_text(box,text)
    def show_tree(self):
        if not self.latest:
            messagebox.showinfo('Search tree','Play a move first.'); return
        result=self.latest
        lines=[f'{result.mode} • last completed iteration',f'ROOT {"MAX" if result.side=="O" else "MIN"} ({result.side}), value {result.score:+d}', 'Recorded levels 1–2 only, maximum 100 records.', 'Cutoff = alpha ≥ beta; cache bound = transposition cutoff.', 'Scores on internal nodes can be bounds after cutoffs.\n']
        for event in result.trace:
            path=event['path']; coords=' → '.join(f'({i//3+1},{i%3+1})' for i in path)
            lines.append('    '*len(path)+f'{coords} | {"MAX" if event["side"]=="O" else "MIN"} | {event["score"]:+d} | {event["kind"]}'+(' | CUTOFF' if event.get('cutoff') else ''))
        self.popup_text('Recorded search tree', '\n'.join(lines))
    def show_info(self):
        self.popup_text('Search metrics & syllabus', '''MEASUREMENT RULES
Nodes: root + each recursive call, including cache hits.
Terminals: calls that evaluate a completed win/loss/draw.
Heuristic leaves: nonterminal states evaluated at depth zero.
Cutoffs: loop exits caused by alpha >= beta (including zero remaining siblings).
Branches skipped: immediate unvisited siblings, never guessed descendants.
Max depth: deepest visited ply from this decision's root.
Cache hits: table lookups finding an entry; may tighten bounds without returning.
Unique states: table keys stored (board symmetry + side + remaining depth).
Time: search and candidate analysis only; excludes GUI/worker startup.
Iterative deepening metrics accumulate across all iterations; the tree shows the last.

COMPARISON
Every root candidate uses a full alpha-beta window so all alternative scores are exact at the selected horizon. This deliberately does more work than a best-move-only root search. The same policy applies to all modes. Tables are cold per decision. Optimized mode adds tactical ordering, bounds caching and symmetry. Equal optimal values matter; tied move coordinates can differ. Fewer nodes do not guarantee lower wall-clock time.

SYLLABUS
Unit I: rational game agent; fully observable, deterministic, sequential, discrete, two-player adversarial environment.
Unit II: state spaces, heuristic evaluation, depth limits and iterative deepening.
Unit III: Minimax, MAX/MIN, alpha-beta and optimal game decisions.
Caching and symmetry are extra implementation optimizations.
Depth-limited mode is experimental and may lose.
''')
    def close(self):
        self.closed=True
        self.generation+=1
        for timer in self.tk.call('after','info'):
            try: self.tk.call('after','cancel',timer)
            except tk.TclError: pass
        self.destroy()
