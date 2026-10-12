# 🧪 LiquidSort AI

**An AI-based Liquid Sort Puzzle Solver using BFS, DFS, and A* Search Algorithms**

LiquidSort AI is a Python-based project that solves the Liquid Sort puzzle by exploring possible bottle configurations and finding a sequence of valid moves to organize the colours. It implements three classical AI search algorithms and compares their performance based on solution length, states explored, and execution time.

## 📌 Project Overview

The Liquid Sort puzzle consists of bottles containing layers of different colours. The objective is to arrange the colours so that each non-empty bottle contains only one colour and is completely filled.

This project models the puzzle as a state-space search problem. It generates legal moves, explores possible states, identifies a goal state, and reconstructs the solution path.

## ✨ Features

- **State Representation:** Represents bottle configurations as immutable states for efficient state comparison.
- **Legal Move Generation:** Checks whether liquid can be poured between bottles according to the game rules.
- **Breadth-First Search (BFS):** Explores states level by level to find a minimum-move solution when a solution exists.
- **Depth-First Search (DFS):** Explores one path deeply before backtracking.
- **A* Search:** Uses a heuristic to prioritize promising states.
- **Solution Reconstruction:** Displays the sequence of bottle-to-bottle moves.
- **Algorithm Comparison:** Measures execution time, number of states explored, and solution length for each algorithm.

## 🛠️ Technologies Used

- Python 3
- `collections.deque` for BFS
- `heapq` for A* priority queue
- `time` for execution-time measurement
- Python data structures such as lists, tuples, sets, and dictionaries

No external Python packages are required by the current implementation.

## 📂 Project Structure

```text
LiquidSort_AI/
├── ai.py
├── main.py
├── .gitignore
└── README.md
```

- `ai.py` — Implements state representation, legal moves, goal checking, BFS, DFS, A*, and algorithm comparison.
- `main.py` — Main project entry point.
- `.gitignore` — Specifies files and folders Git should ignore.
- `README.md` — Project documentation.

## ⚙️ How It Works

1. **Initialize the puzzle:** Define the starting arrangement of colours in the bottles.
2. **Represent the state:** Convert bottle lists into immutable tuples.
3. **Generate legal moves:** Identify valid source and destination bottles.
4. **Explore states:** Apply BFS, DFS, or A* to search for a solution.
5. **Check the goal:** Verify that every non-empty bottle is full and contains a single colour.
6. **Reconstruct the solution:** Recover the moves from the initial state to the goal state.
7. **Compare algorithms:** Display the number of moves, explored states, and execution time.

## 🔍 Search Algorithms

| Algorithm | Search Strategy | Key Characteristic |
|---|---|---|
| BFS | Level-by-level exploration | Finds a minimum-move solution when all moves have equal cost and the search completes |
| DFS | Deep exploration with backtracking | May find a solution without finding the shortest one |
| A* | Priority-based exploration | Uses `f(n) = g(n) + h(n)` to prioritize states |

For A*, `g(n)` represents the cost of moves already taken, while `h(n)` estimates how disorganized the current state is. The current heuristic counts colour transitions and adds a penalty for mixed-colour bottles.

**Note:** The current A* heuristic is a search priority estimate; it is not established as an admissible heuristic, so shortest-path optimality is not guaranteed for A*.

## 💻 Requirements

- Python 3.9 or later recommended
- Git (optional, for cloning the repository)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/RMonisha-06/LiquidSort_AI.git
```

### 2. Open the project directory

```bash
cd LiquidSort_AI
```

### 3. Run the AI search implementation

```bash
python ai.py
```

The script runs the predefined test puzzle using BFS, DFS, and A*. It prints the solutions, states explored, execution times, and an algorithm comparison table.

If your system uses the `python3` command, run:

```bash
python3 ai.py
```

## 📊 Performance Evaluation

The program compares the algorithms using:

- **Solution length:** Number of moves required to solve the puzzle.
- **States explored:** Number of states processed during the search.
- **Execution time:** Time taken by each algorithm to complete its search.

Results depend on the initial puzzle configuration and the machine on which the program runs. No fixed performance values are reported here because results should be measured by running the implementation.

## 🔮 Future Improvements

- Add a graphical user interface for interactive puzzle input.
- Support custom bottle configurations.
- Improve the A* heuristic.
- Add safeguards for larger search spaces and memory usage.
- Visualize the solution steps and compare algorithms across multiple puzzles.

## 👩‍💻 Author

**Monisha**

GitHub: [RMonisha-06](https://github.com/RMonisha-06)

## 📄 License

No license has been specified yet. Unless a license is added, the repository's code should not be assumed to be available for unrestricted reuse.
