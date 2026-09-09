"""
crosswordgenerator.py

Builds a crossword layout from a list of words using randomised
backtracking: words are placed one at a time, each new word must
cross an already-placed word (except the very first), and if a
placement leads to a dead end we backtrack and try another
position.

Also provides the clue-numbering logic (turning grid positions
into "1 Across", "2 Down", etc.) since that's about crossword
*structure*, not drawing.
"""

import random


CELL_SIZE = 40
FONT_SIZE = 20
MAX_ATTEMPTS = 5000  # cap on total placement attempts before giving up

grid = {}            # {(row, col): letter}
word_positions = {}  # {word: {"row": r, "col": c, "direction": "across"/"down"}}

_attempts = 0  # internal counter, reset each time solve() is called


# ============================================================
# GET THE CELLS A WORD WOULD OCCUPY
# ============================================================

def get_positions(word, row, col, direction):

    positions = []

    for i in range(len(word)):

        if direction == "across":
            position = (row, col + i)
        else:
            position = (row + i, col)

        positions.append(position)

    return positions


# ============================================================
# CHECK WHETHER A WORD CAN BE PLACED
# ============================================================

def can_place(word, row, col, direction, require_crossing=False):

    positions = get_positions(word, row, col, direction)
    crossing_count = 0

    # --------------------------------------------------------
    # Check every letter
    # --------------------------------------------------------

    for i, position in enumerate(positions):

        letter = word[i]

        # If this square already has a letter, it must match.
        if position in grid:

            if grid[position] != letter:
                return False

            crossing_count += 1

    # --------------------------------------------------------
    # The word must cross the existing crossword
    # --------------------------------------------------------

    if require_crossing and crossing_count == 0:
        return False

    # --------------------------------------------------------
    # Check the square immediately before the word
    # --------------------------------------------------------

    if direction == "across":
        before = (row, col - 1)
    else:
        before = (row - 1, col)

    if before in grid:
        return False

    # --------------------------------------------------------
    # Check the square immediately after the word
    # --------------------------------------------------------

    if direction == "across":
        after = (row, col + len(word))
    else:
        after = (row + len(word), col)

    if after in grid:
        return False

    # --------------------------------------------------------
    # Check neighbouring squares
    #
    # This is what stops words sitting directly next to each
    # other with no gap.
    # --------------------------------------------------------

    for i, position in enumerate(positions):

        r, c = position
        crossing = position in grid

        if direction == "across":
            neighbours = [(r - 1, c), (r + 1, c)]
        else:
            neighbours = [(r, c - 1), (r, c + 1)]

        for neighbour in neighbours:

            # A neighbouring letter is only allowed when this
            # square is the actual crossing point.
            if neighbour in grid and not crossing:
                return False

    return True


# ============================================================
# PLACE / REMOVE A WORD
# ============================================================

def place_word(word, row, col, direction):

    positions = get_positions(word, row, col, direction)

    for i, position in enumerate(positions):
        if position not in grid:
            grid[position] = word[i]

    word_positions[word] = {
        "row": row,
        "col": col,
        "direction": direction
    }


def remove_word(word, row, col, direction):

    positions = get_positions(word, row, col, direction)

    for position in positions:
        if position in grid:
            del grid[position]

    word_positions.pop(word, None)


# ============================================================
# SAVE / RESTORE GRID (used for backtracking)
# ============================================================

def save_grid():
    return (grid.copy(), word_positions.copy())


def restore_grid(saved_state):

    saved_grid, saved_word_positions = saved_state

    grid.clear()
    grid.update(saved_grid)

    word_positions.clear()
    word_positions.update(saved_word_positions)


# ============================================================
# FIND POSSIBLE POSITIONS FOR A WORD
# ============================================================

