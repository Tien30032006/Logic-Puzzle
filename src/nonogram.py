import os
import json
import copy
import heapq
import time
import tracemalloc
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from collections import deque

# ==========================================
# CẤU HÌNH GIAO DIỆN 
# ==========================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==========================================
# 0. HÀM ĐỌC DỮ LIỆU TỪ FILE
# ==========================================
def load_test_cases():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "input", "nonogram_in.txt")
    except NameError:
        filepath = os.path.join("input", "nonogram_in.txt")

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ LỖI: Không đọc được file dữ liệu. Chi tiết: {e}")
        return {}

TEST_CASES = load_test_cases()

# ==========================================
# 1. HÀM SINH TỔ HỢP 
# ==========================================
def get_permutations(clues, length):
    if not clues: return [[-1] * length]
    perms = []
    c = clues[0]
    min_rest = sum(clues[1:]) + len(clues[1:])
    for i in range(length - c - min_rest + 1):
        prefix = [-1] * i + [1] * c
        if len(clues) == 1:
            perms.append(prefix + [-1] * (length - len(prefix)))
        else:
            for rest in get_permutations(clues[1:], length - len(prefix) - 1):
                perms.append(prefix + [-1] + rest)
    return perms

# ==========================================
# 2. HÀM ĐÁNH GIÁ HEURISTIC & PRUNING
# ==========================================
def is_valid_partial_board(board, col_perms, row_idx):
    rows, cols = len(board), len(board[0])
    for j in range(cols):
        assigned_cells = [(i, board[i][j]) for i in range(row_idx + 1)]
        match_found = False
        for p in col_perms[j]:
            match = True
            for idx, val in assigned_cells:
                if p[idx] != val:
                    match = False
                    break
            if match:
                match_found = True
                break
        if not match_found:
            return False
    return True

def calc_heuristic_h(board, col_perms):
    rows, cols = len(board), len(board[0])
    h_score = 0
    for j in range(cols):
        assigned_cells = [(i, board[i][j]) for i in range(rows) if board[i][j] != 0]
        valid_count = 0
        for p in col_perms[j]:
            match = True
            for idx, val in assigned_cells:
                if p[idx] != val:
                    match = False
                    break
            if match:
                valid_count += 1
        
        if valid_count == 0:
            return float('inf')
        
        h_score += valid_count
        
    return h_score

# ==========================================
# 3. CÁC THUẬT TOÁN (BLIND SEARCH VÀ HEURISTIC )
# ==========================================
def solve_nonogram_dfs(row_clues, col_clues):
    rows, cols = len(row_clues), len(col_clues)
    row_perms = [get_permutations(c, cols) for c in row_clues]
    col_perms = [get_permutations(c, rows) for c in col_clues]

    initial_board = [[0] * cols for _ in range(rows)]
    stack = [(0, initial_board)]

    game_history = [copy.deepcopy(initial_board)]
    action_history = ["Bắt đầu Blind Search (DFS)"]

    while stack:
        row_idx, current_board = stack.pop()

        if row_idx > 0:
            game_history.append(copy.deepcopy(current_board))
            action_history.append(f"DFS Duyệt: Đâm sâu xuống hàng {row_idx}")

        if row_idx == rows:
            game_history.append(copy.deepcopy(current_board))
            action_history.append("🎉 Đã điền xong bảng! TÌM THẤY GIẢI PHÁP BẰNG BLIND SEARCH (DFS).")
            return game_history, action_history

        for p in reversed(row_perms[row_idx]):
            new_board = copy.deepcopy(current_board)
            new_board[row_idx] = p
            
            if is_valid_partial_board(new_board, col_perms, row_idx):
                stack.append((row_idx + 1, new_board))

    action_history.append("❌ Không tìm thấy giải pháp bằng Blind Search (DFS).")
    return game_history, action_history

def solve_nonogram_brfs(row_clues, col_clues):
    rows, cols = len(row_clues), len(col_clues)
    row_perms = [get_permutations(c, cols) for c in row_clues]
    col_perms = [get_permutations(c, rows) for c in col_clues]

    initial_board = [[0] * cols for _ in range(rows)]

    queue = deque([(0, initial_board)])

    game_history = [copy.deepcopy(initial_board)]
    action_history = ["Bắt đầu Blind Search (BrFS)"]

    while queue:
        row_idx, current_board = queue.popleft()

        if row_idx > 0:
            game_history.append(copy.deepcopy(current_board))
            action_history.append(f"BrFS Duyệt: Loang rộng ở hàng {row_idx}")

        if row_idx == rows:
            game_history.append(copy.deepcopy(current_board))
            action_history.append("🎉 Đã điền xong bảng! TÌM THẤY GIẢI PHÁP BẰNG BLIND SEARCH (BrFS).")
            return game_history, action_history

        for p in row_perms[row_idx]:
            new_board = copy.deepcopy(current_board)
            new_board[row_idx] = p
            
            if is_valid_partial_board(new_board, col_perms, row_idx):
                queue.append((row_idx + 1, new_board))

    action_history.append("❌ Không tìm thấy giải pháp bằng Blind Search (BrFS).")
    return game_history, action_history

