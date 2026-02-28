import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Remove characters invalid in filenames."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip()


def slugify(text: str) -> str:
    """Convert text to a safe HTML anchor/filename fragment."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def detect_output_path(input_path: Path, output: Path | None) -> Path:
    """
    Resolve the output .epub path.
    If output is None, place the EPUB next to the input PDF.
    If output is a directory, place the EPUB inside it with the PDF's stem.
    """
    if output is None:
        return input_path.with_suffix(".epub")
    if output.is_dir():
        return output / input_path.with_suffix(".epub").name
    return output
