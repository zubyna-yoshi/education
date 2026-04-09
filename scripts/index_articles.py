#!/usr/bin/env python3
"""Build article-to-page index from extracted PDF page text folders.

Expected doc dir layout:
- pages_text/page_0001.txt
- pages_jpg/page_0001.jpg (optional)

Outputs in out dir:
- article_index_by_doc.json
- article_index_master.json
- article_index_master.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

HEADING_RE = re.compile(
    r"^\s*제\s*(?P<article>\d+)\s*조(?:\s*의\s*(?P<sub>\d+))?\s*\((?P<title>[^)\n]{1,120})\)",
    re.UNICODE,
)


def parse_page_no(path: Path) -> int:
    m = re.search(r"page_(\d+)$", path.stem)
    if not m:
        return -1
    return int(m.group(1))


def article_label(article: str, sub: str | None) -> str:
    if sub:
        return f"제{int(article)}조의{int(sub)}"
    return f"제{int(article)}조"


def article_key(article: str, sub: str | None) -> str:
    if sub:
        return f"{int(article)}-{int(sub)}"
    return str(int(article))


def extract_article_excerpt(lines: list[str], start_line_no: int, max_chars: int = 3000) -> str:
    """Extract only the current article text until the next article heading on the same page."""
    start_idx = max(0, start_line_no - 1)
    out: list[str] = []
    size = 0
    for i in range(start_idx, len(lines)):
        if i > start_idx and HEADING_RE.match(lines[i]):
            break
        line = lines[i]
        out.append(line)
        size += len(line) + 1
        if size >= max_chars:
            break
    return "\n".join(out).strip()[:max_chars]


def index_doc(doc_dir: Path) -> dict:
    pages_text_dir = doc_dir / "pages_text"
    pages_jpg_dir = doc_dir / "pages_jpg"
    page_files = sorted(pages_text_dir.glob("page_*.txt"), key=parse_page_no)

    by_article: dict[str, dict] = {}

    for text_file in page_files:
        pno = parse_page_no(text_file)
        lines = text_file.read_text(encoding="utf-8", errors="ignore").splitlines()

        for idx, line in enumerate(lines, start=1):
            m = HEADING_RE.match(line)
            if not m:
                continue
            a = m.group("article")
            s = m.group("sub")
            t = m.group("title").strip()

            key = article_key(a, s)
            label = article_label(a, s)

            if key not in by_article:
                by_article[key] = {
                    "article_key": key,
                    "article_label": label,
                    "article_no": int(a),
                    "sub_no": int(s) if s else None,
                    "first_page": pno,
                    "pages": [],
                    "titles": [],
                    "occurrences": [],
                }

            entry = by_article[key]
            if pno < entry["first_page"]:
                entry["first_page"] = pno
            if pno not in entry["pages"]:
                entry["pages"].append(pno)
            if t and t not in entry["titles"]:
                entry["titles"].append(t)

            img_path = pages_jpg_dir / f"page_{pno:04d}.jpg"
            entry["occurrences"].append(
                {
                    "page": pno,
                    "line": idx,
                    "title": t,
                    "article_excerpt": extract_article_excerpt(lines, idx),
                    "text_file": str(text_file),
                    "image_file": str(img_path) if img_path.exists() else None,
                }
            )

    # sort page lists and occurrences for consistency
    for entry in by_article.values():
        entry["pages"].sort()
        entry["occurrences"].sort(key=lambda x: (x["page"], x["line"]))

    ordered = dict(sorted(by_article.items(), key=lambda kv: (kv[1]["article_no"], kv[1]["sub_no"] or 0)))

    return {
        "doc_name": doc_dir.name,
        "doc_dir": str(doc_dir),
        "pages_text_dir": str(pages_text_dir),
        "pages_jpg_dir": str(pages_jpg_dir),
        "article_count": len(ordered),
        "articles": ordered,
    }


def build_master(by_doc: dict[str, dict]) -> dict:
    master: dict[str, dict] = {}

    for doc_name, doc_data in by_doc.items():
        for key, article in doc_data["articles"].items():
            if key not in master:
                master[key] = {
                    "article_key": key,
                    "article_label": article["article_label"],
                    "article_no": article["article_no"],
                    "sub_no": article["sub_no"],
                    "documents": {},
                }
            master[key]["documents"][doc_name] = {
                "first_page": article["first_page"],
                "pages": article["pages"],
                "titles": article["titles"],
                "occurrence_count": len(article["occurrences"]),
                "first_text_file": article["occurrences"][0]["text_file"] if article["occurrences"] else None,
                "first_image_file": article["occurrences"][0]["image_file"] if article["occurrences"] else None,
                "first_text_preview": (
                    article["occurrences"][0].get("article_excerpt", "")[:1200]
                    if article["occurrences"]
                    else ""
                ),
            }

    return dict(sorted(master.items(), key=lambda kv: (kv[1]["article_no"], kv[1]["sub_no"] or 0)))


def write_csv(master: dict, out_csv: Path) -> None:
    doc_names = sorted({d for item in master.values() for d in item["documents"].keys()})

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        header = ["article_key", "article_label"]
        for d in doc_names:
            header.extend([f"{d}:first_page", f"{d}:pages", f"{d}:titles"])
        w.writerow(header)

        for item in master.values():
            row = [item["article_key"], item["article_label"]]
            for d in doc_names:
                if d in item["documents"]:
                    dd = item["documents"][d]
                    row.extend(
                        [
                            dd["first_page"],
                            ",".join(str(p) for p in dd["pages"]),
                            " | ".join(dd["titles"]),
                        ]
                    )
                else:
                    row.extend(["", "", ""])
            w.writerow(row)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc-dir", action="append", required=True, help="Extracted document output directory")
    ap.add_argument("--out-dir", required=True, help="Where to save index files")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    by_doc = {}
    for d in args.doc_dir:
        doc_path = Path(d).resolve()
        by_doc[doc_path.name] = index_doc(doc_path)

    master = build_master(by_doc)

    by_doc_path = out_dir / "article_index_by_doc.json"
    master_path = out_dir / "article_index_master.json"
    csv_path = out_dir / "article_index_master.csv"

    by_doc_path.write_text(json.dumps(by_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    master_path.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(master, csv_path)

    summary = {
        "documents": {k: v["article_count"] for k, v in by_doc.items()},
        "master_article_count": len(master),
        "outputs": {
            "by_doc": str(by_doc_path),
            "master": str(master_path),
            "csv": str(csv_path),
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
