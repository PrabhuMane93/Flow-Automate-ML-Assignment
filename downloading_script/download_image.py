#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen


BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "jewellery_products_subset.json"
IMAGES_DIR = BASE_DIR / "images"


def extension_from_url(url: str) -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix else ".jpg"


def download_file(url: str, output_path: Path) -> None:
    with urlopen(url) as response:
        data = response.read()
    output_path.write_bytes(data)


def main() -> None:
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"JSON file not found: {JSON_PATH}")

    with JSON_PATH.open("r", encoding="utf-8") as f:
        products = json.load(f)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    total_downloaded = 0
    total_failed = 0

    for product in products:
        product_id = str(product.get("product_id", "")).strip()
        image_urls = product.get("images", [])

        if not product_id:
            print("Skipping product with missing product_id")
            continue

        if not isinstance(image_urls, list) or not image_urls:
            print(f"Skipping {product_id}: no image URLs")
            continue

        product_dir = IMAGES_DIR / product_id
        product_dir.mkdir(parents=True, exist_ok=True)

        for idx, url in enumerate(image_urls, start=1):
            if not isinstance(url, str) or not url.strip():
                print(f"Skipping invalid URL for product {product_id}: {url!r}")
                total_failed += 1
                continue

            ext = extension_from_url(url)
            out_file = product_dir / f"{idx}{ext}"

            try:
                download_file(url, out_file)
                total_downloaded += 1
                print(f"Downloaded: {out_file}")
            except Exception as exc:
                total_failed += 1
                print(f"Failed: {product_id} | {url} | {exc}")

    print(
        f"Done. Downloaded {total_downloaded} images with {total_failed} failures."
    )


if __name__ == "__main__":
    main()
