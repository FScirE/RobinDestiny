import os
import json
from datetime import datetime, timezone

class Colors:
    WHITE = "\033[00m"
    PURPLE = "\033[95m"
    GRAY = "\033[90m"

def write_data_file(data: object, filepath: str) -> None:
    """
    Write json data to file, path must include folder
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def read_data_file(filepath: str) -> object:
    """
    Read data from json file
    """
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        return None
    else:
        return data

def timestamp_print(text: str) -> None:
    """
    Prints text with timestamp
    """
    now = datetime.now(timezone.utc)
    isotime = now.isoformat(timespec="seconds").split("+")[0]
    print(
        f"{Colors.GRAY}@(UTC){isotime} " +
        f"{Colors.PURPLE}|RD| " +
        f"{Colors.WHITE}{text}"
    )
