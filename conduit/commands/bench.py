import time
from conduit.runtime.inference import Engine
from rich.console import Console
from rich.table import Table

console = Console()

PROMPT = "Explain how neural networks work in simple terms."

def run(args):
    if not args:
        console.print("[red] Oops! [/red]")
        return
    
    console.print("[bold cyan]Starting model benchmark...[/bold cyan]\n")

    start_load = time.time()

            
    engine = Engine(args[0])
    load_time = time.time() - start_load

    console.print(f"[green]Model load time:[/green] {load_time:.3f}s")

    tokens = 0
    first_token_time = None

    start = time.time()

    for token in engine.generate(PROMPT):

        if tokens == 0:
            first_token_time = time.time()

        tokens += 1

    end = time.time()

    total_time = end - start
    first_token_latency = first_token_time - start
    tps = tokens / total_time if total_time > 0 else 0

    table = Table(title="Benchmark Results")

    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("First Token Latency", f"{first_token_latency:.3f}s")
    table.add_row("Total Generation Time", f"{total_time:.3f}s")
    table.add_row("Tokens Generated", str(tokens))
    table.add_row("Tokens/sec", f"{tps:.2f}")

    console.print()
    console.print(table)
