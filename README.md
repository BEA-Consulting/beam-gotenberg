# beam-gotenberg

The [Gotenberg](https://gotenberg.dev) image (MIT licence) that BEAM QMS uses to convert Word and Excel
documents and its reports to PDF, with two small changes:

- **Font substitutes for Aptos**, Microsoft Office's default font since 2024. Aptos can't be
  redistributed, so without these LibreOffice falls back to a serif font. See
  [`fonts/60-beam-font-substitutes.conf`](fonts/60-beam-font-substitutes.conf).
- **A South African locale**, so spreadsheet cells in Excel's built-in short-date format print as
  `2026/01/31`, not US-style `1/31/2026`.

Everything else (routes, options, basic auth) is the stock Gotenberg image's.

This repository holds only how the image is built. No documents or data pass through it. Gotenberg
itself runs in BEAM's own Azure Container App, which pulls the published image:

```
ghcr.io/bea-consulting/beam-gotenberg:<gotenberg version>-beam.<revision>
```

Each push to `main` builds the image, converts the two documents in [`test/`](test/), checks the
fonts and dates in the PDFs ([`test/check.py`](test/check.py)), and only then publishes it. The
converted PDFs are kept on each workflow run for a visual check.
