import os
import datetime
from conduit.commands.path import get_path

MODELS_DIR = get_path()


def get_modified(path):
    ts = os.path.getmtime(path)
    now = datetime.datetime.now()
    diff = now - datetime.datetime.fromtimestamp(ts)

    seconds = diff.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    if seconds < 3600:
        return f"{int(seconds // 60)} min ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)} hour ago"
    if seconds < 604800:
        return f"{int(seconds // 86400)} days ago"

    return f"{int(seconds // 604800)} weeks ago"


def get_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)

    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total


def human_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def run(args):

    if not os.path.exists(MODELS_DIR):
        print("No models directory found.")
        return

    models = os.listdir(MODELS_DIR)

    if not models:
        print("No models installed.")
        return

    print(f"{'NAME':40} {'SIZE':>10} {'MODIFIED':>17}")

    for m in models:
        if m.endswith(".gguf"):
            path = os.path.join(MODELS_DIR, m)
            size = human_size(get_size(path))
            modified = get_modified(path)
            m = m.replace(".gguf","")
            print(f"{m:40} {size:>10} {modified:>17}")

    print()
