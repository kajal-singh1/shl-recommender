# import requests
# from bs4 import BeautifulSoup

# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/120.0.0.0 Safari/537.36"
#     )
# }

# # Test different URL patterns SHL might use
# urls_to_test = [
#     "https://www.shl.com/solutions/products/product-catalog/?start=12&type=1",
#     "https://www.shl.com/solutions/products/product-catalog/?start=12",
#     "https://www.shl.com/solutions/products/product-catalog/?page=2",
#     "https://www.shl.com/solutions/products/product-catalog/?start=12&type=1&ajax=1",
# ]

# for url in urls_to_test:
#     resp = requests.get(url, headers=HEADERS, timeout=15)
#     soup = BeautifulSoup(resp.text, "html.parser")
#     rows = soup.select("tr.product-catalogue__row")
#     all_rows = soup.select("tr")
#     links = soup.select("a[href*='/products/']")
#     print(f"\nURL: {url}")
#     print(f"  product-catalogue__row: {len(rows)}")
#     print(f"  all <tr> tags: {len(all_rows)}")
#     print(f"  product links: {len(links)}")
#     # Print first product link found
#     if links:
#         print(f"  first link: {links[0].get_text(strip=True)} -> {links[0]['href']}")

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Check the base catalog page with NO parameters
url = "https://www.shl.com/solutions/products/product-catalog/"
resp = requests.get(url, headers=HEADERS, timeout=15)
soup = BeautifulSoup(resp.text, "html.parser")

# Print ALL unique hrefs containing 'product'
links = soup.select("a[href*='/product']")
seen = set()
for link in links:
    href = link.get("href", "")
    text = link.get_text(strip=True)
    if href not in seen and text:
        seen.add(href)
        print(f"{text[:60]:<60} -> {href}")

print(f"\nTotal unique product links: {len(seen)}")