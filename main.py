import pygame
import sys
import copy
import random
from ai import make_state, astar_solve, state_to_bottles


# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

WIDTH = 1100
HEIGHT = 750

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LiquidSort AI")

clock = pygame.time.Clock()


# ============================================================
# COLORS
# ============================================================

BACKGROUND = (245, 241, 234)
TEXT = (35, 35, 35)

GLASS = (180, 190, 200)
SELECTED = (90, 170, 255)

BLUE = (60, 130, 230)
RED = (225, 70, 75)
GREEN = (70, 180, 105)
YELLOW = (245, 195, 55)
PURPLE = (150, 90, 200)
ORANGE = (240, 140, 50)

WHITE = (255, 255, 255)

BUTTON_COLOR = (225, 220, 210)
BUTTON_HOVER = (210, 205, 195)
BUTTON_BORDER = (180, 190, 200)

DISABLED_BUTTON = (235, 232, 227)


# ============================================================
# FONTS
# ============================================================

title_font = pygame.font.Font(None, 58)
subtitle_font = pygame.font.Font(None, 28)
bottle_font = pygame.font.Font(None, 25)
message_font = pygame.font.Font(None, 28)
button_font = pygame.font.Font(None, 23)
level_font = pygame.font.Font(None, 27)


# ============================================================
# BOTTLE SETTINGS
# ============================================================

BOTTLE_WIDTH = 80

# Slightly smaller than the previous version so that
# two rows of bottles fit comfortably on the screen.
BOTTLE_HEIGHT = 210

NECK_WIDTH = 35
NECK_HEIGHT = 35

CAPACITY = 4


# ============================================================
# COLOR MAP
# ============================================================

COLOR_MAP = {
    "B": BLUE,
    "R": RED,
    "G": GREEN,
    "Y": YELLOW,
    "P": PURPLE,
    "O": ORANGE
}


# ============================================================
# LEVEL CONFIGURATION
# ============================================================

LEVEL_CONFIG = {

    1: {
        "colors": ["B", "R", "G", "Y"],
        "scramble": 14
    },

    2: {
        "colors": ["B", "R", "G", "Y", "P"],
        "scramble": 24
    },

    3: {
        "colors": ["B", "R", "G", "Y", "P", "O"],
        "scramble": 36
    }
}


# ============================================================
# BUTTON SETTINGS
# ============================================================

BUTTON_WIDTH = 110
BUTTON_HEIGHT = 40


# Top-right buttons
UNDO_BUTTON = pygame.Rect(
    820,
    28,
    BUTTON_WIDTH,
    BUTTON_HEIGHT
)

RESET_BUTTON = pygame.Rect(
    945,
    28,
    BUTTON_WIDTH,
    BUTTON_HEIGHT
)

AI_SOLVE_BUTTON = pygame.Rect(820, 80, 235, 40)

# AI statistics panel
AI_PANEL = pygame.Rect(820, 140, 235, 190)


# Level controls
PREV_LEVEL_BUTTON = pygame.Rect(
    375,
    115,
    70,
    38
)

LEVEL_DISPLAY = pygame.Rect(
    455,
    115,
    120,
    38
)

NEXT_LEVEL_BUTTON = pygame.Rect(
    585,
    115,
    70,
    38
)

NEW_PUZZLE_BUTTON = pygame.Rect(
    680,
    115,
    125,
    38
)


# ============================================================
# DRAW BUTTON
# ============================================================

def draw_button(rect, text, enabled=True):

    mouse_pos = pygame.mouse.get_pos()

    if not enabled:

        color = DISABLED_BUTTON

    elif rect.collidepoint(mouse_pos):

        color = BUTTON_HOVER

    else:

        color = BUTTON_COLOR

    # Button background
    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=10
    )

    # Button border
    pygame.draw.rect(
        screen,
        BUTTON_BORDER,
        rect,
        2,
        border_radius=10
    )

    # Button text
    text_surface = button_font.render(
        text,
        True,
        TEXT
    )

    text_x = (
        rect.centerx
        - text_surface.get_width() // 2
    )

    text_y = (
        rect.centery
        - text_surface.get_height() // 2
    )

    screen.blit(
        text_surface,
        (text_x, text_y)
    )


