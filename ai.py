# ============================================================
# LIQUID SORT AI
# PHASE 2 - AI SEARCH
#
# State Representation
# Legal Move Generation
# BFS
# DFS
# A*
# Algorithm Comparison
# ============================================================

from collections import deque
import time
import heapq


# ============================================================
# CONSTANTS
# ============================================================

CAPACITY = 4


# ============================================================
# STATE REPRESENTATION
# ============================================================

def make_state(bottles):
    """
    Convert normal game representation into an immutable AI state.

    Example:
        [
            ["R", "B"],
            ["G"],
            []
        ]

    becomes:
        (
            ("R", "B"),
            ("G",),
            ()
        )
    """

    return tuple(
        tuple(bottle)
        for bottle in bottles
    )


# ============================================================
# CONVERT STATE BACK TO BOTTLES
# ============================================================

def state_to_bottles(state):
    """
    Convert an AI state back into normal lists.
    """

    return [
        list(bottle)
        for bottle in state
    ]


# ============================================================
# TOP COLOR GROUP
# ============================================================

def get_top_group_count(bottle):
    """
    Count consecutive layers of the same colour
    at the top of the bottle.
    """

    if not bottle:
        return 0

    top_color = bottle[-1]
    count = 0

    for i in range(len(bottle) - 1, -1, -1):

        if bottle[i] == top_color:
            count += 1
        else:
            break

    return count


# ============================================================
# CHECK LEGAL MOVE
# ============================================================

def can_pour(source, destination):
    """
    Check whether liquid can be poured from source
    to destination.
    """

    # Source must contain liquid
    if not source:
        return False

    # Destination must have free space
    if len(destination) >= CAPACITY:
        return False

    # Empty destination is allowed
    if not destination:
        return True

    # Otherwise top colours must match
    return source[-1] == destination[-1]


# ============================================================
# APPLY POUR
# ============================================================

def apply_pour(
    bottles,
    source_index,
    destination_index
):
    """
    Apply one legal pour without modifying the
    original state.
    """

    new_bottles = [
        bottle.copy()
        for bottle in bottles
    ]

    source = new_bottles[source_index]
    destination = new_bottles[destination_index]

    # Number of consecutive top layers
    group_count = get_top_group_count(source)

    # Free space in destination
    available_space = CAPACITY - len(destination)

    # Number of layers that can actually move
    amount = min(
        group_count,
        available_space
    )

    # Perform the pour
    for _ in range(amount):
        destination.append(source.pop())

    return new_bottles


# ============================================================
# GENERATE ALL LEGAL MOVES
# ============================================================

def get_possible_moves(state):
    """
    Generate every legal next state.

    Returns:
        [
            (
                next_state,
                source_index,
                destination_index
            ),
            ...
        ]
    """

    bottles = state_to_bottles(state)
    possible_moves = []

    number_of_bottles = len(bottles)

    # Try every source bottle
    for source_index in range(number_of_bottles):

        source = bottles[source_index]

        # Empty bottles cannot be sources
        if not source:
            continue

        # Try every destination bottle
        for destination_index in range(number_of_bottles):

            # Cannot pour into itself
            if source_index == destination_index:
                continue

            destination = bottles[destination_index]

            # Check legal move
            if not can_pour(source, destination):
                continue

            # Apply move
            new_bottles = apply_pour(
                bottles,
                source_index,
                destination_index
            )

            new_state = make_state(new_bottles)

            possible_moves.append(
                (
                    new_state,
                    source_index,
                    destination_index
                )
            )

    return possible_moves


# ============================================================
# CHECK SOLVED STATE
# ============================================================

def is_solved(state):
    """
    A puzzle is solved when every non-empty bottle is:
        1. Completely full
        2. One colour only

    Empty bottles are allowed.
    """

    for bottle in state:

        # Empty bottle is fine
        if not bottle:
            continue

        # Non-empty bottle must be full
        if len(bottle) != CAPACITY:
            return False

        # All layers must have the same colour
        if len(set(bottle)) != 1:
            return False

    return True


# ============================================================
# A* HEURISTIC
# ============================================================

def heuristic(state):
    """
    Estimate how disorganized the state is.

    The heuristic counts:
      - colour transitions inside bottles
      - an additional penalty for mixed bottles

    Lower score = closer to the goal.
    """

    score = 0

    for bottle in state:

        if not bottle:
            continue

        # Count colour transitions
        for i in range(len(bottle) - 1):

            if bottle[i] != bottle[i + 1]:
                score += 1

        # Penalize mixed bottles
        if len(set(bottle)) > 1:
            score += 1

    return score


# ============================================================
# PRINT STATE
# ============================================================

