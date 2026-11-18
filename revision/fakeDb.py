import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("fake_db.json")


def load_fake_db() -> dict:
    if not DATA_FILE.exists():
        return {}

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_fake_db(data: dict) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


fake_db = load_fake_db()


DEFAULT_TEXT_FILE = Path(__file__).with_name("data.txt")


def txt_halper(data: str, file_path: str | None = None) -> str:
    p = Path(file_path) if file_path else DEFAULT_TEXT_FILE
    with p.open("a", encoding="utf-8") as file:
        file.write(data + "\n")
    return "added data successfully"

def get_txt_file(file_path: str | None = None) -> list[str]:
    p = Path(file_path) if file_path else DEFAULT_TEXT_FILE
    if not p.exists():
        return []

    with p.open("r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]

txt_file = get_txt_file()