# ============================================================
# DRAW BOTTLE
# ============================================================

def draw_bottle(
    x,
    y,
    liquids,
    selected=False
):

    # --------------------------------------------------------
    # Bottle body
    # --------------------------------------------------------

    body_rect = pygame.Rect(
        x,
        y + NECK_HEIGHT,
        BOTTLE_WIDTH,
        BOTTLE_HEIGHT
    )

    # --------------------------------------------------------
    # Selection highlight
    # --------------------------------------------------------

    if selected:

        highlight_rect = pygame.Rect(
            x - 7,
            y + NECK_HEIGHT - 7,
            BOTTLE_WIDTH + 14,
            BOTTLE_HEIGHT + 14
        )

        pygame.draw.rect(
            screen,
            SELECTED,
            highlight_rect,
            5,
            border_radius=15
        )

    # --------------------------------------------------------
    # Glass body
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        GLASS,
        body_rect,
        3,
        border_radius=12
    )

    # --------------------------------------------------------
    # Bottle neck
    # --------------------------------------------------------

    neck_x = (
        x
        + (BOTTLE_WIDTH - NECK_WIDTH) // 2
    )

    neck_rect = pygame.Rect(
        neck_x,
        y,
        NECK_WIDTH,
        NECK_HEIGHT + 10
    )

    pygame.draw.rect(
        screen,
        GLASS,
        neck_rect,
        3,
        border_radius=5
    )

    # --------------------------------------------------------
    # Liquid layers
    # --------------------------------------------------------

    layer_height = (
        BOTTLE_HEIGHT - 10
    ) // CAPACITY

    for i, liquid in enumerate(liquids):

        color = COLOR_MAP[liquid]

        liquid_rect = pygame.Rect(
            x + 5,
            y + BOTTLE_HEIGHT
            - (i + 1) * layer_height,
            BOTTLE_WIDTH - 10,
            layer_height
        )

        pygame.draw.rect(
            screen,
            color,
            liquid_rect
        )

    # --------------------------------------------------------
    # Separator lines
    # --------------------------------------------------------

    for i in range(1, len(liquids)):

        line_y = (
            y
            + BOTTLE_HEIGHT
            - i * layer_height
        )

        pygame.draw.line(
            screen,
            WHITE,
            (x + 6, line_y),
            (x + BOTTLE_WIDTH - 6, line_y),
            2
        )


# ============================================================
# GET CLICKED BOTTLE
# ============================================================

def get_clicked_bottle(
    mouse_pos,
    bottle_positions
):

    mouse_x, mouse_y = mouse_pos

    for index, (x, y) in enumerate(
        bottle_positions
    ):

        clickable_rect = pygame.Rect(
            x - 8,
            y - 5,
            BOTTLE_WIDTH + 16,
            BOTTLE_HEIGHT + NECK_HEIGHT + 10
        )

        if clickable_rect.collidepoint(
            mouse_x,
            mouse_y
        ):

            return index

    return None


# ============================================================
# TOP COLOR GROUP
# ============================================================

def get_top_group_count(bottle):

    if len(bottle) == 0:

        return 0

    top_color = bottle[-1]

    count = 0

    for i in range(
        len(bottle) - 1,
        -1,
        -1
    ):

        if bottle[i] == top_color:

            count += 1

        else:

            break

    return count


# ============================================================
# CHECK LEGAL POUR
# ============================================================

def can_pour(
    source,
    destination
):

    # Source must contain liquid
    if len(source) == 0:

        return False

    # Destination must have space
    if len(destination) >= CAPACITY:

        return False

    # Empty destination is valid
    if len(destination) == 0:

        return True

    # Otherwise colours must match
    return source[-1] == destination[-1]


# ============================================================
# POUR LIQUID
# ============================================================

