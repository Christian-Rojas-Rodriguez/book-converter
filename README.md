# Book Converter

PDF to EPUB converter for Kindle reading.

## Objectives
- Convert PDF books to EPUB format
- Preserve text formatting and structure
- Optimize output for Kindle devices
- Support batch conversion of multiple files

## Installation

```bash
git clone https://github.com/Christian-Rojas-Rodriguez/book-converter
cd book-converter
uv sync
```

## Usage

```bash
# Convert a single file
uv run book-converter convert book.pdf
uv run book-converter convert book.pdf --output my-book.epub

# Batch convert all PDFs in a directory
uv run book-converter batch ./pdf-folder/
uv run book-converter batch ./pdf-folder/ --output-dir ./epub-folder/
```

## Development

```bash
uv sync --dev
uv run pytest
uv run pytest --cov=book_converter --cov-report=term-missing
```

## Tech Stack
- Python 3.12
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text extraction
- [ebooklib](https://github.com/aerkalov/ebooklib) — EPUB generation
- [Typer](https://typer.tiangolo.com/) — CLI framework
- [Rich](https://rich.readthedocs.io/) — terminal output

## Roadmap
- [x] Project setup and dependencies
- [ ] PDF text extraction
- [ ] EPUB generation
- [ ] CLI interface
- [ ] Batch processing

## Branching Strategy
- `main` — stable, production-ready code
- `feature/*` — individual features, merged to main via PR
