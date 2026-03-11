import os

MODELS_DIR = "models"


def run(args):

    if not args:
        print("Wrong argument.")
        print("Usage: conduit remove <model>")
        return

    if not os.path.exists(MODELS_DIR):
        print("Models directory not found.")
        return

    model = args[0]

    models = os.listdir(MODELS_DIR)
    clean_models = {os.path.splitext(m)[0]: m for m in models}

    if model in clean_models:

        file = clean_models[model]

        ch = input(f"Delete model {model}? (y/n): ").strip().lower()

        if ch == "y":
            os.remove(os.path.join(MODELS_DIR, file))
            print(f"Removed model: {model}")
        else:
            print("Cancelled")

    else:
        print("Unknown model.")