def pour(
    source,
    destination
):

    group_count = get_top_group_count(
        source
    )

    available_space = (
        CAPACITY
        - len(destination)
    )

    amount = min(
        group_count,
        available_space
    )

    for _ in range(amount):

        destination.append(
            source.pop()
        )

    return amount


# ============================================================
# CHECK SOLVED
# ============================================================

def is_solved(bottles):

    for bottle in bottles:

        # Empty bottles are allowed
        if len(bottle) == 0:

            continue

        # Filled bottles only
        if len(bottle) != CAPACITY:

            return False

        # Every layer must have the same colour
        if len(set(bottle)) != 1:

            return False

    return True


# ============================================================
# CREATE SOLVED PUZZLE
# ============================================================

def create_solved_bottles(colors):

    bottles = []

    # One complete bottle for each colour
    for color in colors:

        bottles.append(
            [color] * CAPACITY
        )

    # Two empty bottles
    bottles.append([])
    bottles.append([])

    return bottles


# ============================================================
# REVERSE SCRAMBLE
#
# Start from a solved puzzle and perform reverse operations.
#
# Because the puzzle begins in a solved state, reversing these
# operations gives us a state that has a valid solution.
# ============================================================

def reverse_scramble(
    bottles,
    steps,
    rng
):

    last_move = None

    for _ in range(steps):

        candidates = []

        # ----------------------------------------------------
        # Find possible reverse operations
        # ----------------------------------------------------

        for destination_index, destination in enumerate(
            bottles
        ):

            # Cannot remove liquid from an empty bottle
            if len(destination) == 0:

                continue

            color = destination[-1]

            group_count = get_top_group_count(
                destination
            )

            for source_index, source in enumerate(
                bottles
            ):

                # Same bottle
                if source_index == destination_index:

                    continue

                # Receiving bottle must have space
                if len(source) >= CAPACITY:

                    continue

                # Avoid immediately undoing the previous
                # reverse operation
                if last_move is not None:

                    previous_source = last_move[0]
                    previous_destination = last_move[1]

                    if (
                        source_index
                        == previous_destination
                        and
                        destination_index
                        == previous_source
                    ):

                        continue

                # Avoid merging with same colour in the
                # receiving bottle during reverse scrambling
                if (
                    len(source) > 0
                    and source[-1] == color
                ):

                    continue

                max_amount = min(
                    group_count,
                    CAPACITY - len(source)
                )

                for amount in range(
                    1,
                    max_amount + 1
                ):

                    # Keep the reverse operation consistent
                    # with the game's normal pour behaviour.
                    if amount < len(destination):

                        if amount >= group_count:

                            continue

                    candidates.append(
                        (
                            source_index,
                            destination_index,
                            amount
                        )
                    )

        # ----------------------------------------------------
        # No valid reverse operation
        # ----------------------------------------------------

        if not candidates:

            break

        # Choose a random operation
        source_index, destination_index, amount = (
            rng.choice(candidates)
        )

        source = bottles[source_index]
        destination = bottles[destination_index]

        # ----------------------------------------------------
        # Perform reverse operation
        # ----------------------------------------------------

        for _ in range(amount):

            source.append(
                destination.pop()
            )

        last_move = (
            source_index,
            destination_index
        )


# ============================================================
# CHECK WHETHER PUZZLE IS INTERESTING
# ============================================================

def is_interesting_puzzle(bottles):

    # Do not accept an already solved puzzle
    if is_solved(bottles):

        return False

    mixed_bottles = 0

    for bottle in bottles:

        if len(bottle) > 1:

            if len(set(bottle)) > 1:

                mixed_bottles += 1

    # Require at least two mixed bottles
    return mixed_bottles >= 2


# ============================================================
# GENERATE PUZZLE
# ============================================================

def generate_puzzle(level):

    config = LEVEL_CONFIG[level]

    colors = config["colors"]
    scramble_steps = config["scramble"]

    # Try multiple times until an interesting puzzle
    # is generated.
    for _ in range(100):

        rng = random.Random()

        bottles = create_solved_bottles(
            colors
        )

        reverse_scramble(
            bottles,
            scramble_steps,
            rng
        )

        if is_interesting_puzzle(
            bottles
        ):

            return bottles

    # Fallback
    return bottles


