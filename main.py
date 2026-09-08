# Importing json and the path finder
import json
from pathlib import Path


# Folder containing the JSON files
DATABASE_FOLDER = Path("Database")


# For loop to read every JSON file in the folder
for json_file in DATABASE_FOLDER.glob("*.json"):

    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Print each word and definition
    for entry in data:
        word = entry["word"]
        definition = entry["definition"]

        print(f"{word:<20} | {definition}")
