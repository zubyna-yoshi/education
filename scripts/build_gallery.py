#!/usr/bin/env python3
from pathlib import Path
import argparse

HTML_HEAD = """<!doctype html>
<html lang=\"ko\">
<head>
<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<title>PDF Pages Gallery</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif; margin: 0; background: #f6f7f9; }
  .wrap { max-width: 1200px; margin: 0 auto; padding: 20px; }
  h1 { margin: 0 0 12px; font-size: 22px; }
  .meta { color: #444; margin-bottom: 16px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
  .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.05); }
  .card img { width: 100%; display: block; background: #ddd; }
  .row { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; font-size: 13px; }
  .row a { text-decoration: none; color: #0b57d0; }
</style>
</head>
<body>
<div class=\"wrap\">\n"""

HTML_TAIL = """</div></body></html>\n"""


def build(doc_dir: Path) -> Path:
    pages_jpg = doc_dir / 'pages_jpg'
    pages_text = doc_dir / 'pages_text'
    imgs = sorted(pages_jpg.glob('page_*.jpg'))

    out = [HTML_HEAD]
    out.append(f"<h1>{doc_dir.name}</h1>")
    out.append(f"<div class='meta'>총 페이지 이미지: {len(imgs)}장</div>")
    out.append("<div class='grid'>")

    for img in imgs:
        stem = img.stem
        txt = pages_text / f"{stem}.txt"
        txt_link = txt.name if txt.exists() else ''
        out.append("<div class='card'>")
        out.append(f"<a href='pages_jpg/{img.name}' target='_blank'><img loading='lazy' src='pages_jpg/{img.name}' alt='{stem}'></a>")
        out.append("<div class='row'>")
        out.append(f"<span>{stem}</span>")
        if txt_link:
            out.append(f"<a href='pages_text/{txt_link}' target='_blank'>텍스트</a>")
        else:
            out.append("<span></span>")
        out.append("</div></div>")

    out.append("</div>")
    out.append(HTML_TAIL)

    out_path = doc_dir / 'gallery.html'
    out_path.write_text(''.join(out), encoding='utf-8')
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--doc-dir', required=True)
    args = ap.parse_args()
    p = build(Path(args.doc_dir).resolve())
    print(p)


if __name__ == '__main__':
    main()
