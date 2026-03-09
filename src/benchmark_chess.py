import time
import tracemalloc
import matplotlib.pyplot as plt

from chess_puzzles import TEST_CASES, parse_fen, dfs, bfs, astar

def run_benchmark():

    print("🚀 CHẠY BENCHMARK CHESS PUZZLE")

    test_names = list(TEST_CASES.keys())

    algorithms = {
        "Heuristic (A*)": astar,
        "Blind (DFS)": lambda board: dfs(board, [board], set()),
        "Blind (BFS)": bfs
    }

    results_time = {algo: [] for algo in algorithms}
    results_mem = {algo: [] for algo in algorithms}

    for test_name in test_names:

        print(f"\n▶ Test: {test_name}")

        fen = TEST_CASES[test_name]["fen"]
        board = parse_fen(fen)

        for algo_name, func in algorithms.items():

            print(f"   + {algo_name}...", end="", flush=True)

            tracemalloc.start()
            start = time.perf_counter()

            try:

                func(board)

                end = time.perf_counter()

                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                exec_time = end - start
                peak_memory = peak / (1024 * 1024)

                results_time[algo_name].append(exec_time)
                results_mem[algo_name].append(peak_memory)

                print(f" Done ({exec_time:.4f}s | {peak_memory:.4f} MB)")

            except MemoryError:

                tracemalloc.stop()

                print(" ❌ Memory Error")

                results_time[algo_name].append(None)
                results_mem[algo_name].append(None)

            except Exception as e:

                tracemalloc.stop()

                print(f" ❌ Error: {e}")

                results_time[algo_name].append(None)
                results_mem[algo_name].append(None)

    # ===============================
    # DRAW GRAPH
    # ===============================

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    x_positions = range(len(test_names))

    styles = {
        "Heuristic (A*)": {"color": "#2ca02c", "marker": "o", "linewidth": 2.5},
        "Blind (DFS)": {"color": "#1f77b4", "marker": "s", "linewidth": 2.5},
        "Blind (BFS)": {"color": "#ff7f0e", "marker": "^", "linewidth": 2.5, "linestyle": "--"}
    }

    # ===============================
    # TIME GRAPH
    # ===============================

    for algo in algorithms:
        ax1.plot(
            x_positions,
            results_time[algo],
            label=algo,
            **styles[algo]
        )

    ax1.set_ylabel("Execution Time (s)")
    ax1.set_title("Chess Puzzle - Execution Time Comparison")
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(test_names)
    ax1.legend()
    ax1.grid(True)

    # ===============================
    # MEMORY GRAPH
    # ===============================

    for algo in algorithms:
        ax2.plot(
            x_positions,
            results_mem[algo],
            label=algo,
            **styles[algo]
        )

    ax2.set_ylabel("Memory Usage (MB)")
    ax2.set_title("Chess Puzzle - Memory Usage Comparison")
    ax2.set_xticks(x_positions)
    ax2.set_xticklabels(test_names)
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_benchmark()