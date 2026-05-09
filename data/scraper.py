import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.shl.com"
CATALOG_BASE = "https://www.shl.com/products/product-catalog/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# ── Step 1: Collect all product URLs ────────────────────────────

def collect_product_urls() -> list[dict]:
    """
    Paginate through both type=1 and type=2 catalogs.
    Extract every /products/product-catalog/view/ URL found.
    """
    product_urls = {}  # url -> {name, type}

    for catalog_type in [1, 2]:
        start = 0
        print(f"\nCollecting type={catalog_type} catalog URLs...")

        while True:
            url = f"{CATALOG_BASE}?start={start}&type={catalog_type}"
            print(f"  Fetching offset {start}...")

            try:
                soup = get_soup(url)
            except Exception as e:
                print(f"  Failed: {e}")
                break

            # Find all product detail links
            links = soup.select("a[href*='/product-catalog/view/']")

            if not links:
                print(f"  No product links found. End of type={catalog_type}.")
                break

            new_found = 0
            for link in links:
                href = link.get("href", "")
                name = link.get_text(strip=True)
                full_url = BASE_URL + href if href.startswith("/") else href

                if full_url not in product_urls and name:
                    product_urls[full_url] = {
                        "name": name,
                        "url": full_url,
                        "catalog_type": catalog_type
                    }
                    new_found += 1

            print(f"  Found {new_found} new products (total: {len(product_urls)})")

            # Find next page number for this type
            next_start = get_next_start(soup, catalog_type, start)
            if next_start is None:
                print(f"  No next page. End of type={catalog_type}.")
                break

            start = next_start
            time.sleep(1)  # polite delay

    return list(product_urls.values())


def get_next_start(soup, catalog_type: int, current_start: int) -> int | None:
    """Find the next pagination offset from page links."""
    # Look for pagination links for this type
    pattern = f"?start="
    next_start = None

    page_links = soup.select(f"a[href*='type={catalog_type}']")
    for link in page_links:
        href = link.get("href", "")
        if f"type={catalog_type}" in href and "start=" in href:
            try:
                start_val = int(href.split("start=")[1].split("&")[0])
                if start_val > current_start:
                    # Take the immediate next page
                    if next_start is None or start_val < next_start:
                        next_start = start_val
            except (ValueError, IndexError):
                continue

    return next_start


# ── Step 2: Scrape each product detail page ──────────────────────

def scrape_product_detail(product: dict) -> dict:
    """Visit individual product page and extract full metadata."""
    url = product["url"]

    try:
        soup = get_soup(url)
        time.sleep(0.5)

        # Description — try multiple selectors
        description = extract_description(soup)

        # Test type badges / tags
        test_types = extract_test_types(soup)

        # Duration
        duration = extract_duration(soup)

        # Job levels
        job_levels = extract_job_levels(soup)

        # Remote testing flag
        remote_testing = extract_flag(soup, "remote")

        # Adaptive/IRT flag
        adaptive_irt = extract_flag(soup, "adaptive")

        return {
            **product,
            "description": description,
            "test_types": test_types,
            "duration": duration,
            "job_levels": job_levels,
            "remote_testing": remote_testing,
            "adaptive_irt": adaptive_irt
        }

    except Exception as e:
        print(f"  Warning: failed to scrape {url}: {e}")
        return {
            **product,
            "description": "",
            "test_types": [],
            "duration": "",
            "job_levels": [],
            "remote_testing": False,
            "adaptive_irt": False
        }


def extract_description(soup) -> str:
    """Try multiple selectors to get product description."""
    selectors = [
        ".product-catalogue-training-calendar__row--description",
        ".product-hero__description",
        ".product-detail__description",
        "main .rich-text p",
        "main p",
        ".content-wrapper p"
    ]
    for sel in selectors:
        els = soup.select(sel)
        if els:
            text = " ".join(el.get_text(strip=True) for el in els[:4])
            if len(text) > 30:
                return text
    return ""


def extract_test_types(soup) -> list[str]:
    """Extract test type labels."""
    types = []
    selectors = [
        ".product-catalogue__key span",
        "[class*='test-type']",
        ".product-detail__meta span",
        ".catalogue__key span"
    ]
    for sel in selectors:
        els = soup.select(sel)
        if els:
            types = [el.get_text(strip=True) for el in els if el.get_text(strip=True)]
            if types:
                break
    return types


def extract_duration(soup) -> str:
    """Extract assessment duration."""
    selectors = [
        ".product-catalogue__duration",
        "[class*='duration']",
        "td:contains('minute')",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(strip=True)
            if text:
                return text

    # Fallback: search text for minute patterns
    full_text = soup.get_text()
    import re
    match = re.search(r"(\d+)\s*[-–]?\s*(\d+)?\s*minutes?", full_text, re.IGNORECASE)
    if match:
        return match.group(0)
    return ""


def extract_job_levels(soup) -> list[str]:
    """Extract job level tags."""
    selectors = [
        ".product-catalogue__job-level span",
        "[class*='job-level'] span",
        ".product-detail__job-levels span"
    ]
    for sel in selectors:
        els = soup.select(sel)
        if els:
            levels = [el.get_text(strip=True) for el in els if el.get_text(strip=True)]
            if levels:
                return levels
    return []


def extract_flag(soup, flag_type: str) -> bool:
    """Extract yes/no flags for remote testing or adaptive."""
    keyword = "remote" if flag_type == "remote" else "adaptive"
    
    # Check aria-labels
    els = soup.select(f"[aria-label*='{keyword}' i]")
    for el in els:
        aria = el.get("aria-label", "").lower()
        classes = " ".join(el.get("class", []))
        if "yes" in classes or "yes" in aria:
            return True

    # Check table cells
    full_text = soup.get_text().lower()
    if keyword in full_text:
        idx = full_text.index(keyword)
        surrounding = full_text[idx:idx+50]
        if "yes" in surrounding:
            return True

    return False


# ── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1: collect all product URLs
    print("=" * 50)
    print("STEP 1: Collecting product URLs")
    print("=" * 50)
    products = collect_product_urls()
    print(f"\nTotal unique products found: {len(products)}")

    # Step 2: scrape each product detail
    print("\n" + "=" * 50)
    print("STEP 2: Scraping product detail pages")
    print("=" * 50)

    detailed_products = []
    for i, product in enumerate(products, 1):
        print(f"[{i}/{len(products)}] Scraping: {product['name'][:60]}")
        detailed = scrape_product_detail(product)
        detailed_products.append(detailed)

    # Save raw output
    with open("data/raw_catalog.json", "w", encoding="utf-8") as f:
        json.dump(detailed_products, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved {len(detailed_products)} products to data/raw_catalog.json")

    # Quick summary
    with_desc = sum(1 for p in detailed_products if p.get("description"))
    print(f"   Products with descriptions: {with_desc}/{len(detailed_products)}")