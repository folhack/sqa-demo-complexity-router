"""Terminal panels rendered with rich."""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def verdict_text(approved):
    if approved:
        return Text("APROVADA", style="bold green")
    return Text("NÃO VALIDADA", style="bold red")


def summary_table(summary):
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column()
    table.add_row("Pergunta", Text(summary["question"]))
    table.add_row("Rota inicial", Text(summary["initial_tier"]))
    table.add_row("Rota final", Text(summary["final_tier"]))
    table.add_row("Caminho", Text(" > ".join(summary["path"])))
    table.add_row("Modelos", Text(", ".join(summary["models"])))
    table.add_row("Tentativas", Text(str(summary["attempts"])))
    table.add_row("Tokens", Text(str(summary["tokens"])))
    table.add_row("Custo estimado (USD)", Text("%.6f" % summary["cost"]))
    table.add_row("Nota do juiz", Text(str(summary["score"])))
    table.add_row("Cache", Text("sim" if summary["cached"] else "não"))
    table.add_row("Veredito", verdict_text(summary["approved"]))
    table.add_row("Problemas", Text("\n".join(summary["issues"]) or "nenhum"))
    return table


def render(summary, console):
    console.print(Panel(summary_table(summary), title="Roteamento", expand=False))
    console.print(Panel(Text(summary["answer"]), title="Resposta"))


def batch_row(question, expected, initial, final, attempts, score, approved):
    return (
        Text(question),
        expected,
        initial,
        final,
        str(attempts),
        str(score),
        verdict_text(approved),
    )


def render_batch(rows, console):
    table = Table(title="Resumo do lote")
    table.add_column("Pergunta", max_width=48, no_wrap=True, overflow="ellipsis")
    for header in ("Esperada", "Inicial", "Final", "Tentativas", "Nota", "Veredito"):
        table.add_column(header)
    for expected, s in rows:
        table.add_row(
            *batch_row(
                s["question"],
                expected,
                s["initial_tier"],
                s["final_tier"],
                s["attempts"],
                s["score"],
                s["approved"],
            )
        )
    console.print(table)