def find_positions(word):

    positions = []

    # --------------------------------------------------------
    # If the grid is empty, this is the first word - anchor it
    # at the origin. (This also covers what used to be a
    # separate "index == 0" special case in solve().)
    # --------------------------------------------------------

    if not grid:
        return [(0, 0, "across")]

    # --------------------------------------------------------
    # Otherwise, look for existing letters that match a letter
    # in the new word, and try crossing through them.
    # --------------------------------------------------------

    for existing_position, existing_letter in grid.items():

        existing_row, existing_col = existing_position

        for i, letter in enumerate(word):

            if letter != existing_letter:
                continue

            # ACROSS
            row = existing_row
            col = existing_col - i

            if can_place(word, row, col, "across", require_crossing=True):
                positions.append((row, col, "across"))

            # DOWN
            row = existing_row - i
            col = existing_col

            if can_place(word, row, col, "down", require_crossing=True):
                positions.append((row, col, "down"))

    positions = list(dict.fromkeys(positions))  # de-duplicate, keep order
    random.shuffle(positions)  # so re-running gives different layouts

    return positions


# ============================================================
# SOLVE THE CROSSWORD
# ============================================================

def solve(words):
    """
    Attempt to place every word in `words` into a single connected
    crossword grid.

    Returns True and leaves the result in `grid` / `word_positions`
    if successful. Returns False (and leaves grid/word_positions
    empty) if no layout could be found within MAX_ATTEMPTS total
    placement attempts.
    """

    global _attempts

    grid.clear()
    word_positions.clear()
    _attempts = 0

    if _solve(list(words), 0):
        return True

    grid.clear()
    word_positions.clear()
    return False


def _solve(words, index):

    global _attempts

    # All words have been placed successfully.
    if index >= len(words):
        return True

    word = words[index]
    positions = find_positions(word)

    for row, col, direction in positions:

        _attempts += 1
        if _attempts > MAX_ATTEMPTS:
            return False

        saved_state = save_grid()
        place_word(word, row, col, direction)

        if _solve(words, index + 1):
            return True

        # That arrangement didn't work - undo it and try the
        # next candidate position.
        restore_grid(saved_state)

    return False


# ============================================================
# GRID BOUNDS (for sizing the canvas)
# ============================================================

def get_grid_bounds():
    """Return (min_row, max_row, min_col, max_col) for the current grid."""

    rows = [position[0] for position in grid]
    cols = [position[1] for position in grid]

    return min(rows), max(rows), min(cols), max(cols)


# ============================================================
# CLUE NUMBERING
# ============================================================

def number_cells():
    """
    Number every cell that starts an across or down word, in
    standard crossword convention: scan the grid in reading order
    (top-to-bottom, then left-to-right) and assign the next number
    to each cell that begins at least one word.

    NOTE: this replaces the previous approach, which numbered
    cells in the order the solver happened to place words in -
    that could put "1 Across" somewhere other than the top-left
    of the grid. Numbering is now independent of placement order.
    """

    start_positions = {
        (info["row"], info["col"])
        for info in word_positions.values()
    }

    numbered_cells = {}

    for number, position in enumerate(sorted(start_positions), start=1):
        numbered_cells[position] = number

    return numbered_cells


def get_clues(dictionary):
    """
    Build the ACROSS and DOWN clue lists.

    dictionary -- {word: definition}, supplied by the caller since
                  crosswordgenerator only knows about grid layout,
                  not definitions.

    Returns (numbered_cells, across_clues, down_clues), where each
    clue list is [(number, word, definition), ...] sorted by number.
    """

    numbered_cells = number_cells()

    across_clues = []
    down_clues = []

    for word, info in word_positions.items():

        position = (info["row"], info["col"])
        number = numbered_cells[position]
        definition = dictionary[word]
        clue = (number, word, definition)

        if info["direction"] == "across":
            across_clues.append(clue)
        else:
            down_clues.append(clue)

    across_clues.sort(key=lambda clue: clue[0])
    down_clues.sort(key=lambda clue: clue[0])

    return numbered_cells, across_clues, down_clues