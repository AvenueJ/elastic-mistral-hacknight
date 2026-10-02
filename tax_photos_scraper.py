#!/usr/bin/env python3
"""
Scrape NYC Municipal Archives 1940s Tax Photos (OCR test corpus).

Downloads a batch of scanned 1939-1941 NYC tax-assessment photographs from the
NYC DORIS digital archive (Preservica) and writes each image plus a sidecar row
of scraped metadata, so an OCR result can later be mapped back to a real
address / block / lot.

The archive is a server-rendered Preservica site. Objects are UUID-prefixed:
    SO_<uuid>  structural object (folder: the collection root, or a borough)
    IO_<uuid>  information object (a single photo asset)

Confirmed endpoints (plain unauthenticated GET, no cookie/referer needed):
    folder page : https://nycrecords.access.preservica.com/uncategorized/{SO_id}/
    asset page  : https://nycrecords.access.preservica.com/uncategorized/{IO_id}/
    file bytes  : https://nycrecords.access.preservica.com/download/file/{IO_id}

Pagination caveat: a folder's static HTML returns only its FIRST page of
children (~24 assets). Deeper paging and the Block/Lot faceted search are
driven by client-side XHR that this scraper does not replay. For a small OCR
test corpus (the stated goal) the first page per borough folder is plenty; to
go deeper, seed --io-ids / --so-ids with IDs copied from the site's search.

Licensing: non-commercial use of Municipal Archives materials is exempt from
licensing. Credit derived/published output as:
    [Item Name], 1940s Tax Department photographs,
    Courtesy of the Municipal Archives, City of New York

Be a good citizen: this is a city-government server, not a CDN. The scraper
rate-limits to ~1 request/second and sends a descriptive User-Agent.

Usage:
    python tax_photos_scraper.py                       # Richmond (Staten Island), 200 images
    python tax_photos_scraper.py --borough brooklyn --max 50
    python tax_photos_scraper.py --so-ids SO_xxance... --max 100
    python tax_photos_scraper.py --io-ids IO_039ddc71-0796-4a01-9043-aae5b1cf2080
"""
import argparse
import csv
import os
import re
import sys
import time

import requests

BASE = "https://nycrecords.access.preservica.com"
USER_AGENT = (
    "nyc-hacknight-taxphoto-ocr/1.0 "
    "(Elastic x Mistral NYC hack night; non-commercial OCR research)"
)

# Collection root and its five borough folders (confirmed).
COLLECTION_ROOT = "SO_d501be84-e09a-4023-bb8a-263aa8b0e04f"
BOROUGHS = {
    "bronx":     "SO_ad9565b5-e87e-4b78-96d1-ebb2035d0d9a",
    "brooklyn":  "SO_6619dce3-4174-450e-bcbb-ae5ef78060de",
    "manhattan": "SO_e6e79554-4227-414f-afc2-5f008fb9c96b",
    "queens":    "SO_c7d09c9c-66cb-4d9d-9f80-01a5401e58c9",
    "richmond":  "SO_f592b9c3-c7e5-4932-baf4-3780d8420d58",  # Staten Island
}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

DELAY_SECONDS = 1.0  # polite rate limit between requests

