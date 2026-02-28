"""PDF text extraction using PyMuPDF."""

import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF


@dataclass
class Chapter:
    title: str
    content: str
    index: int


@dataclass
class BookData:
    title: str
    author: str
    chapters: list[Chapter] = field(default_factory=list)


# Regex to detect common chapter heading patterns
_CHAPTER_RE = re.compile(
    r"^(chapter|part|section|prologue|epilogue|introduction|conclusion)\b",
    re.IGNORECASE,
)


def extract_book(pdf_path: Path) -> BookData:
    """Open a PDF and return a BookData with metadata and detected chapters."""
    doc = fitz.open(str(pdf_path))
    try:
        title, author = _extract_metadata(doc, pdf_path)
        chapters = _extract_chapters(doc, title)
    finally:
        doc.close()

    return BookData(title=title, author=author, chapters=chapters)


def _extract_metadata(doc: fitz.Document, pdf_path: Path) -> tuple[str, str]:
    """Extract title and author from PDF metadata, falling back to sensible defaults."""
    meta = doc.metadata or {}
    title = (meta.get("title") or "").strip() or pdf_path.stem.replace("_", " ").title()
    author = (meta.get("author") or "").strip() or "Unknown"
    return title, author


def _detect_body_font_size(doc: fitz.Document) -> float:
    """Return the modal (most common) font size across the first 5 pages."""
    sizes: list[float] = []
    for page in doc[:5]:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
        for block in blocks:
            if block.get("type") != 0:  # type 0 = text
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = round(span.get("size", 0), 1)
                    if size > 0:
                        sizes.append(size)

    if not sizes:
        return 11.0

    # Return the mode (most frequent size) as the body font size
    try:
        return statistics.mode(sizes)
    except statistics.StatisticsError:
        return statistics.median(sizes)


def _blocks_to_paragraphs(blocks: list) -> str:
    """Convert PyMuPDF text blocks into paragraph-separated plain text."""
    paragraphs = []
    for block in blocks:
        if block.get("type") != 0:
            continue
        lines = []
        for line in block.get("lines", []):
            line_text = "".join(span["text"] for span in line.get("spans", []))
            # Remove soft hyphens at line ends (hyphenation artifacts)
            if line_text.endswith("-"):
                line_text = line_text[:-1]
            line_text = line_text.strip()
            if line_text:
                lines.append(line_text)
        paragraph = " ".join(lines).strip()
        if paragraph:
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


def _extract_chapters(doc: fitz.Document, book_title: str) -> list[Chapter]:
    """
    Detect chapter boundaries and split the document into Chapter objects.

    Detection strategy (in priority order):
    1. Regex match on common heading words (Chapter, Part, Section, etc.)
    2. Font size spike: block font > body_median * 1.4, text < 100 chars
    3. Fallback: whole document as a single chapter
    """
    body_size = _detect_body_font_size(doc)
    heading_threshold = body_size * 1.4

    chapters: list[Chapter] = []
    current_title: str | None = None
    current_blocks: list = []

    def _flush(title: str, blocks: list, idx: int) -> None:
        content = _blocks_to_paragraphs(blocks).strip()
        if content:
            chapters.append(Chapter(title=title, content=content, index=idx))

    chapter_idx = 0

    for page in doc:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]

        for block in blocks:
            if block.get("type") != 0:
                continue

            # Gather block text and max font size
            block_spans = [
                span
                for line in block.get("lines", [])
                for span in line.get("spans", [])
            ]
            if not block_spans:
                continue

            block_text = " ".join(s["text"] for s in block_spans).strip()
            if not block_text:
                continue

            max_size = max(s.get("size", 0) for s in block_spans)
            is_heading = (
                # Regex-based heading
                bool(_CHAPTER_RE.match(block_text))
                # Font-size-based heading: large font, short text
                or (max_size >= heading_threshold and len(block_text) < 100)
            )

            if is_heading:
                # Save previous chapter
                if current_title is not None:
                    _flush(current_title, current_blocks, chapter_idx)
                    chapter_idx += 1
                current_title = block_text
                current_blocks = []
            else:
                current_blocks.append(block)

    # Flush final chapter
    if current_title is not None:
        _flush(current_title, current_blocks, chapter_idx)
    elif current_blocks:
        # No headings at all — treat entire doc as one chapter
        content = _blocks_to_paragraphs(current_blocks).strip()
        if content:
            chapters.append(Chapter(title=book_title, content=content, index=0))

    # Edge case: headings detected but all had empty bodies (scanned/image PDF)
    if not chapters:
        all_blocks = [
            block
            for page in doc
            for block in page.get_text("dict")["blocks"]
            if block.get("type") == 0
        ]
        content = _blocks_to_paragraphs(all_blocks).strip()
        chapters.append(Chapter(title=book_title, content=content or "(No text extracted)", index=0))

    return chapters
