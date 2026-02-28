"""Tests for the PDF extractor module."""

import pytest
from pathlib import Path
from book_converter.extractor import extract_book, BookData, Chapter


def test_extract_metadata(sample_pdf_path):
    book = extract_book(sample_pdf_path)
    assert book.title == "Test Book"
    assert book.author == "Test Author"


def test_returns_book_data(sample_pdf_path):
    book = extract_book(sample_pdf_path)
    assert isinstance(book, BookData)


def test_chapter_detection(sample_pdf_path):
    book = extract_book(sample_pdf_path)
    assert len(book.chapters) >= 1
    titles = [ch.title for ch in book.chapters]
    assert any("Chapter" in t or "Introduction" in t for t in titles)


def test_chapter_content_not_empty(sample_pdf_path):
    book = extract_book(sample_pdf_path)
    for chapter in book.chapters:
        assert chapter.content.strip(), f"Chapter '{chapter.title}' has empty content"


def test_chapter_indices_are_sequential(sample_pdf_path):
    book = extract_book(sample_pdf_path)
    for i, chapter in enumerate(book.chapters):
        assert chapter.index == i


def test_fallback_for_flat_pdf(flat_pdf_path):
    """A PDF with no headings should still return exactly one chapter."""
    book = extract_book(flat_pdf_path)
    assert len(book.chapters) == 1
    assert book.chapters[0].content.strip()


def test_metadata_fallback(tmp_path):
    """PDF with no metadata falls back to filename stem for title."""
    import fitz

    pdf_path = tmp_path / "my_cool_book.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Some text without metadata.", fontsize=11)
    doc.save(str(pdf_path))
    doc.close()

    book = extract_book(pdf_path)
    assert book.title == "My Cool Book"
    assert book.author == "Unknown"
