"""Tests for the EPUB converter module."""

import zipfile
from pathlib import Path

import pytest
from book_converter.converter import build_epub, _text_to_html


def test_epub_created(sample_book_data, tmp_path):
    out = tmp_path / "output.epub"
    build_epub(sample_book_data, out)
    assert out.exists()


def test_epub_is_valid_zip(sample_book_data, tmp_path):
    out = tmp_path / "output.epub"
    build_epub(sample_book_data, out)
    assert zipfile.is_zipfile(out)


def test_epub_has_content_opf(sample_book_data, tmp_path):
    out = tmp_path / "output.epub"
    build_epub(sample_book_data, out)
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    assert any("content.opf" in n for n in names)


def test_epub_has_toc(sample_book_data, tmp_path):
    out = tmp_path / "output.epub"
    build_epub(sample_book_data, out)
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    assert any("toc.ncx" in n or "nav" in n for n in names)


def test_epub_chapter_count(sample_book_data, tmp_path):
    out = tmp_path / "output.epub"
    build_epub(sample_book_data, out)
    with zipfile.ZipFile(out) as z:
        xhtml_files = [n for n in z.namelist() if n.endswith(".xhtml") and "chapter" in n]
    assert len(xhtml_files) == len(sample_book_data.chapters)


def test_epub_chapter_filenames(sample_book_data, tmp_path):
    out = tmp_path / "output.epub"
    build_epub(sample_book_data, out)
    with zipfile.ZipFile(out) as z:
        names = z.namelist()
    assert any("chapter_000.xhtml" in n for n in names)
    assert any("chapter_001.xhtml" in n for n in names)


def test_text_to_html_structure():
    xhtml = _text_to_html("First paragraph.\n\nSecond paragraph.", "Test Title")
    assert "<h1>Test Title</h1>" in xhtml
    assert "<p>First paragraph.</p>" in xhtml
    assert "<p>Second paragraph.</p>" in xhtml


def test_text_to_html_escapes_special_chars():
    xhtml = _text_to_html("Text with <b> & special chars.", "Title & More")
    assert "&lt;b&gt;" in xhtml
    assert "&amp;" in xhtml


def test_single_chapter_epub(tmp_path):
    """A BookData with one chapter produces a valid single-chapter EPUB."""
    from book_converter.extractor import BookData, Chapter

    book_data = BookData(
        title="Single Chapter Book",
        author="Author Name",
        chapters=[Chapter(title="Only Chapter", content="Just some text.", index=0)],
    )
    out = tmp_path / "single.epub"
    build_epub(book_data, out)
    assert zipfile.is_zipfile(out)
