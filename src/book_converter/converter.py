"""EPUB generation using ebooklib."""

import html
import uuid
import warnings
from pathlib import Path

# ebooklib triggers a Python 3.12 deprecation warning for the removed `cgi` module
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from ebooklib import epub

from .extractor import BookData, Chapter
from .utils import slugify


def build_epub(book_data: BookData, output_path: Path) -> None:
    """Convert a BookData object to an EPUB file at output_path."""
    book = _create_epub_book(book_data)

    epub_items: list[epub.EpubHtml] = []
    for chapter in book_data.chapters:
        item = _chapter_to_epub_item(chapter)
        book.add_item(item)
        epub_items.append(item)

    book.toc = _build_toc(book_data.chapters, epub_items)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + epub_items

    epub.write_epub(str(output_path), book)


def _create_epub_book(book_data: BookData) -> epub.EpubBook:
    """Create and configure an EpubBook with metadata."""
    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(book_data.title)
    book.set_language("en")
    book.add_author(book_data.author)
    return book


def _chapter_to_epub_item(chapter: Chapter) -> epub.EpubHtml:
    """Convert a Chapter to an EpubHtml item."""
    slug = slugify(chapter.title) or f"chapter-{chapter.index}"
    filename = f"chapter_{chapter.index:03d}.xhtml"
    xhtml = _text_to_html(chapter.content, chapter.title)

    item = epub.EpubHtml(
        title=chapter.title,
        file_name=filename,
        lang="en",
    )
    item.content = xhtml.encode("utf-8")
    return item


def _text_to_html(text: str, title: str) -> str:
    """Convert plain text to a valid XHTML document."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    escaped_title = html.escape(title)
    para_tags = "\n".join(f"    <p>{html.escape(p)}</p>" for p in paragraphs)

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
  <head>
    <title>{escaped_title}</title>
  </head>
  <body>
    <h1>{escaped_title}</h1>
{para_tags}
  </body>
</html>"""


def _build_toc(
    chapters: list[Chapter], epub_items: list[epub.EpubHtml]
) -> list[epub.Link]:
    """Create TOC entries linking chapter titles to their EPUB items."""
    return [
        epub.Link(item.file_name, chapter.title, f"chapter-{chapter.index}")
        for chapter, item in zip(chapters, epub_items)
    ]
