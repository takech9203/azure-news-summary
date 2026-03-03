#!/usr/bin/env python3
"""
Azure Updates RSS Feed Parser

Parses the Azure Updates RSS feed and outputs filtered items as JSON.

Usage:
    python parse_azure_updates.py [--days DAYS] [--feed PATH]

Options:
    --days DAYS    Number of days to look back (default: 7)
    --feed PATH    Path to RSS feed XML file (default: /tmp/azure_updates.xml)

Output:
    JSON object with filtered update items

RSS Feed URL:
    https://www.microsoft.com/releasecommunications/api/v2/azure/rss

RSS 2.0 Format:
    <item>
        <guid>unique-id</guid>
        <link>https://azure.microsoft.com/updates/...</link>
        <title>[Launched] Service Name - Feature Title</title>
        <description>Feature description</description>
        <pubDate>Mon, 01 Mar 2026 00:00:00 GMT</pubDate>
        <category>Category1</category>
        <category>Category2</category>
        <a10:updated>2026-03-01T00:00:00Z</a10:updated>
    </item>
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


def parse_rfc2822_date(date_str: str) -> datetime:
    """Parse RFC 2822 date string (RSS 2.0 pubDate format) to datetime object."""
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now(timezone.utc)


def parse_iso8601_date(date_str: str) -> datetime:
    """Parse ISO 8601 date string to datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def extract_status_from_title(title: str) -> tuple[str, str]:
    """
    Extract status prefix from title.

    Azure Updates titles have format: "[Status] Service - Feature"
    Status can be: Launched, In preview, In development, Retired, etc.

    Returns:
        tuple: (status, clean_title)
    """
    # Match patterns like [Launched], [In preview], [In development]
    match = re.match(r'^\[([^\]]+)\]\s*(.+)$', title)
    if match:
        status = match.group(1).strip()
        clean_title = match.group(2).strip()
        return status, clean_title
    return "Unknown", title


def parse_feed(feed_path: Path, days: int) -> dict:
    """Parse Azure Updates RSS 2.0 feed."""
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing feed: {e}", file=sys.stderr)
        return {"source": "azure-updates", "total_items": 0, "items": []}

    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Namespace for Atom 1.0 elements (a10:updated)
    ns = {"a10": "http://www.w3.org/2005/Atom"}

    # Find all items in RSS 2.0 format
    items_elem = root.findall(".//item")

    items = []
    for item in items_elem:
        try:
            title_elem = item.find("title")
            link_elem = item.find("link")
            description_elem = item.find("description")
            pub_date_elem = item.find("pubDate")
            guid_elem = item.find("guid")
            category_elems = item.findall("category")

            # Try to get a10:updated for more precise timestamp
            updated_elem = item.find("a10:updated", ns)

            if title_elem is None or title_elem.text is None:
                continue

            title = title_elem.text.strip()

            # Extract status from title
            status, clean_title = extract_status_from_title(title)

            # Parse date - prefer a10:updated, fall back to pubDate
            if updated_elem is not None and updated_elem.text:
                published = parse_iso8601_date(updated_elem.text)
            elif pub_date_elem is not None and pub_date_elem.text:
                published = parse_rfc2822_date(pub_date_elem.text)
            else:
                continue

            # Filter by date
            if published < cutoff_date:
                continue

            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            description = description_elem.text.strip() if description_elem is not None and description_elem.text else ""
            guid = guid_elem.text.strip() if guid_elem is not None and guid_elem.text else ""
            categories = [cat.text.strip() for cat in category_elems if cat.text]

            items.append({
                "title": clean_title,
                "original_title": title,
                "status": status,
                "date": published.strftime("%Y-%m-%d"),
                "datetime": published.isoformat(),
                "url": link,
                "description": description,
                "guid": guid,
                "categories": categories,
                "source": "azure-updates",
            })

        except Exception as e:
            print(f"Error parsing item: {e}", file=sys.stderr)
            continue

    # Sort by date (newest first)
    items.sort(key=lambda x: x["datetime"], reverse=True)

    return {
        "source": "azure-updates",
        "total_items": len(items),
        "items": items,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse Azure Updates RSS feed"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)",
    )
    parser.add_argument(
        "--feed",
        type=Path,
        default=Path("/tmp/azure_updates.xml"),
        help="Path to RSS feed XML file",
    )

    args = parser.parse_args()

    if not args.feed.exists():
        print(f"Error: Feed file not found: {args.feed}", file=sys.stderr)
        sys.exit(1)

    result = parse_feed(args.feed, args.days)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
