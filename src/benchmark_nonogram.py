import time
import tracemalloc
import matplotlib.pyplot as plt
import numpy as np

from nonogram import TEST_CASES, solve_nonogram_dfs, solve_nonogram_brfs, solve_nonogram_heuristic

def run_benchmark():
    print("BẮT ĐẦU CHẠY BENCHMARK ĐÁNH GIÁ THUẬT TOÁN...")
    all_tests = list(TEST_CASES.keys())
    test_names = all_tests[20:40] 
    
    algorithms = {
        "Heuristic (GBFS)": solve_nonogram_heuristic,
        "Blind (DFS)": solve_nonogram_dfs,
        "Blind (BrFS)": solve_nonogram_brfs

    }

    results_time = {algo: [] for algo in algorithms}
    results_mem = {algo: [] for algo in algorithms}

    for test_name in test_names:
        print(f"\n▶ Đang test bài: {test_name}")
        row_clues = TEST_CASES[test_name]["r"]
        col_clues = TEST_CASES[test_name]["c"]

        for algo_name, func in algorithms.items():
            print(f"  + Chạy {algo_name}...", end="", flush=True)
            
            tracemalloc.start()
            start_time = time.perf_counter()
            
            try:
                func(row_clues, col_clues)
                
                end_time = time.perf_counter()
                _, peak_mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                exec_time = end_time - start_time
                peak_memory_mb = peak_mem / (1024 * 1024)

                results_time[algo_name].append(exec_time)
                results_mem[algo_name].append(peak_memory_mb)
                
                print(f" Xong! ({exec_time:.4f}s | {peak_memory_mb:.4f} MB)")
                
            except MemoryError:
                tracemalloc.stop()
                print(" ❌ TRÀN BỘ NHỚ (Memory Error)!")
                results_time[algo_name].append(None)
                results_mem[algo_name].append(None)
            except Exception as e:
                tracemalloc.stop()
                print(f" ❌ LỖI KHÔNG XÁC ĐỊNH: {e}")
                results_time[algo_name].append(None)
                results_mem[algo_name].append(None)

    # LINE CHART
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    short_labels = [name.split(':')[0] if ':' in name else name[:5] for name in test_names]

    styles = {
        "Heuristic (GBFS)": {"color": "#2ca02c", "marker": "o", "linewidth": 2.5},
        "Blind (DFS)": {"color": "#1f77b4", "marker": "s", "linewidth": 2.5},
        "Blind (BrFS)": {"color": "#ff7f0e", "marker": "^", "linewidth": 2.5, "linestyle": "--"}
    }

    x_positions = range(len(test_names))

    #  1. TIME
    for algo in algorithms:
        ax1.plot(x_positions, results_time[algo], label=algo, **styles[algo])

    ax1.set_ylabel('Execution Time (s)', fontsize=11)
    ax1.set_title('Execution Time', fontweight='bold', fontsize=13)
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(short_labels, rotation=0, fontsize=10)
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.7)

    # 2. MEMORY
    for algo in algorithms:
        ax2.plot(x_positions, results_mem[algo], label=algo, **styles[algo])

    ax2.set_ylabel('Memory Usage (MB)', fontsize=11)
    ax2.set_title('Memory Usage', fontweight='bold', fontsize=13)
    ax2.set_xticks(x_positions)
    ax2.set_xticklabels(short_labels, rotation=0, fontsize=10)
    ax2.legend()
    ax2.grid(True, linestyle=':', alpha=0.7)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_benchmark()