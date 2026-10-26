"""Checks the PDFs the image made from the two test documents.

Usage: python check.py <docx.pdf> <xlsx.pdf>
Prints what it found as GitHub notices, and fails if any check fails.
"""
import re
import sys

import pymupdf


def spans(path):
    for page in pymupdf.open(path):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if span["text"].strip():
                        yield span["text"].strip(), span["font"]


def font_of(all_spans, prefix):
    for text, font in all_spans:
        # Adjacent cells can come out as one span ("2026/01/01 Example Foods").
        if text.startswith(prefix) or " " + prefix in text:
            return font
    return None


failures = []
report = []


def expect_font(all_spans, label, prefix, wanted):
    font = font_of(all_spans, prefix)
    ok = font is not None and wanted.lower() in font.lower()
    report.append(f"{label}: '{prefix}' printed in {font}" + ("" if ok else f" (expected {wanted})"))
    if not ok:
        failures.append(f"{label}: '{prefix}' printed in {font}, expected {wanted}")


docx = list(spans(sys.argv[1]))
xlsx = list(spans(sys.argv[2]))

# Word: Aptos body text and headings, plus the fonts that already had metric-compatible substitutes.
expect_font(docx, "Word body (Aptos)", "Upload this document", "Carlito")
expect_font(docx, "Word heading (Aptos Display)", "1. Fonts", "Carlito")
expect_font(docx, "Word", "Aptos - The quick", "Carlito")
expect_font(docx, "Word", "Aptos Display - The quick", "Carlito")
expect_font(docx, "Word", "Calibri - The quick", "Carlito")
expect_font(docx, "Word", "Cambria - The quick", "Caladea")
expect_font(docx, "Word", "Arial - The quick", "LiberationSans")
expect_font(docx, "Word", "Times New Roman - The quick", "LiberationSerif")

# Excel: Aptos Narrow is the default cell font.
expect_font(xlsx, "Excel", "Aptos Narrow - The quick", "RobotoCondensed")
expect_font(xlsx, "Excel register cells (Aptos Narrow)", "Example Foods", "RobotoCondensed")

# Excel's built-in short date: the register's first row is 1 January 2026.
dates = sorted({word for text, _ in xlsx for word in text.split()
                if re.fullmatch(r"\d{1,4}[/.-]\d{1,2}[/.-]\d{1,4}", word)})
report.append(f"Excel short dates print like: {', '.join(dates[:3])}")
if "2026/01/01" not in dates:
    failures.append(f"Excel short date: expected 2026/01/01, found {dates[:3]}")

# Not checked, just reported: how the register's rand amounts print with the new locale.
amounts = [text for text, _ in xlsx if text.startswith("R ")]
report.append(f"Excel rand amounts print like: {', '.join(amounts[:3])}")

# One notice for the lot: GitHub only shows the first 10 annotations of each kind per step.
print("::notice title=Conversion check::" + "%0A".join(report))

for failure in failures:
    print(f"::error::{failure}")
sys.exit(1 if failures else 0)
