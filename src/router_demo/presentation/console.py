"""Terminal panels rendered with rich."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

APPROVED = "APROVADA"
NOT_VALIDATED = "NÃO VALIDADA"


def verdict_text(summary: dict) -> Text:
    if summary["approved"]:
        return Text(APPROVED, style="bold green")
    return Text(NOT_VALIDATED, style="bold red")


def summary_table(summary: dict) -> Table:
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column()
    rows = [
        ("Pergunta", summary["question"]),
        ("Rota inicial", summary["initial_tier"]),
        ("Rota final", summary["final_tier"]),
        ("Caminho", " > ".join(summary["path"])),
        ("Modelos", ", ".join(summary["models"])),
        ("Tentativas", str(summary["attempts"])),
        ("Tokens", str(summary["tokens"])),
        ("Custo estimado (USD)", f"{summary['cost']:.6f}"),
        ("Nota do juiz", str(summary["score"])),
        ("Cache", "sim" if summary["cached"] else "não"),
    ]
    for label, value in rows:
        table.add_row(label, Text(value))
    table.add_row("Veredito", verdict_text(summary))
    table.add_row("Problemas", Text("\n".join(summary["issues"]) or "nenhum"))
    return table


def render(summary: dict, console: Console) -> None:
    console.print(Panel(summary_table(summary), title="Roteamento", expand=False))
    console.print(Panel(Text(summary["answer"]), title="Resposta"))


def render_batch(rows: list[tuple[str, dict]], console: Console) -> None:
    table = Table(title="Resumo do lote")
    table.add_column("Pergunta", max_width=48, no_wrap=True, overflow="ellipsis")
    for header in ("Esperada", "Inicial", "Final", "Tentativas", "Nota", "Veredito"):
        table.add_column(header)
    for expected, summary in rows:
        table.add_row(
            Text(summary["question"]),
            expected,
            summary["initial_tier"],
            summary["final_tier"],
            str(summary["attempts"]),
            str(summary["score"]),
            verdict_text(summary),
        )
    console.print(table)