def solve_nonogram_heuristic(row_clues, col_clues):
    rows, cols = len(row_clues), len(col_clues)
    row_perms = [get_permutations(c, cols) for c in row_clues]
    col_perms = [get_permutations(c, rows) for c in col_clues]

    initial_board = [[0] * cols for _ in range(rows)]
    
    h_initial = calc_heuristic_h(initial_board, col_perms)

    counter = 0
    open_list = [(h_initial, counter, 0, initial_board)]

    game_history = [copy.deepcopy(initial_board)]
    action_history = [f"Bắt đầu Heuristic | h(n) = {int(h_initial)}"]

    while open_list:
        current_h, _, row_idx, current_board = heapq.heappop(open_list)

        if row_idx > 0:
            game_history.append(copy.deepcopy(current_board))
            action_history.append(f"Heuristic Duyệt: Điền hàng {row_idx} | h(n) = {int(current_h)}")

        if row_idx == rows:
            game_history.append(copy.deepcopy(current_board))
            action_history.append(f"🎉 Đã điền xong bảng! TÌM THẤY GIẢI PHÁP (h(n) = {int(current_h)})")
            return game_history, action_history

        for p in row_perms[row_idx]:
            new_board = copy.deepcopy(current_board)
            new_board[row_idx] = p
            
            h_new = calc_heuristic_h(new_board, col_perms)

            if h_new != float('inf'):
                counter += 1
                heapq.heappush(open_list, (h_new, counter, row_idx + 1, new_board))

    action_history.append("❌ Không tìm thấy giải pháp bằng Heuristic.")
    return game_history, action_history


# ==========================================
# 4. HÀM VẼ GIAO DIỆN CHUỖI
# ==========================================
def render_board_string(board, row_clues, col_clues, step, total_steps, action, algo_name=""):
    # Giữ nguyên toàn bộ text của action để không mất thông số h(n)
    output_str = f"--- BƯỚC {step}/{total_steps} ({algo_name}) ---\n"
    output_str += f"⚡ {action}\n\n"

    max_col_clues = max(len(c) for c in col_clues)
    max_row_clues = max(len(r) for r in row_clues)
    row_padding_spaces = max_row_clues * 3

    for i in range(max_col_clues):
        output_str += " " * row_padding_spaces + " | "
        for c in col_clues:
            idx = i - (max_col_clues - len(c))
            output_str += f"{c[idx]:>2} " if idx >= 0 else "   "
        output_str += "\n"

    output_str += "-" * row_padding_spaces + "-+-" + "-" * (len(col_clues) * 3) + "\n"
    symbols = {0: ' . ', 1: '██ ', -1: '   '}

    for i, row in enumerate(board):
        pad_len = max_row_clues - len(row_clues[i])
        clue_str = "   " * pad_len + "".join(f"{x:>2} " for x in row_clues[i])
        output_str += clue_str + " | " + "".join(symbols[cell] for cell in row) + "\n"

    return output_str

