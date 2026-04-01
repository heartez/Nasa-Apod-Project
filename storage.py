import os
import json
from config import FAVORITES_FILE


def save_text_file(filename, title, date, explanation, media_type, media_url, copyright_text):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Título: {title}\n")
        file.write(f"Data: {date}\n")
        file.write(f"Tipo: {media_type}\n")
        file.write(f"URL: {media_url}\n")
        file.write(f"Copyright: {copyright_text}\n\n")
        file.write("Descrição:\n")
        file.write(explanation)


def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return []

    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
        json.dump(favorites, file, indent=4, ensure_ascii=False)


def is_favorite_already_saved(favorites, date):
    for item in favorites:
        if item.get("date") == date:
            return True
    return False