# ============================================================
# GET BOTTLE POSITIONS
# ============================================================

def get_bottle_positions(bottle_count):

    positions = []

    gap = 135

    # --------------------------------------------------------
    # Maximum 4 bottles per row
    #
    # 6 bottles -> 4 + 2
    # 7 bottles -> 4 + 3
    # 8 bottles -> 4 + 4
    # --------------------------------------------------------

    first_row_count = min(
        bottle_count,
        4
    )

    second_row_count = (
        bottle_count
        - first_row_count
    )

    # --------------------------------------------------------
    # FIRST ROW
    # --------------------------------------------------------

    if first_row_count > 0:

        total_width = (
            (first_row_count - 1) * gap
            + BOTTLE_WIDTH
        )

        start_x = (
            WIDTH - total_width
        ) // 2

        for i in range(
            first_row_count
        ):

            x = (
                start_x
                + i * gap
            )

            positions.append(
                (x, 195)
            )

    # --------------------------------------------------------
    # SECOND ROW
    # --------------------------------------------------------

    if second_row_count > 0:

        total_width = (
            (second_row_count - 1) * gap
            + BOTTLE_WIDTH
        )

        start_x = (
            WIDTH - total_width
        ) // 2

        for i in range(
            second_row_count
        ):

            x = (
                start_x
                + i * gap
            )

            positions.append(
                (x, 430)
            )

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if len(positions) != bottle_count:

        raise RuntimeError(
            f"Position error: "
            f"{bottle_count} bottles requested, "
            f"but {len(positions)} positions generated."
        )

    return positions


# ============================================================
# RESET CURRENT LEVEL
# ============================================================

def reset_current_level(
    original_bottles
):

    bottles = copy.deepcopy(
        original_bottles
    )

    history = []

    move_count = 0

    selected_bottle = None

    game_won = False

    message = "Select a bottle"

    return (
        bottles,
        history,
        move_count,
        selected_bottle,
        game_won,
        message
    )


# ============================================================
# LOAD NEW LEVEL
# ============================================================

def load_level(level):

    original_bottles = generate_puzzle(
        level
    )

    return (
        reset_current_level(
            original_bottles
        )
        + (
            original_bottles,
        )
    )


# ============================================================
# AI INTEGRATION
# ============================================================

AI_MOVE_DELAY = 500


def start_ai_solver(current_bottles):
    """Run A* on the current Pygame puzzle and return search statistics."""
    current_state = make_state(current_bottles)

    start_time = pygame.time.get_ticks()
    solution, states_explored = astar_solve(current_state)
    end_time = pygame.time.get_ticks()

    search_time = (end_time - start_time) / 1000.0

    if solution is None:
        print("\nA* could not find a solution.")
        return None, states_explored, search_time

    print("\n==============================")
    print("A* SOLUTION FOR CURRENT PUZZLE")
    print("==============================")
    print("States explored:", states_explored)
    print("Total moves:", len(solution))
    print(f"Search time: {search_time:.3f} seconds")

    for i, (source, destination) in enumerate(solution, start=1):
        print(
            f"{i:2}. Bottle {source + 1} -> "
            f"Bottle {destination + 1}"
        )

    return solution, states_explored, search_time


def execute_ai_move(bottles, ai_solution, ai_move_index):
    """Execute one legal move from the A* solution."""
    if ai_move_index >= len(ai_solution):
        return ai_move_index

    source_index, destination_index = ai_solution[ai_move_index]
    source = bottles[source_index]
    destination = bottles[destination_index]

    if can_pour(source, destination):
        amount = pour(source, destination)
        print(
            f"AI Move {ai_move_index + 1}: "
            f"Bottle {source_index + 1} -> "
            f"Bottle {destination_index + 1} "
            f"({amount} layer(s))"
        )
        return ai_move_index + 1

    print("AI error: generated move is no longer legal.")
    return ai_move_index


