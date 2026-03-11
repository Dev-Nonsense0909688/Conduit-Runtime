from conduit.runtime.inference import Engine
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner

console = Console()


def run(args):
    if not args:
        console.print("[red] Oops! [/red]")
        return

    model = args[0]
    engine = Engine(model)

    try:
        while True:

            inp = console.input("[bold cyan]>>> [/bold cyan]")
            prompt = inp

            response = ""
            spinner = Spinner("dots", text="Thinking...")

            with Live(spinner, console=console, refresh_per_second=20) as live:
                first_token = True

                try:
                    for token in engine.generate(prompt):

                        if first_token:
                            first_token = False
                            live.update(Markdown(""))

                        response += token
                        live.update(Markdown(response))

                except KeyboardInterrupt:
                    continue

    except KeyboardInterrupt:
        console.print("\n[yellow]bye.[/yellow]")