LINK_RE = re.compile(r"/uncategorized/((?:SO|IO)_[0-9a-f-]+)/")
META_RE = re.compile(
    r'<span[^>]*>([A-Za-z ]+)</span>'
    r'<span class="metadata-field-separator">:</span>\s*'
    r'<span class="metadata-content">(.*?)</span>',
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")


def get(url):
    """Rate-limited GET returning the response (raises on HTTP error)."""
    time.sleep(DELAY_SECONDS)
    r = SESSION.get(url, timeout=30)
    r.raise_for_status()
    return r


def folder_children(so_id):
    """Return (so_children, io_children) found on a folder's first page."""
    html = get(f"{BASE}/uncategorized/{so_id}/").text
    ids = {m for m in LINK_RE.findall(html)}
    so = sorted(i for i in ids if i.startswith("SO_") and i != so_id)
    io = sorted(i for i in ids if i.startswith("IO_"))
    return so, io


def scrape_metadata(io_id):
    """Scrape the metadata block from an asset page into a dict."""
    html = get(f"{BASE}/uncategorized/{io_id}/").text
    meta = {}
    for label, value in META_RE.findall(html):
        label = label.strip().lower().replace(" ", "_")
        value = TAG_RE.sub("", value).strip()
        if value and label not in meta:  # keep first non-empty (e.g. primary Title)
            meta[label] = value
    return meta


def download_image(io_id, path):
    """Download the asset's file bytes to path. Returns the content-type."""
    r = get(f"{BASE}/download/file/{io_id}")
    with open(path, "wb") as f:
        f.write(r.content)
    return r.headers.get("Content-Type", "")


def safe(part, default="unknown"):
    part = (part or default).strip() or default
    return re.sub(r"[^0-9A-Za-z._-]+", "_", part)


def crawl(seed_so, seed_io, out_dir, max_images):
    os.makedirs(out_dir, exist_ok=True)
    meta_path = os.path.join(out_dir, "metadata.csv")
    fields = ["io_uuid", "borough", "block", "lot", "title",
              "start_date", "end_date", "identifier", "file_path"]

    seen_io = set()
    queue_so = list(seed_so)
    queue_io = list(seed_io)
    count = 0

    with open(meta_path, "w", newline="") as mf:
        writer = csv.DictWriter(mf, fieldnames=fields)
        writer.writeheader()

        while (queue_so or queue_io) and count < max_images:
            # Expand folders first so we discover assets to download.
            while queue_so and count + len(queue_io) < max_images:
                so = queue_so.pop(0)
                try:
                    so_children, io_children = folder_children(so)
                except requests.RequestException as e:
                    print(f"  ! folder {so}: {e}", file=sys.stderr)
                    continue
                queue_so.extend(s for s in so_children if s not in queue_so)
                queue_io.extend(i for i in io_children if i not in seen_io and i not in queue_io)
                print(f"folder {so}: +{len(so_children)} folders, +{len(io_children)} assets "
                      f"(queued {len(queue_io)})")

            if not queue_io:
                break

            io_id = queue_io.pop(0)
            if io_id in seen_io:
                continue
            seen_io.add(io_id)

            try:
                meta = scrape_metadata(io_id)
            except requests.RequestException as e:
                print(f"  ! metadata {io_id}: {e}", file=sys.stderr)
                continue

            borough = safe(meta.get("borough", "").split("(")[0])
            block = safe(meta.get("block"))
            lot = safe(meta.get("lot"))
            dest_dir = os.path.join(out_dir, borough, block)
            os.makedirs(dest_dir, exist_ok=True)
            file_path = os.path.join(dest_dir, f"{lot}_{io_id}.jpg")

            try:
                download_image(io_id, file_path)
            except requests.RequestException as e:
                print(f"  ! download {io_id}: {e}", file=sys.stderr)
                continue

            writer.writerow({
                "io_uuid": io_id,
                "borough": meta.get("borough", ""),
                "block": meta.get("block", ""),
                "lot": meta.get("lot", ""),
                "title": meta.get("title", ""),
                "start_date": meta.get("start_date", ""),
                "end_date": meta.get("end_date", ""),
                "identifier": meta.get("identifier", ""),
                "file_path": file_path,
            })
            mf.flush()
            count += 1
            print(f"[{count}/{max_images}] {meta.get('title', io_id)} "
                  f"(block {meta.get('block','?')} lot {meta.get('lot','?')})")

    print(f"\nDone. {count} images + metadata written to {out_dir}/")
    print(f"Metadata sidecar: {meta_path}")


def main():
    global DELAY_SECONDS
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--borough", choices=sorted(BOROUGHS),
                    help="Borough folder to crawl (default: richmond / Staten Island).")
    ap.add_argument("--root", action="store_true",
                    help="Crawl from the collection root (all five boroughs).")
    ap.add_argument("--so-ids", nargs="*", default=[],
                    help="Explicit SO_ folder IDs to crawl.")
    ap.add_argument("--io-ids", nargs="*", default=[],
                    help="Explicit IO_ asset IDs to download directly.")
    ap.add_argument("--out", default="output", help="Output directory (default: output).")
    ap.add_argument("--max", type=int, default=200, help="Max images (default: 200).")
    ap.add_argument("--delay", type=float, default=DELAY_SECONDS,
                    help="Seconds between requests (default: 1.0).")
    args = ap.parse_args()

    DELAY_SECONDS = args.delay

    seed_so = list(args.so_ids)
    if args.root:
        seed_so.append(COLLECTION_ROOT)
    if args.borough:
        seed_so.append(BOROUGHS[args.borough])
    if not seed_so and not args.io_ids:
        seed_so.append(BOROUGHS["richmond"])  # smallest borough: good first test

    print(f"Seeds: {len(seed_so)} folder(s), {len(args.io_ids)} asset(s); "
          f"max {args.max} images; {DELAY_SECONDS}s between requests\n")
    crawl(seed_so, list(args.io_ids), args.out, args.max)


if __name__ == "__main__":
    main()