# ==========================================
# 5. GIAO DIỆN 
# ==========================================
class NonogramModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Solver: Nonogram Puzzle")
        self.geometry("1100x800")
        
        # Biến trạng thái
        self.CACHE = {}
        self.game_history = []
        self.action_history = []
        self.current_step = 0
        self.total_steps = 0
        self.current_row_clues = []
        self.current_col_clues = []
        self.is_auto_running = False
        self.current_algo = "Heuristic (GBFS)"
        self.auto_speed_ms = 150 
        
        self.testcase_keys = list(TEST_CASES.keys()) if TEST_CASES else []

        self.setup_ui()
        
        if self.testcase_keys:
            self.trigger_solve()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu test cases tại input/nonogram_in.txt")

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------
        # THANH ĐIỀU KHIỂN BÊN TRÁI
        # ----------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Nonogram", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- Chọn Level ---
        self.label_select = ctk.CTkLabel(self.sidebar_frame, text="1. Chọn Level:", font=ctk.CTkFont(weight="bold"), anchor="w")
        self.label_select.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        self.level_control_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.level_control_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.btn_prev_level = ctk.CTkButton(self.level_control_frame, text="◀", width=30, command=self.prev_level)
        self.btn_prev_level.pack(side="left", padx=(0, 5))

        self.combo_testcases = ctk.CTkComboBox(self.level_control_frame, values=self.testcase_keys, width=170)
        self.combo_testcases.pack(side="left", fill="x", expand=True)
        self.combo_testcases.set(self.testcase_keys[0] if self.testcase_keys else "")
        
        self.btn_next_level = ctk.CTkButton(self.level_control_frame, text="▶", width=30, command=self.next_level)
        self.btn_next_level.pack(side="right", padx=(5, 0))

        # --- Chọn Thuật toán ---
        self.label_algo = ctk.CTkLabel(self.sidebar_frame, text="2. Chọn thuật toán:", font=ctk.CTkFont(weight="bold"), anchor="w")
        self.label_algo.grid(row=4, column=0, padx=20, pady=(15, 0), sticky="w")
        
        self.combo_algo = ctk.CTkComboBox(self.sidebar_frame, values=["Heuristic (GBFS)", "Blind Search (DFS)", "Blind Search (BrFS)"], width=250)
        self.combo_algo.grid(row=5, column=0, padx=20, pady=5)

        # Nút Giải
        self.btn_solve = ctk.CTkButton(self.sidebar_frame, text="Bắt đầu Giải", command=self.trigger_solve, fg_color="#1f538d")
        self.btn_solve.grid(row=6, column=0, padx=20, pady=(20, 10))

        # Tự động chạy
        self.btn_auto = ctk.CTkButton(self.sidebar_frame, text="Tự động chạy ⏭", 
                                      command=self.toggle_auto_run, fg_color="#228B22", hover_color="#006400")
        self.btn_auto.grid(row=7, column=0, padx=20, pady=(10, 5), sticky="n")

        # Thanh tốc độ
        self.label_speed = ctk.CTkLabel(self.sidebar_frame, text=f"Độ trễ: {self.auto_speed_ms}ms (Chậm ↔ Nhanh)", font=ctk.CTkFont(size=11))
        self.label_speed.grid(row=8, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.slider_speed = ctk.CTkSlider(self.sidebar_frame, from_=500, to=1, command=self.on_speed_change)
        self.slider_speed.grid(row=9, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.slider_speed.set(150)

        # Thống kê
        self.stats_frame = ctk.CTkFrame(self.sidebar_frame, corner_radius=10, fg_color="#2b2b2b")
        self.stats_frame.grid(row=10, column=0, padx=20, pady=20, sticky="nsew")
        
        self.label_stats_title = ctk.CTkLabel(self.stats_frame, text="Thống kê:", font=ctk.CTkFont(weight="bold"))
        self.label_stats_title.pack(pady=(10,0))
        
        self.text_stats = ctk.CTkTextbox(self.stats_frame, width=230, height=80, font=("Arial", 11), 
                                        fg_color="transparent", activate_scrollbars=False)
        self.text_stats.pack(padx=10, pady=10)
        self.text_stats.configure(state="disabled")

        # ----------------------------------
        # KHU VỰC HIỂN THỊ CHÍNH
        # ----------------------------------
        self.text_area = ctk.CTkTextbox(self, font=("Courier New", 13), fg_color="#1e1e1e", border_width=1, border_color="#333333")
        self.text_area.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="nsew")
        self.text_area.configure(state="disabled")

        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.grid(row=1, column=1, padx=20, pady=(10, 20), sticky="ew")
        self.nav_frame.grid_columnconfigure(1, weight=1)

        self.btn_prev = ctk.CTkButton(self.nav_frame, text="◀ Trước", command=self.on_prev, width=80)
        self.btn_prev.grid(row=0, column=0, padx=(10, 10))

        self.slider_step = ctk.CTkSlider(self.nav_frame, from_=0, to=1, command=self.on_step_slider_change)
        self.slider_step.grid(row=0, column=1, sticky="ew", padx=10)
        
        self.step_label = ctk.CTkLabel(self.nav_frame, text="Bước: 0/0", font=ctk.CTkFont(weight="bold"))
        self.step_label.grid(row=1, column=1, pady=(5,0))

        self.btn_next = ctk.CTkButton(self.nav_frame, text="Tiếp ▶", command=self.on_next, width=80)
        self.btn_next.grid(row=0, column=2, padx=(10, 10))

    # ==========================================
    # LOGIC XỬ LÝ CHUYỂN LEVEL
    # ==========================================
    def prev_level(self):
        if not self.testcase_keys: return
        current_val = self.combo_testcases.get()
        try:
            idx = self.testcase_keys.index(current_val)
        except ValueError:
            idx = 0
        new_idx = max(0, idx - 1)
        self.combo_testcases.set(self.testcase_keys[new_idx])

    def next_level(self):
        if not self.testcase_keys: return
        current_val = self.combo_testcases.get()
        try:
            idx = self.testcase_keys.index(current_val)
        except ValueError:
            idx = 0
        new_idx = min(len(self.testcase_keys) - 1, idx + 1)
        self.combo_testcases.set(self.testcase_keys[new_idx])

    # ==========================================
    # LOGIC XỬ LÝ KHÁC
    # ==========================================
    def on_speed_change(self, value):
        self.auto_speed_ms = int(value)
        self.label_speed.configure(text=f"Độ trễ: {self.auto_speed_ms}ms (Chậm ↔ Nhanh)")

    def trigger_solve(self):
        if not self.testcase_keys: return
        
        test_name = self.combo_testcases.get()
        algo = self.combo_algo.get()
        cache_key = f"{test_name}_{algo}"
        
        self.current_algo = algo
        self.is_auto_running = False
        self.btn_auto.configure(text="Tự động chạy ⏭", fg_color="#228B22")

        self.current_row_clues = TEST_CASES[test_name]["r"]
        self.current_col_clues = TEST_CASES[test_name]["c"]

        if cache_key not in self.CACHE:
            self.update_text_area(f"\n⏳ Đang chạy thuật toán {algo} cho bài toán:\n{test_name}\n\nVui lòng chờ trong giây lát...")
            self.update_stats_area("Đang tính toán...")
            self.update() 

            tracemalloc.start()
            start_time = time.perf_counter()

            # Gọi đúng hàm tương ứng với 3 thuật toán
            if algo == "Heuristic (GBFS)":
                g_hist, a_hist = solve_nonogram_heuristic(self.current_row_clues, self.current_col_clues)
            elif algo == "Blind Search (DFS)":
                g_hist, a_hist = solve_nonogram_dfs(self.current_row_clues, self.current_col_clues)
            elif algo == "Blind Search (BrFS)":
                g_hist, a_hist = solve_nonogram_brfs(self.current_row_clues, self.current_col_clues)

            end_time = time.perf_counter()
            _, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            exec_time = end_time - start_time
            peak_memory_mb = peak_mem / (1024 * 1024)

            stats_msg = f"Thuật toán: {algo}\nThời gian: {exec_time:.4f}s\nRAM đỉnh: {peak_memory_mb:.4f} MB"
            
            self.CACHE[cache_key] = (g_hist, a_hist, stats_msg)

        self.game_history, self.action_history, last_stats = self.CACHE[cache_key]
        self.current_step = 0
        self.total_steps = len(self.game_history) - 1
        
        if self.total_steps > 0:
            self.slider_step.configure(to=self.total_steps, number_of_steps=self.total_steps)
            self.slider_step.set(0)
            
        self.update_stats_area(last_stats)
        self.update_ui_state()

    def update_text_area(self, content):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, content)
        self.text_area.configure(state="disabled")

    def update_stats_area(self, content):
        self.text_stats.configure(state="normal")
        self.text_stats.delete("1.0", tk.END)
        self.text_stats.insert(tk.END, content)
        self.text_stats.configure(state="disabled")

    def update_ui_state(self):
        if self.total_steps > 0:
            board_str = render_board_string(
                self.game_history[self.current_step], 
                self.current_row_clues, 
                self.current_col_clues,
                self.current_step, 
                self.total_steps, 
                self.action_history[self.current_step],
                self.current_algo
            )
            self.update_text_area(board_str)
            self.step_label.configure(text=f"Bước: {self.current_step}/{self.total_steps}")
            self.slider_step.set(self.current_step)
        
        self.btn_prev.configure(state="normal" if self.current_step > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_step < self.total_steps else "disabled")
        self.btn_auto.configure(state="normal" if self.current_step < self.total_steps else "disabled")

    def on_prev(self):
        self.is_auto_running = False
        if self.current_step > 0:
            self.current_step -= 1
            self.update_ui_state()

    def on_next(self):
        self.is_auto_running = False
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.update_ui_state()

    def on_step_slider_change(self, value):
        self.is_auto_running = False
        self.btn_auto.configure(text="Tự động chạy ⏭", fg_color="#228B22")
        
        new_step = int(value)
        if new_step != self.current_step:
            self.current_step = new_step
            self.update_ui_state()

    def toggle_auto_run(self):
        if self.is_auto_running:
            self.is_auto_running = False
            self.btn_auto.configure(text="Tự động chạy ⏭", fg_color="#228B22")
        else:
            if self.current_step == self.total_steps:
                self.current_step = 0
            self.is_auto_running = True
            self.btn_auto.configure(text="Dừng chạy ⏹", fg_color="#B22222")
            self.auto_step()

    def auto_step(self):
        if self.is_auto_running and self.current_step < self.total_steps:
            self.current_step += 1
            self.update_ui_state()
            self.after(self.auto_speed_ms, self.auto_step) 
        else:
            self.is_auto_running = False
            self.btn_auto.configure(text="Tự động chạy ⏭", fg_color="#228B22")

if __name__ == "__main__":
    app = NonogramModernApp()
    app.mainloop()