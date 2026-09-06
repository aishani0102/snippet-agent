"""
main.py
--------
Command-line interface for the Code Snippet Generator Agent.

Usage:
    python build_index.py     # one-time setup: builds the RAG vector index
    python main.py            # start chatting

Type 'exit', 'quit', or Ctrl+C to stop.
Type 'reset' to clear the conversation and start a new session.
Type 'sources' to see which knowledge base chunks were used for the last reply.
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from rag_agent import CodeSnippetAgent

console = Console()


def main():
    console.print(
        Panel.fit(
            "[bold cyan]Code Snippet Generator Agent[/bold cyan]\n"
            "Describe what you need in plain English. Ask follow-ups to refine.\n"
            "Commands: 'reset' | 'sources' | 'exit'",
            border_style="cyan",
        )
    )

    try:
        agent = CodeSnippetAgent()
    except Exception as e:
        console.print(f"[bold red]Startup error:[/bold red] {e}")
        return

    while True:
        try:
            user_input = console.input("\n[bold green]You:[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            console.print("[yellow]Goodbye![/yellow]")
            break
        if user_input.lower() == "reset":
            agent.reset()
            console.print("[yellow]Conversation reset.[/yellow]")
            continue
        if user_input.lower() == "sources":
            if agent.last_retrieved:
                console.print(Panel("\n\n".join(agent.last_retrieved), title="Retrieved context", border_style="magenta"))
            else:
                console.print("[yellow]No retrieval has happened yet.[/yellow]")
            continue

        with console.status("[cyan]Thinking...[/cyan]"):
            try:
                reply = agent.ask(user_input)
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}")
                continue

        console.print("\n[bold blue]Agent:[/bold blue]")
        console.print(Markdown(reply))


if __name__ == "__main__":
    main()
