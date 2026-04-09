#!/usr/bin/env python3
"""Extract text and images from a PDF using PyMuPDF.

Outputs:
- full_text.txt: concatenated text for all pages
- pages_text/page_XXXX.txt: text by page
- pages_jpg/page_XXXX.jpg: rendered page images (optional)
- embedded_images/*: images embedded in PDF objects (optional, xref deduped)
- manifest.json: extraction metadata
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import fitz


def safe_name(name: str) -> str:
    bad = '<>:"/\\|?*\n\r\t'
    out = ''.join('_' if c in bad else c for c in name)
    out = out.strip(' .')
    return out or 'document'


def extract(
    pdf_path: Path,
    out_root: Path,
    dpi: int,
    max_pages: int | None,
    render_pages: bool,
    extract_embedded: bool,
) -> dict:
    doc = fitz.open(pdf_path)
    doc_name = safe_name(pdf_path.stem)
    out_dir = out_root / doc_name
    out_dir.mkdir(parents=True, exist_ok=True)

    page_text_dir = out_dir / 'pages_text'
    page_text_dir.mkdir(exist_ok=True)

    page_img_dir = out_dir / 'pages_jpg'
    if render_pages:
        page_img_dir.mkdir(exist_ok=True)

    embedded_dir = out_dir / 'embedded_images'
    if extract_embedded:
        embedded_dir.mkdir(exist_ok=True)

    total_pages = doc.page_count
    end_page = min(total_pages, max_pages) if max_pages else total_pages

    full_text_parts = []
    embedded_saved = 0
    seen_xref = set()

    for i in range(end_page):
        page = doc.load_page(i)
        pno = i + 1

        text = page.get_text('text')
        (page_text_dir / f'page_{pno:04d}.txt').write_text(text, encoding='utf-8')
        full_text_parts.append(f'\n\n===== PAGE {pno} =====\n\n{text}')

        if render_pages:
            mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            pix.save(page_img_dir / f'page_{pno:04d}.jpg')

        if extract_embedded:
            for img in page.get_images(full=True):
                xref = img[0]
                if xref in seen_xref:
                    continue
                seen_xref.add(xref)
                data = doc.extract_image(xref)
                if not data:
                    continue
                ext = data.get('ext', 'bin')
                image_bytes = data.get('image', b'')
                if not image_bytes:
                    continue
                out_img = embedded_dir / f'xref_{xref}.{ext}'
                out_img.write_bytes(image_bytes)
                embedded_saved += 1

    (out_dir / 'full_text.txt').write_text(''.join(full_text_parts), encoding='utf-8')

    manifest = {
        'source_pdf': str(pdf_path),
        'output_dir': str(out_dir),
        'total_pages_in_pdf': total_pages,
        'pages_processed': end_page,
        'rendered_page_images': render_pages,
        'embedded_images_extracted': extract_embedded,
        'embedded_images_saved': embedded_saved,
        'dpi': dpi if render_pages else None,
    }
    (out_dir / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', required=True, help='Path to source PDF')
    parser.add_argument('--out-root', required=True, help='Output root directory')
    parser.add_argument('--dpi', type=int, default=96)
    parser.add_argument('--max-pages', type=int, default=0)
    parser.add_argument('--no-render-pages', action='store_true')
    parser.add_argument('--no-embedded-images', action='store_true')
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    out_root = Path(args.out_root).expanduser().resolve()

    manifest = extract(
        pdf_path=pdf_path,
        out_root=out_root,
        dpi=args.dpi,
        max_pages=(args.max_pages if args.max_pages > 0 else None),
        render_pages=not args.no_render_pages,
        extract_embedded=not args.no_embedded_images,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
