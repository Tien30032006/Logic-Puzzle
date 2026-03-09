import heapq
import time
import tracemalloc
import json
import os
import customtkinter as ctk

BOARD_SIZE = 8
CELL_SIZE = 60


# ===============================
# LOAD TEST CASES
# ===============================

def load_test_cases():

    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "input", "chess_puzzles_in.txt")
    except:
        path = os.path.join("input", "chess_puzzles_in.txt")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


TEST_CASES = load_test_cases()


# ===============================
# BOARD UTILS
# ===============================

def parse_fen(fen):

    board = []

    for row in fen.split("/"):
        r = []
        for c in row:

            if c.isdigit():
                r += [None]*int(c)
            else:
                r.append(c)

        board.append(r)

    return board


def board_to_string(board):
    return str(board)


def find_pieces(board):

    pieces=[]

    for i in range(8):
        for j in range(8):

            if board[i][j] is not None:
                pieces.append((board[i][j],i,j))

    return pieces


def count_pieces(board):
    return sum(cell is not None for row in board for cell in row)


def is_valid(x,y):
    return 0<=x<8 and 0<=y<8


# ===============================
# MOVE GENERATION
# ===============================

def sliding_moves(x,y,board,directions):

    moves=[]

    for dx,dy in directions:

        nx,ny=x+dx,y+dy

        while is_valid(nx,ny):

            if board[nx][ny] is None:
                nx+=dx
                ny+=dy
                continue

            moves.append((nx,ny))
            break

    return moves


MOVES={

'P':lambda x,y,board:[
(x-1,y-1),(x-1,y+1)
],

'N':lambda x,y,board:[
(x+2,y+1),(x+2,y-1),
(x-2,y+1),(x-2,y-1),
(x+1,y+2),(x+1,y-2),
(x-1,y+2),(x-1,y-2)
],

'B':lambda x,y,board:
sliding_moves(x,y,board,
[(1,1),(1,-1),(-1,1),(-1,-1)]),

'R':lambda x,y,board:
sliding_moves(x,y,board,
[(1,0),(-1,0),(0,1),(0,-1)]),

'Q':lambda x,y,board:
sliding_moves(x,y,board,
[(1,1),(1,-1),(-1,1),(-1,-1),
(1,0),(-1,0),(0,1),(0,-1)]),

'K':lambda x,y,board:[
(x+1,y),(x-1,y),(x,y+1),(x,y-1),
(x+1,y+1),(x+1,y-1),
(x-1,y+1),(x-1,y-1)
]

}


# ===============================
# GENERATE CAPTURE MOVES
# ===============================

def generate_moves(board):

    moves=[]

    for piece,x,y in find_pieces(board):

        if piece not in MOVES:
            continue

        for tx,ty in MOVES[piece](x,y,board):

            if not is_valid(tx,ty):
                continue

            if board[tx][ty] is None:
                continue

            new_board=[row[:] for row in board]

            new_board[tx][ty]=piece
            new_board[x][y]=None

            moves.append(new_board)

    return moves


# ===============================
# GOAL
# ===============================

def is_goal(board):
    return count_pieces(board)==1


# ===============================
# HEURISTIC
# ===============================
def heuristic(board):

    pieces = count_pieces(board)

    captures = 0

    for piece,x,y in find_pieces(board):

        if piece in MOVES:
            for tx,ty in MOVES[piece](x,y,board):

                if is_valid(tx,ty) and board[tx][ty] is not None:
                    captures += 1

    return pieces + captures

# ===============================
# DFS
# ===============================

def dfs(board,path,visited):

    key=board_to_string(board)

    if key in visited:
        return False,[]

    visited.add(key)

    if is_goal(board):
        return True,path

    moves=generate_moves(board)

    moves.sort(key=lambda b:count_pieces(b))

    for new_board in moves:

        solved,sol=dfs(
            new_board,
            path+[new_board],
            visited
        )

        if solved:
            return True,sol

    return False,[]


# ===============================
# BFS
# ===============================

def bfs(start):

    from collections import deque

    queue=deque([(start,[start])])

    visited=set()

    while queue:

        board,path=queue.popleft()

        key=board_to_string(board)

        if key in visited:
            continue

        visited.add(key)

        if is_goal(board):
            return True,path

        for new_board in generate_moves(board):

            queue.append(
                (new_board,path+[new_board])
            )

    return False,[]


