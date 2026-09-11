import json
import random
from pathlib import Path

import crosswordgenerator
from crosswordcanvas import CrosswordCanvas

DATABASE_FOLDER = Path("Database")

# Space left for future random sampling of a subset of words.
# For now, ALL words found in Database/ are used - None means
# "no sampling". Set this to an int later to pick a random subset.
NUMBER_OF_WORDS = None


# ============================================================
# LOAD WORDS AND DEFINITIONS
# ============================================================

def load_dictionary():
    """Read JSON files in Database and return 20 random words."""

    dictionary = {}

    for json_file in DATABASE_FOLDER.glob("*.json"):

        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        for entry in data:
            dictionary[entry["word"]] = entry["definition"]

    # Pick 20 random words
    if len(dictionary) > 10:
        dictionary = dict(random.sample(list(dictionary.items()), 10))

    return dictionary


def choose_words(dictionary, number_of_words):

    """ Return the list of words to build the crossword from.

    Currently uses every word in `dictionary`. Pass an integer for
    number_of_words to randomly sample a subset instead of using all words."""

    words = list(dictionary.keys())

    if number_of_words is not None:
        words = random.sample(words, number_of_words)

    return words


# ============================================================
# MAIN
# ============================================================

def main():

    dictionary = load_dictionary()
    words = choose_words(dictionary, NUMBER_OF_WORDS)

    if not crosswordgenerator.solve(words):
        print(
            f"Could not fit all {len(words)} words into a crossword "
            f"within {crosswordgenerator.MAX_ATTEMPTS} placement "
            "attempts. Try fewer words, or run again for a "
            "different random layout."
        )
        return

    bounds = crosswordgenerator.get_grid_bounds()
    numbered_cells, across_clues, down_clues = crosswordgenerator.get_clues(dictionary)

    canvas = CrosswordCanvas(
        grid=crosswordgenerator.grid,
        bounds=bounds,
        numbered_cells=numbered_cells,
        across_clues=across_clues,
        down_clues=down_clues,
        cell_size=crosswordgenerator.CELL_SIZE,
        font_size=crosswordgenerator.FONT_SIZE,
    )
    canvas.run()


if __name__ == "__main__":
    main()
