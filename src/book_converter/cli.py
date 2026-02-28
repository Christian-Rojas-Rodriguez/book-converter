"""CLI interface for book-converter using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from .converter import build_epub
from .extractor import extract_book
from .utils import detect_output_path

app = typer.Typer(
    name="book-converter",
    help="Convert PDF books to EPUB format for Kindle reading.",
    add_completion=False,
)
console = Console()


@app.command()
def convert(
    input_pdf: Path = typer.Argument(
        ...,
        help="Path to the input PDF file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output EPUB path. Defaults to same directory as input with .epub extension.",
    ),
) -> None:
    """Convert a single PDF file to EPUB."""
    output_path = detect_output_path(input_pdf, output)
    _convert_single(input_pdf, output_path)


@app.command()
def batch(
    directory: Path = typer.Argument(
        ...,
        help="Directory containing PDF files to convert.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-d",
        help="Directory for output EPUB files. Defaults to same directory as PDFs.",
    ),
) -> None:
    """Batch convert all PDF files in a directory to EPUB."""
    pdf_files = sorted(directory.glob("*.pdf"))

    if not pdf_files:
        console.print(f"[yellow]No PDF files found in {directory}[/]")
        raise typer.Exit(code=0)

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    total = len(pdf_files)
    console.print(f"Found [bold]{total}[/] PDF file(s) to convert.")

    failed = 0
    for i, pdf_path in enumerate(pdf_files, 1):
        console.print(f"\n[dim][{i}/{total}][/] {pdf_path.name}")
        output_path = detect_output_path(pdf_path, output_dir)
        try:
            _convert_single(pdf_path, output_path)
        except Exception as exc:  # noqa: BLE001
            console.print(f"  [red]Failed:[/] {exc}")
            failed += 1

    console.print()
    if failed:
        console.print(f"[red]Completed with {failed} error(s).[/]")
        raise typer.Exit(code=1)
    else:
        console.print(f"[green]All {total} file(s) converted successfully.[/]")


def _convert_single(pdf_path: Path, output_path: Path) -> None:
    """Extract and convert a single PDF, showing a rich progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Extracting [cyan]{pdf_path.name}[/]...", total=100)

        book_data = extract_book(pdf_path)
        progress.update(task, completed=50, description=f"Building EPUB [cyan]{output_path.name}[/]...")

        # Warn if no chapters were detected (fallback mode)
        if len(book_data.chapters) == 1 and book_data.chapters[0].title == book_data.title:
            progress.stop()
            console.print(
                f"  [yellow]Warning:[/] No chapters detected in [cyan]{pdf_path.name}[/]"
                " — treating as single document."
            )
            progress.start()

        build_epub(book_data, output_path)
        progress.update(task, completed=100, description="Done")

    console.print(
        f"  [green]✓[/] Saved to [bold]{output_path}[/]"
        f"  ([dim]{len(book_data.chapters)} chapter(s)[/])"
    )
