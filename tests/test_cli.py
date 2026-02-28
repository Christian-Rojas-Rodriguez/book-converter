"""Tests for the CLI interface."""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from book_converter.cli import app

runner = CliRunner()


def test_convert_success(sample_pdf_path, tmp_path):
    out = tmp_path / "result.epub"
    result = runner.invoke(app, ["convert", str(sample_pdf_path), "--output", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_convert_default_output(sample_pdf_path, tmp_path):
    """Without --output, EPUB is placed next to the PDF."""
    pdf_copy = tmp_path / "sample.pdf"
    shutil.copy(sample_pdf_path, pdf_copy)
    result = runner.invoke(app, ["convert", str(pdf_copy)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "sample.epub").exists()


def test_convert_missing_file():
    result = runner.invoke(app, ["convert", "/nonexistent/file.pdf"])
    assert result.exit_code != 0


def test_convert_short_flag(sample_pdf_path, tmp_path):
    out = tmp_path / "result.epub"
    result = runner.invoke(app, ["convert", str(sample_pdf_path), "-o", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_batch_success(sample_pdf_path, tmp_path):
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    shutil.copy(sample_pdf_path, pdf_dir / "book1.pdf")
    shutil.copy(sample_pdf_path, pdf_dir / "book2.pdf")

    out_dir = tmp_path / "epubs"
    result = runner.invoke(app, ["batch", str(pdf_dir), "--output-dir", str(out_dir)])
    assert result.exit_code == 0, result.output

    epub_files = list(out_dir.glob("*.epub"))
    assert len(epub_files) == 2


def test_batch_no_pdfs(tmp_path):
    """Empty directory exits cleanly with code 0."""
    result = runner.invoke(app, ["batch", str(tmp_path)])
    assert result.exit_code == 0
    assert "No PDF files found" in result.output


def test_batch_default_output_dir(sample_pdf_path, tmp_path):
    """Without --output-dir, EPUBs land in the same directory as the PDFs."""
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    shutil.copy(sample_pdf_path, pdf_dir / "book.pdf")

    result = runner.invoke(app, ["batch", str(pdf_dir)])
    assert result.exit_code == 0, result.output
    assert (pdf_dir / "book.epub").exists()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "convert" in result.output
    assert "batch" in result.output