# ===============================
# A*
# ===============================

def astar(start):

    pq=[]
    counter=0

    heapq.heappush(
        pq,
        (heuristic(start),0,counter,start,[start])
    )

    visited=set()

    while pq:

        f,g,_,board,path=heapq.heappop(pq)

        key=board_to_string(board)

        if key in visited:
            continue

        visited.add(key)

        if is_goal(board):
            return True,path

        for new_board in generate_moves(board):

            g2=g+1
            h2=heuristic(new_board)

            counter+=1

            heapq.heappush(
                pq,
                (g2+h2,g2,counter,new_board,path+[new_board])
            )

    return False,[]


# ===============================
# UI
# ===============================

class ChessUI(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Chess Puzzle Solver")
        self.geometry("850x550")

        self.create_widgets()


    def create_widgets(self):

        sidebar=ctk.CTkFrame(self)
        sidebar.pack(side="left",fill="y",padx=10,pady=10)

        ctk.CTkLabel(sidebar,text="Level").pack(pady=5)

        self.combo_level=ctk.CTkComboBox(
            sidebar,
            values=list(TEST_CASES.keys())
        )
        self.combo_level.pack(pady=5)


        ctk.CTkLabel(sidebar,text="Algorithm").pack(pady=5)

        self.combo_algo=ctk.CTkComboBox(
            sidebar,
            values=["DFS","BFS","A*"]
        )
        self.combo_algo.pack(pady=5)


        solve_btn=ctk.CTkButton(
            sidebar,
            text="Solve",
            command=self.solve
        )
        solve_btn.pack(pady=20)


        next_btn=ctk.CTkButton(
            sidebar,
            text="Next Step",
            command=self.next_step
        )
        next_btn.pack(pady=10)


        auto_btn=ctk.CTkButton(
            sidebar,
            text="Auto Play",
            command=self.auto_play
        )
        auto_btn.pack(pady=10)


        self.info=ctk.CTkLabel(sidebar,text="")
        self.info.pack(pady=10)


        self.canvas=ctk.CTkCanvas(
            self,
            width=CELL_SIZE*8,
            height=CELL_SIZE*8
        )
        self.canvas.pack(pady=20)


        self.steps=[]
        self.step_index=0


    # ===============================

    def draw_board(self,board):

        self.canvas.delete("all")

        for i in range(8):
            for j in range(8):

                color="#EEEED2" if (i+j)%2==0 else "#769656"

                x1=j*CELL_SIZE
                y1=i*CELL_SIZE
                x2=x1+CELL_SIZE
                y2=y1+CELL_SIZE

                self.canvas.create_rectangle(
                    x1,y1,x2,y2,fill=color
                )

                piece=board[i][j]

                if piece:

                    self.canvas.create_text(
                        x1+CELL_SIZE/2,
                        y1+CELL_SIZE/2,
                        text=piece,
                        font=("Arial",24,"bold")
                    )


    # ===============================

    def solve(self):

        level=self.combo_level.get()

        fen=TEST_CASES[level]["fen"]

        board=parse_fen(fen)

        algo=self.combo_algo.get()

        self.draw_board(board)

        tracemalloc.start()
        start=time.perf_counter()

        if algo=="DFS":
            solved,self.steps=dfs(board,[board],set())

        elif algo=="BFS":
            solved,self.steps=bfs(board)

        else:
            solved,self.steps=astar(board)

        end=time.perf_counter()

        _,peak=tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.step_index=0

        self.info.configure(
            text=f"Steps: {len(self.steps)} | Time: {end-start:.4f}s | RAM: {peak/1024/1024:.2f} MB"
        )


    # ===============================

    def next_step(self):

        if not self.steps:
            return

        if self.step_index>=len(self.steps):
            return

        board=self.steps[self.step_index]

        self.draw_board(board)

        self.step_index+=1


    # ===============================

    def auto_play(self):

        if self.step_index>=len(self.steps):
            return

        self.next_step()

        self.after(300,self.auto_play)


# ===============================

if __name__=="__main__":

    app=ChessUI()
    app.mainloop()