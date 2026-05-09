import json
import re

# SHL test type codes and their meanings
TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

KNOWN_JOB_LEVELS = [
    "Director", "Entry-Level", "Executive", "Front Line Manager",
    "General Population", "Graduate", "Manager", "Mid-Professional",
    "Professional Individual Contributor", "Supervisor"
]

def extract_duration(description: str) -> int | None:
    """Extract duration in minutes from description text."""
    patterns = [
        r"Approximate Completion Time in minutes\s*=\s*(?:max\s*)?(\d+)",
        r"(\d+)\s*minutes?",
        r"(\d+)\s*[-–]\s*\d+\s*minutes?",  # range like "15 to 35"
    ]
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    return None

def extract_job_levels(description: str) -> list[str]:
    """Extract job levels mentioned in description."""
    found = []
    for level in KNOWN_JOB_LEVELS:
        if level.lower() in description.lower():
            found.append(level)
    return found

def extract_test_types(description: str) -> list[str]:
    """Extract test type codes from description."""
    # SHL embeds test types like "Test Type:AKP" or "Test Type:CP"
    match = re.search(r"Test Type:\s*([A-Z]+)", description)
    if match:
        codes = match.group(1)
        return [TEST_TYPE_MAP.get(c, c) for c in codes]
    return []

def extract_remote_testing(description: str) -> bool:
    """Detect if remote testing is supported."""
    text = description.lower()
    # Look for positive indicators
    if "remote testing:" in text:
        idx = text.index("remote testing:")
        surrounding = text[idx:idx+30]
        # If there's a "yes" or a URL/indicator after it
        if "yes" in surrounding or "✓" in surrounding:
            return True
    # Also check for explicit mentions
    if "unproctored" in text or "online" in text:
        return True
    return False

def extract_adaptive(description: str) -> bool:
    """Detect if assessment is adaptive/IRT."""
    keywords = ["adaptive", "irt", "item response theory"]
    text = description.lower()
    return any(kw in text for kw in keywords)

def clean_description(description: str) -> str:
    """
    Remove trailing metadata from description text.
    Keep the meaningful descriptive content only.
    """
    if not description:
        return ""

    # Remove test type and remote testing suffixes
    cleaners = [
        r"Test Type:[A-Z]+\s*Remote Testing:.*$",
        r"Remote Testing:.*$",
        r"Test Type:[A-Z]+.*$",
    ]
    for pattern in cleaners:
        description = re.sub(pattern, "", description, flags=re.IGNORECASE | re.DOTALL)

    # Clean whitespace
    description = " ".join(description.split())
    return description.strip()

def build_searchable_text(product: dict) -> str:
    """
    Build a rich text field that combines all metadata for embedding.
    This is what gets embedded and stored in FAISS.
    Better text = better retrieval = higher Recall@10.
    """
    parts = [
        f"Assessment: {product['name']}",
        f"Description: {product['clean_description']}",
    ]

    if product["job_levels"]:
        parts.append(f"Job levels: {', '.join(product['job_levels'])}")

    if product["test_types"]:
        parts.append(f"Test types: {', '.join(product['test_types'])}")

    if product["duration_minutes"]:
        parts.append(f"Duration: approximately {product['duration_minutes']} minutes")

    if product["remote_testing"]:
        parts.append("Remote testing: supported")

    if product["adaptive_irt"]:
        parts.append("Assessment type: adaptive")

    # Catalog type context
    if product["catalog_type"] == 1:
        parts.append("Category: Individual assessment or report")
    else:
        parts.append("Category: Pre-packaged job solution")

    return " | ".join(parts)

def clean_catalog(raw_path: str, output_path: str) -> list[dict]:
    """Clean raw scraped catalog into structured, embeddable records."""

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_products = json.load(f)

    print(f"Cleaning {len(raw_products)} products...")

    cleaned = []
    for product in raw_products:
        name = product.get("name", "").strip()
        description = product.get("description", "")

        if not name:
            continue

        # Extract structured fields from description text
        duration = extract_duration(description)
        job_levels = extract_job_levels(description)
        test_types = extract_test_types(description)
        remote = extract_remote_testing(description)
        adaptive = extract_adaptive(description)
        clean_desc = clean_description(description)

        cleaned_product = {
            "name": name,
            "url": product.get("url", ""),
            "catalog_type": product.get("catalog_type", 1),
            "clean_description": clean_desc,
            "raw_description": description,
            "job_levels": job_levels,
            "test_types": test_types,
            "duration_minutes": duration,
            "remote_testing": remote,
            "adaptive_irt": adaptive,
        }

        # Build the rich searchable text for embedding
        cleaned_product["searchable_text"] = build_searchable_text(cleaned_product)

        cleaned.append(cleaned_product)

    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    # Print summary stats
    with_duration = sum(1 for p in cleaned if p["duration_minutes"])
    with_levels = sum(1 for p in cleaned if p["job_levels"])
    with_types = sum(1 for p in cleaned if p["test_types"])

    print(f"\n✅ Cleaned catalog saved to {output_path}")
    print(f"   Total products:        {len(cleaned)}")
    print(f"   With duration:         {with_duration}")
    print(f"   With job levels:       {with_levels}")
    print(f"   With test types:       {with_types}")

    return cleaned

if __name__ == "__main__":
    cleaned = clean_catalog("data/raw_catalog.json", "data/catalog.json")

    # Show a sample record
    print("\n--- Sample cleaned record ---")
    sample = cleaned[0]
    print(f"Name:          {sample['name']}")
    print(f"Job levels:    {sample['job_levels']}")
    print(f"Duration:      {sample['duration_minutes']} min")
    print(f"Test types:    {sample['test_types']}")
    print(f"Remote:        {sample['remote_testing']}")
    print(f"\nSearchable text (first 200 chars):")
    print(sample['searchable_text'][:200])