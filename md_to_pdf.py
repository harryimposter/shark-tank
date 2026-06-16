"""Convert BUILD_GUIDE.md to BUILD_GUIDE.pdf via xhtml2pdf."""
import os
import markdown
from xhtml2pdf import pisa

MD_PATH  = "BUILD_GUIDE.md"
PDF_PATH = "BUILD_GUIDE.pdf"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 2.2cm 2.4cm 2.2cm 2.4cm;
  }}

  body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #1a1a1a;
  }}

  /* ── Headings ── */
  h1 {{
    font-size: 18pt;
    font-weight: 700;
    color: #111;
    margin: 0 0 6pt;
    padding-bottom: 4pt;
    border-bottom: 2px solid #b8960c;
    page-break-before: always;
  }}
  h1:first-of-type {{ page-break-before: avoid; }}

  h2 {{
    font-size: 13pt;
    font-weight: 700;
    color: #222;
    margin: 16pt 0 4pt;
    padding-bottom: 2pt;
    border-bottom: 1px solid #ddd;
  }}

  h3 {{
    font-size: 11pt;
    font-weight: 700;
    color: #333;
    margin: 12pt 0 3pt;
  }}

  h4 {{
    font-size: 10.5pt;
    font-weight: 700;
    color: #444;
    margin: 10pt 0 2pt;
  }}

  /* ── Body text ── */
  p  {{ margin: 0 0 6pt; }}
  ul, ol {{ margin: 4pt 0 6pt 18pt; padding: 0; }}
  li {{ margin-bottom: 3pt; line-height: 1.5; }}

  /* ── Code ── */
  code {{
    font-family: "Courier New", Courier, monospace;
    font-size: 8.5pt;
    background: #f5f5f2;
    padding: 1pt 3pt;
    border-radius: 2pt;
    color: #c0392b;
  }}
  pre {{
    font-family: "Courier New", Courier, monospace;
    font-size: 8pt;
    background: #f5f5f2;
    border: 1px solid #e0e0dc;
    border-left: 3px solid #b8960c;
    padding: 7pt 9pt;
    margin: 6pt 0 8pt;
    line-height: 1.45;
    overflow-wrap: break-word;
    white-space: pre-wrap;
    word-break: break-all;
  }}
  pre code {{
    background: transparent;
    padding: 0;
    color: #1a1a1a;
    border-radius: 0;
  }}

  /* ── Tables ── */
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9.5pt;
    margin: 6pt 0 10pt;
  }}
  th {{
    background: #f0ede4;
    font-weight: 700;
    text-align: left;
    padding: 4pt 6pt;
    border: 1px solid #ccc;
  }}
  td {{
    padding: 3.5pt 6pt;
    border: 1px solid #ddd;
    vertical-align: top;
  }}
  tr:nth-child(even) td {{ background: #fafaf8; }}

  /* ── Block quote / hr ── */
  blockquote {{
    margin: 6pt 0 6pt 0;
    padding: 5pt 10pt;
    background: #fdf8ec;
    border-left: 3px solid #b8960c;
    font-style: italic;
    color: #444;
  }}
  hr {{ border: none; border-top: 1px solid #ddd; margin: 12pt 0; }}

  /* ── Links ── */
  a {{ color: #b8960c; text-decoration: none; }}

  /* ── Suppress page-break inside code/table ── */
  pre, table {{ page-break-inside: avoid; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

def main():
    with open(MD_PATH, encoding="utf-8") as f:
        md_text = f.read()

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "nl2br"],
        extension_configs={
            "codehilite": {"noclasses": True, "linenums": False}
        }
    )

    full_html = HTML_TEMPLATE.format(body=html_body)

    with open(PDF_PATH, "wb") as out:
        result = pisa.CreatePDF(full_html, dest=out)

    if result.err:
        print(f"ERROR: xhtml2pdf reported {result.err} error(s).")
        return False

    size = os.path.getsize(PDF_PATH)
    print(f"OK: {PDF_PATH}  ({size:,} bytes)")
    return True

if __name__ == "__main__":
    main()
