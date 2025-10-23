#!/usr/bin/env python3
"""Extract text from all PDFs in the `pdfs/` directory into .txt files.

Behavior:
- Only scans the `pdfs/` directory (non-recursive).
- For each `something.pdf` creates `something.txt` next to it (in `pdfs/`).
- If the .txt already exists and is non-empty, the PDF is skipped.

Dependencies: PyPDF2 (pip install PyPDF2)

Usage: python3 pdf_to_text.py
"""
import sys
from pathlib import Path
import logging
import shutil
import subprocess

# Backend detection: try PyPDF2, then pdfminer.six, then pdftotext CLI
_HAS_PYPDF2 = False
_HAS_PDFMINER = False
_HAS_PDFTOTEXT = False

try:
    from PyPDF2 import PdfReader
    _HAS_PYPDF2 = True
except Exception:
    PdfReader = None

try:
    # pdfminer.six high level API
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    _HAS_PDFMINER = True
except Exception:
    pdfminer_extract_text = None

if shutil.which("pdftotext"):
    _HAS_PDFTOTEXT = True


def _extract_with_pypdf2(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return "\n\n".join(texts)


def _extract_with_pdfminer(pdf_path: Path) -> str:
    # pdfminer returns the full text
    return pdfminer_extract_text(str(pdf_path)) or ""


def _extract_with_pdftotext_cli(pdf_path: Path) -> str:
    # pdftotext -layout -q <pdf> -   (write to stdout)
    cmd = ["pdftotext", "-layout", "-q", str(pdf_path), "-"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {res.stderr.decode(errors='replace')}")
    return res.stdout.decode("utf-8", errors="replace")


def extract_pdf_to_text(pdf_path: Path, txt_path: Path) -> None:
    """Extract text from a single PDF into txt_path using the best available backend.

    This function overwrites txt_path.
    """
    if _HAS_PYPDF2:
        content = _extract_with_pypdf2(pdf_path)
    elif _HAS_PDFMINER:
        content = _extract_with_pdfminer(pdf_path)
    elif _HAS_PDFTOTEXT:
        content = _extract_with_pdftotext_cli(pdf_path)
    else:
        raise RuntimeError(
            "No PDF extraction backend available. Install PyPDF2 or pdfminer.six, or ensure pdftotext is on PATH."
        )

    txt_path.write_text(content, encoding="utf-8")


def main() -> int:
    base = Path(__file__).resolve().parent
    pdf_dir = base / "pdfs"
    if not pdf_dir.exists():
        logging.info("Creating missing directory %s", pdf_dir)
        pdf_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logging.info("No PDF files found in %s", pdf_dir)
        return 0

    processed = 0
    skipped = 0
    for pdf in pdf_files:
        txt = pdf.with_suffix('.txt')
        if txt.exists() and txt.stat().st_size > 0:
            logging.info("Skipping already extracted: %s", pdf.name)
            skipped += 1
            continue

        logging.info("Extracting: %s -> %s", pdf.name, txt.name)
        try:
            extract_pdf_to_text(pdf, txt)
            processed += 1
        except Exception as e:
            logging.error("Failed to extract %s: %s", pdf.name, e)

    logging.info("Done. Processed=%d Skipped=%d Total=%d", processed, skipped, len(pdf_files))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(main())
