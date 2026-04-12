#!/usr/bin/env python3
"""Extract road sign images from driver's manual PDFs.

Usage:
    python extract_signs.py <pdf_path> <output_dir> [--min-size 50]
"""

import os
import sys

import fitz  # PyMuPDF


def extract_images(pdf_path: str, output_dir: str, min_size: int = 50):
    """Extract all images from a PDF that are likely road signs."""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)

    extracted = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            if not base_image:
                continue

            width = base_image["width"]
            height = base_image["height"]

            # Filter: signs are typically square-ish images, not too small, not too large
            # Skip tiny icons and full-page images
            if width < min_size or height < min_size:
                continue
            if width > 2000 or height > 2000:
                continue

            ext = base_image["ext"]
            image_bytes = base_image["image"]

            filename = f"page{page_num + 1:03d}_img{img_idx:02d}.{ext}"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            extracted += 1
            print(f"  Page {page_num + 1}: {filename} ({width}x{height} {ext})")

    doc.close()
    print(f"\nExtracted {extracted} images to {output_dir}")
    return extracted


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python extract_signs.py <pdf_path> <output_dir> [--min-size 50]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    min_size = 50

    if "--min-size" in sys.argv:
        idx = sys.argv.index("--min-size")
        min_size = int(sys.argv[idx + 1])

    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"Extracting images from {pdf_path}...")
    extract_images(pdf_path, output_dir, min_size)


if __name__ == "__main__":
    main()
