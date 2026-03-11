import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".conduit"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_path():
    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text())
        return Path(data.get("models", CONFIG_DIR / "models"))
    return CONFIG_DIR / "models"


def set_path(new_path):
    CONFIG_DIR.mkdir(exist_ok=True)

    data = {"models": str(Path(new_path).expanduser())}

    CONFIG_FILE.write_text(json.dumps(data, indent=2))

    print("Models path updated to:", data["models"])


def run(args):

    if args:
        set_path(args[0])
        return

    path = get_path()
    print(path)