def print_state(state):
    """
    Print a state in a readable format.
    """

    print("\nCurrent AI State:")

    for i, bottle in enumerate(state):

        print(
            f"Bottle {i + 1}: "
            f"{list(bottle)}"
        )


# ============================================================
# RECONSTRUCT BFS SOLUTION
# ============================================================

def reconstruct_solution(
    goal_state,
    parent,
    move_used
):
    """
    Reconstruct the path from the start state
    to the goal state.
    """

    solution = []
    current_state = goal_state

    # Walk backwards from goal to start
    while current_state in parent:

        move = move_used[current_state]

        solution.append(move)

        current_state = parent[current_state]

    # Reverse because we reconstructed backwards
    solution.reverse()

    return solution


# ============================================================
# BFS SOLVER
# ============================================================

def bfs_solve(start_state):
    """
    Solve using Breadth-First Search.

    BFS explores states level by level.

    Returns:
        solution
        states_explored
    """

    queue = deque()

    queue.append(start_state)

    # Visited states prevent repeated exploration
    visited = set()
    visited.add(start_state)

    # Parent relationship
    parent = {}

    # Move used to reach each state
    move_used = {}

    states_explored = 0

    while queue:

        # Remove oldest state
        current_state = queue.popleft()

        states_explored += 1

        # Goal test
        if is_solved(current_state):

            solution = reconstruct_solution(
                current_state,
                parent,
                move_used
            )

            return solution, states_explored

        # Generate possible moves
        possible_moves = get_possible_moves(
            current_state
        )

        # Explore successors
        for (
            next_state,
            source,
            destination
        ) in possible_moves:

            if next_state in visited:
                continue

            visited.add(next_state)

            parent[next_state] = current_state

            move_used[next_state] = (
                source,
                destination
            )

            queue.append(next_state)

    # No solution
    return None, states_explored


# ============================================================
# DFS SOLVER
# ============================================================

def dfs_solve(start_state):
    """
    Solve using Depth-First Search.

    DFS explores one branch deeply before
    backtracking.

    Returns:
        solution
        states_explored
    """

    # Stack stores:
    # (current_state, path_taken)
    stack = [
        (start_state, [])
    ]

    visited = set()

    states_explored = 0

    while stack:

        current_state, path = stack.pop()

        # Skip already visited states
        if current_state in visited:
            continue

        visited.add(current_state)

        states_explored += 1

        # Goal test
        if is_solved(current_state):
            return path, states_explored

        # Generate successors
        possible_moves = get_possible_moves(
            current_state
        )

        # Add successors to stack
        for (
            next_state,
            source,
            destination
        ) in possible_moves:

            if next_state in visited:
                continue

            new_path = path + [
                (source, destination)
            ]

            stack.append(
                (
                    next_state,
                    new_path
                )
            )

    # No solution
    return None, states_explored


# ============================================================
# A* SOLVER
# ============================================================

def astar_solve(start_state):
    """
    Solve Liquid Sort using A* Search.

    f(n) = g(n) + h(n)

    g(n) = cost/moves already made
    h(n) = heuristic estimate

    Returns:
        solution
        states_explored
    """

    # Priority queue entry:
    #
    # (f_score, g_score, counter, state, path)

    counter = 0

    priority_queue = []

    initial_h = heuristic(start_state)

    heapq.heappush(
        priority_queue,
        (
            initial_h,
            0,
            counter,
            start_state,
            []
        )
    )

    # Best known cost to each state
    best_cost = {
        start_state: 0
    }

    states_explored = 0

    while priority_queue:

        (
            f_score,
            g_score,
            _,
            current_state,
            path
        ) = heapq.heappop(priority_queue)

        states_explored += 1

        # Goal test
        if is_solved(current_state):
            return path, states_explored

        # Generate successors
        possible_moves = get_possible_moves(
            current_state
        )

        for (
            next_state,
            source,
            destination
        ) in possible_moves:

            # Every pour has cost 1
            new_g = g_score + 1

            # Only continue if this is a better path
            if (
                next_state not in best_cost
                or new_g < best_cost[next_state]
            ):

                best_cost[next_state] = new_g

                # Estimate remaining cost
                h = heuristic(next_state)

                # A* evaluation
                f = new_g + h

                counter += 1

                new_path = path + [
                    (source, destination)
                ]

                heapq.heappush(
                    priority_queue,
                    (
                        f,
                        new_g,
                        counter,
                        next_state,
                        new_path
                    )
                )

    # No solution
    return None, states_explored


# ============================================================
# PRINT SOLUTION
# ============================================================

