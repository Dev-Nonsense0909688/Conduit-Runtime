commands = {
    "run": ["Chat with model", "conduit run <model>"],
    "pull": ["Install model", "conduit pull <repo>"],
    "ls": ["List models", "conduit ls"],
    "remove": ["Remove model", "conduit remove <model>"],
    "bench": ["Benchmark a model", "conduit bench <model>"],
}


def run(args):
    print(f"{'NAME':<10} {'DESC':<20} {'USAGE'}")
    for cmd, help_text in commands.items():
        desc, usage = help_text
        print(f"{cmd:<10} {desc:<20} {usage}")
    print()