"""crosswordcanvas.py

Draws a generated crossword onto window: the letter
grid on the left, and an ACROSS/DOWN clue panel on the right."""

import tkinter as tk

PANEL_WIDTH = 300
PADDING = 1  # extra empty border around the grid, in cells


class CrosswordCanvas:

    def __init__(self, grid, bounds, numbered_cells, across_clues,
                 down_clues, cell_size, font_size):
        """
        grid            -- {(row, col): letter}, from crosswordgenerator
        bounds          -- (min_row, max_row, min_col, max_col)
        numbered_cells  -- {(row, col): clue_number}
        across_clues    -- [(number, word, definition), ...]
        down_clues      -- [(number, word, definition), ...]
        cell_size       -- pixel size of each grid square
        font_size       -- font size for letters drawn in the grid
        """

        self.grid = grid
        self.min_row, self.max_row, self.min_col, self.max_col = bounds
        self.numbered_cells = numbered_cells
        self.across_clues = across_clues
        self.down_clues = down_clues
        self.cell_size = cell_size
        self.font_size = font_size

        self.display_rows = self.max_row - self.min_row + 1 + PADDING * 2
        self.display_cols = self.max_col - self.min_col + 1 + PADDING * 2

        self.window = tk.Tk()
        self.window.title("Crossword")

        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack()

        self._build_grid_canvas()
        self._build_definition_panel()

    # ============================================================
    # GRID CANVAS
    # ============================================================

    def _build_grid_canvas(self):

        canvas_width = self.display_cols * self.cell_size
        canvas_height = self.display_rows * self.cell_size

        self.canvas = tk.Canvas(
            self.main_frame,
            width=canvas_width,
            height=canvas_height,
            background="black",
            highlightthickness=0
        )
        self.canvas.pack(side="left")

        for row in range(self.min_row - PADDING, self.max_row + PADDING + 1):
            for col in range(self.min_col - PADDING, self.max_col + PADDING + 1):
                self._draw_cell(row, col)

    def _draw_cell(self, row, col):

        x = (col - self.min_col + PADDING) * self.cell_size
        y = (row - self.min_row + PADDING) * self.cell_size

        if (row, col) in self.grid:
            self._draw_letter_cell(row, col, x, y)
        else:
            self._draw_empty_cell(x, y)

    def _draw_letter_cell(self, row, col, x, y):

        self.canvas.create_rectangle(
            x, y, x + self.cell_size, y + self.cell_size,
            fill="white", outline="black"
        )

        # Small clue number in the corner, if this cell starts a word.
        if (row, col) in self.numbered_cells:
            self.canvas.create_text(
                x + 4, y + 3,
                text=str(self.numbered_cells[(row, col)]),
                anchor="nw",
                font=("Helvetica", 9),
                fill="black"
            )

        self.canvas.create_text(
            x + self.cell_size / 2, y + self.cell_size / 2 + 3,
            text=self.grid[(row, col)],
            font=("Helvetica", self.font_size),
            fill="black"
        )

    def _draw_empty_cell(self, x, y):

        self.canvas.create_rectangle(
            x, y, x + self.cell_size, y + self.cell_size,
            fill="black", outline="black"
        )

    # ============================================================
    # DEFINITION PANEL
    # ============================================================

    def _build_definition_panel(self):

        self.definition_frame = tk.Frame(
            self.main_frame,
            width=PANEL_WIDTH,
            height=self.display_rows * self.cell_size,
            bg="white"
        )
        self.definition_frame.pack(side="right", fill="y")
        self.definition_frame.pack_propagate(False)

        title = tk.Label(
            self.definition_frame,
            text="CLUES",
            font=("Helvetica", 18, "bold"),
            bg="white",
            fg="black"
        )
        title.pack(pady=(15, 10))

        self._build_clue_section("ACROSS", self.across_clues)
        self._add_separator()
        self._build_clue_section("DOWN", self.down_clues)

    def _build_clue_section(self, heading_text, clues):

        heading = tk.Label(
            self.definition_frame,
            text=heading_text,
            font=("Helvetica", 13, "bold"),
            bg="white",
            fg="black",
            anchor="w"
        )
        heading.pack(fill="x", padx=15, pady=(5, 5))

        for number, word, definition in clues:
            self._build_clue_row(number, definition)

    def _build_clue_row(self, number, definition):

        clue_frame = tk.Frame(self.definition_frame, bg="white")
        clue_frame.pack(fill="x", padx=15, pady=4)

        number_label = tk.Label(
            clue_frame,
            text=f"{number}.",
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="black",
            width=4,
            anchor="nw"
        )
        number_label.pack(side="left")

        definition_label = tk.Label(
            clue_frame,
            text=definition,
            font=("Helvetica", 11),
            bg="white",
            fg="black",
            justify="left",
            anchor="nw",
            wraplength=PANEL_WIDTH - 60
        )
        definition_label.pack(side="left", fill="x", expand=True)

    def _add_separator(self):

        separator = tk.Frame(self.definition_frame, height=2, bg="black")
        separator.pack(fill="x", padx=15, pady=12)

    # ============================================================
    # RUN
    # ============================================================

    def run(self):
        self.window.mainloop()