def print_solution(
    solution,
    algorithm_name="BFS"
):
    """
    Print a solution in human-readable form.
    """

    if solution is None:

        print(
            f"\nNo {algorithm_name} solution found."
        )

        return

    print(
        "\n=============================="
    )

    print(
        f"{algorithm_name} SOLUTION"
    )

    print(
        "=============================="
    )

    print(
        f"Total moves: {len(solution)}"
    )

    print()

    for step, (
        source,
        destination
    ) in enumerate(
        solution,
        start=1
    ):

        print(
            f"{step:2d}. "
            f"Bottle {source + 1} "
            f"-> "
            f"Bottle {destination + 1}"
        )


# ============================================================
# TEST PUZZLE
# ============================================================

def create_test_puzzle():
    """
    Test puzzle used for comparing BFS, DFS and A*.
    """

    return [
        ["Y", "G", "R", "B"],
        ["B", "R", "Y", "G"],
        ["G", "B", "Y", "R"],
        ["R", "Y", "G", "B"],
        [],
        []
    ]


# ============================================================
# MAIN TEST
#
# IMPORTANT:
# Everything below is protected by this condition.
# Therefore importing ai.py from main.py will NOT execute
# the testing code.
# ============================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        "       LIQUID SORT AI - SEARCH TEST"
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Create test puzzle
    # --------------------------------------------------------

    test_bottles = create_test_puzzle()

    # Convert into immutable AI state
    start_state = make_state(
        test_bottles
    )

    # --------------------------------------------------------
    # Display starting state
    # --------------------------------------------------------

    print_state(
        start_state
    )

    # --------------------------------------------------------
    # Check starting state
    # --------------------------------------------------------

    print(
        "\nSolved:",
        is_solved(start_state)
    )

    # --------------------------------------------------------
    # Count immediate legal moves
    # --------------------------------------------------------

    possible_moves = get_possible_moves(
        start_state
    )

    print(
        "\nPossible first moves:",
        len(possible_moves)
    )

    # ========================================================
    # BFS
    # ========================================================

    print("\nRunning BFS...")

    bfs_start_time = time.perf_counter()

    solution, states_explored = bfs_solve(
        start_state
    )

    bfs_end_time = time.perf_counter()

    bfs_time = (
        bfs_end_time
        - bfs_start_time
    )

    print(
        f"\nBFS states explored: "
        f"{states_explored}"
    )

    print_solution(
        solution,
        "BFS"
    )

    print(
        f"BFS execution time: "
        f"{bfs_time:.6f} seconds"
    )

    # ========================================================
    # DFS
    # ========================================================

    print("\nRunning DFS...")

    dfs_start_time = time.perf_counter()

    dfs_solution, dfs_states = dfs_solve(
        start_state
    )

    dfs_end_time = time.perf_counter()

    dfs_time = (
        dfs_end_time
        - dfs_start_time
    )

    print_solution(
        dfs_solution,
        "DFS"
    )

    print(
        f"DFS states explored: "
        f"{dfs_states}"
    )

    print(
        f"DFS execution time: "
        f"{dfs_time:.6f} seconds"
    )

    # ========================================================
    # A*
    # ========================================================

    print("\nRunning A*...")

    astar_start_time = time.perf_counter()

    astar_solution, astar_states = astar_solve(
        start_state
    )

    astar_end_time = time.perf_counter()

    astar_time = (
        astar_end_time
        - astar_start_time
    )

    print_solution(
        astar_solution,
        "A*"
    )

    print(
        f"A* states explored: "
        f"{astar_states}"
    )

    print(
        f"A* execution time: "
        f"{astar_time:.6f} seconds"
    )

    # ========================================================
    # ALGORITHM COMPARISON
    # ========================================================

    print("\n")

    print("=" * 70)

    print(
        "                       ALGORITHM COMPARISON"
    )

    print("=" * 70)

    print(
        f"{'Algorithm':<12}"
        f"{'Moves':<12}"
        f"{'States':<18}"
        f"{'Time (sec)':<15}"
    )

    print("-" * 70)

    bfs_moves = (
        len(solution)
        if solution is not None
        else "-"
    )

    dfs_moves = (
        len(dfs_solution)
        if dfs_solution is not None
        else "-"
    )

    astar_moves = (
        len(astar_solution)
        if astar_solution is not None
        else "-"
    )

    print(
        f"{'BFS':<12}"
        f"{bfs_moves!s:<12}"
        f"{states_explored:<18}"
        f"{bfs_time:<15.6f}"
    )

    print(
        f"{'DFS':<12}"
        f"{dfs_moves!s:<12}"
        f"{dfs_states:<18}"
        f"{dfs_time:<15.6f}"
    )

    print(
        f"{'A*':<12}"
        f"{astar_moves!s:<12}"
        f"{astar_states:<18}"
        f"{astar_time:<15.6f}"
    )

    print("=" * 70)

    print(
        "\nSearch comparison completed successfully."
    )
