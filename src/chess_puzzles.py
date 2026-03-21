import heapq
import time
import tracemalloc
import json
import os
import re
import customtkinter as ctk

BOARD_SIZE = 8
CELL_SIZE = 60
MARGIN = 30

UNICODE_PIECES = {
    'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}

def load_test_cases():
    all_tests = {}
    
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_path = os.path.join(base, "input", "chess_test")
    except:
        base_path = os.path.join("input", "chess_test")
        
    if not os.path.exists(base_path):
        base_path = os.path.join(os.getcwd(), "input", "chess_test")

    if not os.path.exists(base_path):
        return {"Default": {"fen": "8/8/8/8/8/8/8/8"}}

    for filename in os.listdir(base_path):
        if filename.endswith(".txt") or filename.endswith(".json"):
            path = os.path.join(base_path, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_tests.update(data)
            except:
                pass
                
    if not all_tests:
        return {"Default": {"fen": "8/8/8/8/8/8/8/8"}}
        
    def sort_key(k):
        m = re.search(r'\d+', k)
        if m:
            return int(m.group())
        if "special" in k.lower():
            return 999
        return 1000

    return dict(sorted(all_tests.items(), key=lambda item: sort_key(item[0])))

TEST_CASES = load_test_cases()


def parse_fen(fen):
    board = []
    for row in fen.split(" ")[0].split("/"):
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
    'P':lambda x,y,board: [(x-1,y-1),(x-1,y+1)],
    'N':lambda x,y,board: [(x+2,y+1),(x+2,y-1),(x-2,y+1),(x-2,y-1),(x+1,y+2),(x+1,y-2),(x-1,y+2),(x-1,y-2)],
    'B':lambda x,y,board: sliding_moves(x,y,board,[(1,1),(1,-1),(-1,1),(-1,-1)]),
    'R':lambda x,y,board: sliding_moves(x,y,board,[(1,0),(-1,0),(0,1),(0,-1)]),
    'Q':lambda x,y,board: sliding_moves(x,y,board,[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]),
    'K':lambda x,y,board: [(x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)]
}

def generate_moves(board):
    moves=[]
    for piece,x,y in find_pieces(board):
        piece_upper = piece.upper()
        if piece_upper not in MOVES: continue

        for tx,ty in MOVES[piece_upper](x,y,board):
            if not is_valid(tx,ty): continue
            if board[tx][ty] is None: continue

            new_board=[row[:] for row in board]
            new_board[tx][ty]=piece
            new_board[x][y]=None
            moves.append(new_board)
    return moves

def is_goal(board):
    return count_pieces(board)==1

def heuristic(board):
    pieces = count_pieces(board)
    total_capture = 0
    mobility = 0

    for piece,x,y in find_pieces(board):
        piece_upper = piece.upper()
        if piece_upper not in MOVES: continue

        moves = MOVES[piece_upper](x,y,board)
        mobility += len(moves)

        captures = 0
        for tx,ty in moves:
            if is_valid(tx,ty) and board[tx][ty] is not None:
                captures += 1
        total_capture += captures

    return pieces*3 - total_capture + mobility*0.05


def dfs(board,path,visited):
    key=board_to_string(board)
    if key in visited: return False,[]
    visited.add(key)
    if is_goal(board): return True,path

    moves=generate_moves(board)
    moves.sort(key=lambda b:count_pieces(b))

    for new_board in moves:
        solved,sol=dfs(new_board, path+[new_board], visited)
        if solved: return True,sol
    return False,[]

def bfs(start):
    from collections import deque
    queue=deque([(start,[start])])
    visited=set()
    while queue:
        board,path=queue.popleft()
        key=board_to_string(board)
        if key in visited: continue
        visited.add(key)
        if is_goal(board): return True,path

        for new_board in generate_moves(board):
            queue.append((new_board,path+[new_board]))
    return False,[]

def astar(start):
    pq=[]
    counter=0
    heapq.heappush(pq, (heuristic(start),0,counter,start,[start]))
    visited=set()
    while pq:
        f,g,_,board,path=heapq.heappop(pq)
        key=board_to_string(board)
        if key in visited: continue
        visited.add(key)
        if is_goal(board): return True,path

        for new_board in generate_moves(board):
            g2=g+1
            h2=heuristic(new_board)
            counter+=1
            heapq.heappush(pq, (g2+h2,g2,counter,new_board,path+[new_board]))
    return False,[]


def get_move_desc(b1, b2):
    cols = "abcdefgh"
    rows = "87654321"
    
    for piece, x, y in find_pieces(b1):
        piece_upper = piece.upper()
        if piece_upper not in MOVES: 
            continue

        for tx, ty in MOVES[piece_upper](x, y, b1):
            if not is_valid(tx, ty): 
                continue
            
            target = b1[tx][ty]
            if target is None: 
                continue 

            sim_board = [row[:] for row in b1]
            sim_board[tx][ty] = piece
            sim_board[x][y] = None

            if sim_board == b2:
                return f"{piece} ({cols[y]}{rows[x]}) -> {target} ({cols[ty]}{rows[tx]})"
                
    return "Không rõ bước đi"


class ChessUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chess Puzzle Solver")
        self.geometry("880x650") 
        self.create_widgets()

    def create_widgets(self):
        sidebar=ctk.CTkFrame(self)
        sidebar.pack(side="left",fill="y",padx=10,pady=10)

        ctk.CTkLabel(sidebar,text="Level", font=("Arial", 14, "bold")).pack(pady=5)
        
        test_names = list(TEST_CASES.keys())
        self.combo_level=ctk.CTkComboBox(sidebar, values=test_names)
        self.combo_level.pack(pady=5)

        ctk.CTkLabel(sidebar,text="Algorithm", font=("Arial", 14, "bold")).pack(pady=5)
        self.combo_algo=ctk.CTkComboBox(sidebar, values=["DFS","BFS","A*"])
        self.combo_algo.pack(pady=5)

        solve_btn=ctk.CTkButton(sidebar, text="Solve", command=self.solve, fg_color="#2c3e50")
        solve_btn.pack(pady=15)

        next_btn=ctk.CTkButton(sidebar, text="Next Step", command=self.next_step)
        next_btn.pack(pady=5)

        auto_btn=ctk.CTkButton(sidebar, text="Auto Play", command=self.auto_play)
        auto_btn.pack(pady=5)

        self.info=ctk.CTkLabel(sidebar,text="Trạng thái: Sẵn sàng")
        self.info.pack(pady=10)

        ctk.CTkLabel(sidebar,text="Lịch sử các bước:", font=("Arial", 12, "bold")).pack(pady=(10,0))
        self.move_log = ctk.CTkTextbox(sidebar, height=180, width=200)
        self.move_log.pack(pady=5)

        self.canvas=ctk.CTkCanvas(
            self,
            width=CELL_SIZE*8 + MARGIN,
            height=CELL_SIZE*8 + MARGIN,
            highlightthickness=0
        )
        self.canvas.pack(pady=20)

        self.steps=[]
        self.step_index=0


    def draw_board(self,board):
        self.canvas.delete("all")
        
        cols = "abcdefgh"
        rows = "87654321"

        for i in range(8):
            self.canvas.create_text(
                MARGIN / 2, 
                i * CELL_SIZE + CELL_SIZE / 2, 
                text=rows[i], 
                font=("Arial", 14, "bold"), 
                fill="#333333"
            )
            
            self.canvas.create_text(
                MARGIN + i * CELL_SIZE + CELL_SIZE / 2, 
                8 * CELL_SIZE + MARGIN / 2, 
                text=cols[i], 
                font=("Arial", 14, "bold"), 
                fill="#333333"
            )

        for i in range(8):
            for j in range(8):
                color="#EEEED2" if (i+j)%2==0 else "#769656"

                x1 = MARGIN + j*CELL_SIZE
                y1 = i*CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                self.canvas.create_rectangle(x1,y1,x2,y2,fill=color, outline=color)

                piece=board[i][j]
                if piece:
                    char = UNICODE_PIECES.get(piece, piece)
                    self.canvas.create_text(x1+CELL_SIZE/2, y1+CELL_SIZE/2, text=char, fill="#000000", font=("Arial", 38))


    def solve(self):
        level=self.combo_level.get()
        if level not in TEST_CASES: return

        fen=TEST_CASES[level]["fen"]
        board=parse_fen(fen)
        algo=self.combo_algo.get()

        self.draw_board(board)
        self.move_log.delete("0.0", "end")
        self.move_log.insert("end", "Đang giải...\n")
        self.update()

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

        if solved:
            self.info.configure(
                text=f"Steps: {len(self.steps)-1} | Time: {end-start:.4f}s\nRAM: {peak/1024/1024:.2f} MB"
            )
            
            print(f"\n--- TEST: {level} ({algo}) ---")
            self.move_log.delete("0.0", "end")
            self.move_log.insert("end", "Các bước giải:\n")
            for i in range(len(self.steps)-1):
                desc = get_move_desc(self.steps[i], self.steps[i+1])
                log_text = f"{i+1}. {desc}\n"
                self.move_log.insert("end", log_text)
                print(f"Bước {i+1}: {desc}")
        else:
            self.info.configure(text="Không tìm thấy lời giải!")
            self.move_log.delete("0.0", "end")
            self.move_log.insert("end", "Thất bại.")


    def next_step(self):
        if not self.steps: return
        if self.step_index>=len(self.steps): return

        board=self.steps[self.step_index]
        self.draw_board(board)
        self.step_index+=1


    def auto_play(self):
        if self.step_index>=len(self.steps): return
        self.next_step()
        self.after(500, self.auto_play) 


if __name__=="__main__":
    app=ChessUI()
    app.mainloop()