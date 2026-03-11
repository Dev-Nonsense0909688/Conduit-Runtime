import sys
import importlib
import conduit.commands.help as help

sys.dont_write_bytecode = True

COMMAND_PACKAGE = "conduit.commands"


def run_command(cmd, args):
    try:
        module = importlib.import_module(f"{COMMAND_PACKAGE}.{cmd}")
    except ModuleNotFoundError as e:
        print(e)
        print("Unknown")
        return

    if not hasattr(module, "run"):
        print(f"{cmd} has no run() function")
        return

    module.run(args)


def main():
    if len(sys.argv) < 2:
        
        help.run("")
    
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    run_command(cmd, args)


if __name__ == "__main__":
    main()