# ============================================================
# MAIN GAME
# ============================================================

def main():

    running = True

    # --------------------------------------------------------
    # Current level
    # --------------------------------------------------------

    current_level = 1

    # --------------------------------------------------------
    # Load first puzzle
    # --------------------------------------------------------

    (
        bottles,
        history,
        move_count,
        selected_bottle,
        game_won,
        message,
        original_bottles
    ) = load_level(
        current_level
    )

    # AI state
    ai_solution = []
    ai_solving = False
    ai_move_index = 0
    ai_last_move_time = 0
    ai_states_explored = 0
    ai_search_time = 0.0
    ai_highlight_source = None
    ai_highlight_destination = None

    # ========================================================
    # GAME LOOP
    # ========================================================

    while running:

        # ----------------------------------------------------
        # Calculate bottle positions
        # ----------------------------------------------------

        bottle_positions = get_bottle_positions(
            len(bottles)
        )

        # ====================================================
        # EVENT HANDLING
        # ====================================================

        for event in pygame.event.get():

            # ------------------------------------------------
            # CLOSE WINDOW
            # ------------------------------------------------

            if event.type == pygame.QUIT:

                running = False

            # ------------------------------------------------
            # MOUSE CLICK
            # ------------------------------------------------

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:

                    continue

                mouse_pos = pygame.mouse.get_pos()

                # ============================================
                # AI SOLVE
                # ============================================

                if AI_SOLVE_BUTTON.collidepoint(mouse_pos):
                    if not ai_solving and not game_won:
                        message = "AI is calculating a solution..."

                        ai_solution, ai_states_explored, ai_search_time = start_ai_solver(bottles)

                        if ai_solution is not None:
                            ai_move_index = 0
                            ai_solving = True
                            ai_last_move_time = pygame.time.get_ticks()
                            ai_highlight_source = None
                            ai_highlight_destination = None
                            selected_bottle = None
                            message = (
                                f"A* found a solution: "
                                f"{len(ai_solution)} moves"
                            )
                        else:
                            message = "AI could not find a solution."
                    continue

                # ============================================
                # BLOCK MANUAL INPUT WHILE AI IS SOLVING
                # ============================================

                if ai_solving:
                    continue

                # ============================================
                # UNDO
                # ============================================

                if UNDO_BUTTON.collidepoint(
                    mouse_pos
                ):

                    if history:

                        bottles = history.pop()

                        move_count -= 1

                        selected_bottle = None

                        game_won = False

                        message = (
                            f"Move undone. "
                            f"Moves: {move_count}"
                        )

                    else:

                        message = (
                            "Nothing to undo."
                        )

                    continue

                # ============================================
                # RESET
                # ============================================

                if RESET_BUTTON.collidepoint(
                    mouse_pos
                ):

                    (
                        bottles,
                        history,
                        move_count,
                        selected_bottle,
                        game_won,
                        message
                    ) = reset_current_level(
                        original_bottles
                    )

                    ai_solution = []
                    ai_solving = False
                    ai_move_index = 0
                    ai_states_explored = 0
                    ai_search_time = 0.0
                    ai_highlight_source = None
                    ai_highlight_destination = None
                    ai_move_index = 0
                    ai_states_explored = 0

                    continue

                # ============================================
                # PREVIOUS LEVEL
                # ============================================

                if PREV_LEVEL_BUTTON.collidepoint(
                    mouse_pos
                ):

                    if current_level > 1:

                        current_level -= 1

                        (
                            bottles,
                            history,
                            move_count,
                            selected_bottle,
                            game_won,
                            message,
                            original_bottles
                        ) = load_level(
                            current_level
                        )

                        ai_solution = []
                        ai_solving = False
                        ai_move_index = 0
                        ai_states_explored = 0
                        ai_search_time = 0.0
                        ai_highlight_source = None
                        ai_highlight_destination = None
                        ai_move_index = 0
                        ai_states_explored = 0

                    else:

                        message = (
                            "You are already at Level 1."
                        )

                    continue

                # ============================================
                # NEXT LEVEL
                # ============================================

                if NEXT_LEVEL_BUTTON.collidepoint(
                    mouse_pos
                ):

                    if current_level < 3:

                        current_level += 1

                        (
                            bottles,
                            history,
                            move_count,
                            selected_bottle,
                            game_won,
                            message,
                            original_bottles
                        ) = load_level(
                            current_level
                        )

                        ai_solution = []
                        ai_solving = False
                        ai_move_index = 0
                        ai_states_explored = 0
                        ai_search_time = 0.0
                        ai_highlight_source = None
                        ai_highlight_destination = None
                        ai_move_index = 0
                        ai_states_explored = 0

                    else:

                        message = (
                            "You are already at Level 3."
                        )

                    continue

                # ============================================
                # NEW PUZZLE
                # ============================================

                if NEW_PUZZLE_BUTTON.collidepoint(
                    mouse_pos
                ):

                    (
                        bottles,
                        history,
                        move_count,
                        selected_bottle,
                        game_won,
                        message,
                        original_bottles
                    ) = load_level(
                        current_level
                    )

                    ai_solution = []
                    ai_solving = False
                    ai_move_index = 0
                    ai_states_explored = 0
                    ai_search_time = 0.0
                    ai_highlight_source = None
                    ai_highlight_destination = None
                    ai_move_index = 0
                    ai_states_explored = 0

                    message = (
                        f"New Level {current_level} "
                        f"puzzle generated."
                    )

                    continue

                # ============================================
                # GAME BOARD
                # ============================================

                if not game_won:

                    clicked = get_clicked_bottle(
                        mouse_pos,
                        bottle_positions
                    )

                    if clicked is None:

                        continue

                    # ========================================
                    # SELECT SOURCE
                    # ========================================

                    if selected_bottle is None:

                        # Empty bottles cannot be sources
                        if len(
                            bottles[clicked]
                        ) == 0:

                            message = (
                                "That bottle is empty."
                            )

                        else:

                            selected_bottle = clicked

                            message = (
                                f"Bottle "
                                f"{clicked + 1} selected. "
                                f"Choose a destination."
                            )

                    # ========================================
                    # CANCEL SELECTION
                    # ========================================

                    elif clicked == selected_bottle:

                        selected_bottle = None

                        message = (
                            "Selection cancelled."
                        )

                    # ========================================
                    # DESTINATION
                    # ========================================

                    else:

                        source_index = (
                            selected_bottle
                        )

                        destination_index = (
                            clicked
                        )

                        source = bottles[
                            source_index
                        ]

                        destination = bottles[
                            destination_index
                        ]

                        # ==================================
                        # LEGAL MOVE
                        # ==================================

                        if can_pour(
                            source,
                            destination
                        ):

                            # Save state before modifying it
                            history.append(
                                copy.deepcopy(
                                    bottles
                                )
                            )

                            amount = pour(
                                source,
                                destination
                            )

                            move_count += 1

                            plural = (
                                "s"
                                if amount != 1
                                else ""
                            )

                            message = (
                                f"Poured "
                                f"{amount} layer"
                                f"{plural}: "
                                f"Bottle "
                                f"{source_index + 1} "
                                f"-> Bottle "
                                f"{destination_index + 1}"
                            )

                            # Check victory
                            if is_solved(
                                bottles
                            ):

                                game_won = True

                                message = (
                                    "PUZZLE SOLVED! "
                                    f"Moves: "
                                    f"{move_count}"
                                )

                        # ==================================
                        # ILLEGAL MOVE
                        # ==================================

                        else:

                            message = (
                                "Invalid pour! "
                                "Match the top colour "
                                "or use an empty bottle."
                            )

                        selected_bottle = None

        # ====================================================
        # AI ANIMATION / MOVE EXECUTION
        # ====================================================

        if ai_solving:
            current_time = pygame.time.get_ticks()

            if current_time - ai_last_move_time >= AI_MOVE_DELAY:
                history.append(copy.deepcopy(bottles))

                if ai_move_index < len(ai_solution):
                    (
                        ai_highlight_source,
                        ai_highlight_destination
                    ) = ai_solution[ai_move_index]

                ai_move_index = execute_ai_move(
                    bottles, ai_solution, ai_move_index
                )

                move_count += 1
                ai_last_move_time = current_time

                message = (
                    f"AI solving... Move {ai_move_index}/"
                    f"{len(ai_solution)}"
                )

                if is_solved(bottles):
                    game_won = True
                    ai_solving = False
                    message = (
                        "AI SOLVED THE PUZZLE! "
                        f"Moves: {move_count}"
                    )

                elif ai_move_index >= len(ai_solution):
                    ai_solving = False
                    message = "AI finished its solution."

        # ====================================================
        # DRAW BACKGROUND
        # ====================================================

        screen.fill(
            BACKGROUND
        )

        # ====================================================
        # TITLE
        # ====================================================

        title = title_font.render(
            "LIQUID SORT AI",
            True,
            TEXT
        )

        screen.blit(
            title,
            (
                WIDTH // 2
                - title.get_width() // 2,
                35
            )
        )

        # ====================================================
        # SUBTITLE
        # ====================================================

        subtitle = subtitle_font.render(
            "Sort every liquid colour into its own bottle",
            True,
            TEXT
        )

        screen.blit(
            subtitle,
            (
                WIDTH // 2
                - subtitle.get_width() // 2,
                90
            )
        )

        # ====================================================
        # MOVE COUNTER
        # ====================================================

        moves_text = subtitle_font.render(
            f"Moves: {move_count}",
            True,
            TEXT
        )

        screen.blit(
            moves_text,
            (30, 30)
        )

        # ====================================================
        # TOP RIGHT CONTROLS
        # ====================================================

        draw_button(
            UNDO_BUTTON,
            "UNDO",
            enabled=(len(history) > 0 and not ai_solving)
        )

        draw_button(
            RESET_BUTTON,
            "RESET",
            enabled=not ai_solving
        )

        ai_button_label = (
            "AI SOLVING..."
            if ai_solving
            else ("PUZZLE SOLVED" if game_won else "AI SOLVE")
        )

        draw_button(
            AI_SOLVE_BUTTON,
            ai_button_label,
            enabled=(not ai_solving and not game_won)
        )

        # ====================================================
        # LEVEL CONTROLS
        # ====================================================

        draw_button(
            PREV_LEVEL_BUTTON,
            "PREV",
            enabled=(current_level > 1 and not ai_solving)
        )

        # ----------------------------------------------------
        # Level display
        # ----------------------------------------------------

        pygame.draw.rect(
            screen,
            BUTTON_COLOR,
            LEVEL_DISPLAY,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            BUTTON_BORDER,
            LEVEL_DISPLAY,
            2,
            border_radius=10
        )

        level_text = level_font.render(
            f"LEVEL {current_level}",
            True,
            TEXT
        )

        screen.blit(
            level_text,
            (
                LEVEL_DISPLAY.centerx
                - level_text.get_width() // 2,
                LEVEL_DISPLAY.centery
                - level_text.get_height() // 2
            )
        )

        draw_button(
            NEXT_LEVEL_BUTTON,
            "NEXT",
            enabled=(current_level < 3 and not ai_solving)
        )

        draw_button(
            NEW_PUZZLE_BUTTON,
            "NEW PUZZLE",
            enabled=not ai_solving
        )

        # ====================================================
        # LEVEL INFORMATION
        # ====================================================

        config = LEVEL_CONFIG[
            current_level
        ]

        info_text = (
            f"Level {current_level}  |  "
            f"{len(config['colors'])} colours  |  "
            f"{len(bottles)} bottles"
        )

        info_surface = subtitle_font.render(
            info_text,
            True,
            TEXT
        )

        screen.blit(
            info_surface,
            (
                WIDTH // 2
                - info_surface.get_width() // 2,
                155
            )
        )

        # ====================================================
        # DRAW BOTTLES
        # ====================================================

        for i, bottle in enumerate(
            bottles
        ):

            # Safety check
            if i >= len(
                bottle_positions
            ):

                continue

            x, y = bottle_positions[i]

            draw_bottle(
                x,
                y,
                bottle,
                selected=(
                    i == selected_bottle
                    or i == ai_highlight_source
                    or i == ai_highlight_destination
                )
            )

        # ====================================================
        # BOTTLE LABELS
        # ====================================================

        for i, (x, y) in enumerate(
            bottle_positions
        ):

            label = bottle_font.render(
                f"Bottle {i + 1}",
                True,
                TEXT
            )

            label_x = (
                x
                + BOTTLE_WIDTH // 2
                - label.get_width() // 2
            )

            label_y = (
                y
                + NECK_HEIGHT
                + BOTTLE_HEIGHT
                + 8
            )

            screen.blit(
                label,
                (
                    label_x,
                    label_y
                )
            )

        # ====================================================
        # AI SOLVER PANEL
        # ====================================================

        pygame.draw.rect(
            screen,
            WHITE,
            AI_PANEL,
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            BUTTON_BORDER,
            AI_PANEL,
            2,
            border_radius=14
        )

        # Panel title
        ai_title = level_font.render(
            "A* AI SOLVER",
            True,
            TEXT
        )

        screen.blit(
            ai_title,
            (
                AI_PANEL.x + 18,
                AI_PANEL.y + 10
            )
        )

        # Current AI status is placed on its own line so it never
        # overlaps the panel title.
        if ai_solving:
            ai_status_text = (
                f"SOLVING  {ai_move_index}/{len(ai_solution)}"
            )
        elif game_won and ai_solution:
            ai_status_text = "COMPLETED"
        elif ai_solution:
            ai_status_text = "READY"
        else:
            ai_status_text = "IDLE"

        ai_status = bottle_font.render(
            ai_status_text,
            True,
            TEXT
        )

        screen.blit(
            ai_status,
            (
                AI_PANEL.x + 18,
                AI_PANEL.y + 38
            )
        )

        # Progress bar
        progress_rect = pygame.Rect(
            AI_PANEL.x + 18,
            AI_PANEL.y + 62,
            AI_PANEL.width - 36,
            12
        )

        pygame.draw.rect(
            screen,
            BUTTON_COLOR,
            progress_rect,
            border_radius=6
        )

        if ai_solution:
            progress = min(
                ai_move_index / len(ai_solution),
                1.0
            )

            progress_fill = pygame.Rect(
                progress_rect.x,
                progress_rect.y,
                int(progress_rect.width * progress),
                progress_rect.height
            )

            if progress_fill.width > 0:
                pygame.draw.rect(
                    screen,
                    BLUE,
                    progress_fill,
                    border_radius=6
                )

        # Statistics
        stat_lines = [
            f"Algorithm       A*",
            f"Moves           {len(ai_solution) if ai_solution else 0}",
            f"States explored {ai_states_explored}",
            f"Search time     {ai_search_time:.3f}s"
        ]

        for index, line in enumerate(stat_lines):

            stat_surface = bottle_font.render(
                line,
                True,
                TEXT
            )

            screen.blit(
                stat_surface,
                (
                    AI_PANEL.x + 18,
                    AI_PANEL.y + 86 + index * 24
                )
            )

        # ====================================================
        # STATUS MESSAGE
        # ====================================================

        status = message_font.render(
            message,
            True,
            TEXT
        )

        screen.blit(
            status,
            (
                WIDTH // 2
                - status.get_width() // 2,
                715
            )
        )

        # ====================================================
        # UPDATE SCREEN
        # ====================================================

        pygame.display.flip()

        clock.tick(60)

    # ========================================================
    # EXIT
    # ========================================================

    pygame.quit()
    sys.exit()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    main()
