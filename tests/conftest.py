"""Shared test fixtures."""

import pytest
from pathlib import Path

import fitz  # PyMuPDF


@pytest.fixture(scope="session")
def sample_pdf_path(tmp_path_factory) -> Path:
    """
    Programmatically create a minimal two-chapter PDF for testing.
    Avoids committing binary files to the repository.
    """
    tmp = tmp_path_factory.mktemp("pdfs")
    pdf_path = tmp / "sample.pdf"

    doc = fitz.open()

    # Page 1: Chapter 1 heading
    page = doc.new_page()
    page.insert_text((72, 72), "Chapter 1: Introduction", fontsize=18)
    page.insert_text((72, 120), "This is the first paragraph of the introduction.", fontsize=11)
    page.insert_text((72, 150), "It contains multiple sentences for testing purposes.", fontsize=11)

    # Page 2: Chapter 2 heading + body
    page = doc.new_page()
    page.insert_text((72, 72), "Chapter 2: Methods", fontsize=18)
    page.insert_text((72, 120), "This chapter describes the methodology used.", fontsize=11)
    page.insert_text((72, 150), "Several techniques were applied throughout the study.", fontsize=11)

    doc.set_metadata({"title": "Test Book", "author": "Test Author"})
    doc.save(str(pdf_path))
    doc.close()

    return pdf_path


@pytest.fixture(scope="session")
def flat_pdf_path(tmp_path_factory) -> Path:
    """A PDF with no detectable chapter headings (all same font size)."""
    tmp = tmp_path_factory.mktemp("pdfs")
    pdf_path = tmp / "flat.pdf"

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This is a flat document with no headings.", fontsize=11)
    page.insert_text((72, 100), "All text is the same font size throughout.", fontsize=11)
    doc.save(str(pdf_path))
    doc.close()

    return pdf_path


@pytest.fixture
def sample_book_data():
    """Pre-built BookData for converter/cli tests — no PDF required."""
    from book_converter.extractor import BookData, Chapter

    return BookData(
        title="Test Book",
        author="Test Author",
        chapters=[
            Chapter(
                title="Chapter 1: Introduction",
                content="First chapter body.\n\nSecond paragraph of the introduction.",
                index=0,
            ),
            Chapter(
                title="Chapter 2: Methods",
                content="Second chapter body.\n\nMore details about the methodology.",
                index=1,
            ),
        ],
    )
