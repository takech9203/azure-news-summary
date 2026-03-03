#!/usr/bin/env python3
"""
Azure Blog RSS Feed Parser

Parses the Azure Blog RSS feed and outputs filtered items as JSON.

Usage:
    python parse_azure_blog.py [--days DAYS] [--feed PATH]

Options:
    --days DAYS    Number of days to look back (default: 7)
    --feed PATH    Path to RSS feed XML file (default: /tmp/azure_blog.xml)

Output:
    JSON object with filtered blog items

RSS Feed URL:
    https://azure.microsoft.com/en-us/blog/feed/

RSS 2.0 Format:
    <item>
        <title>Blog Post Title</title>
        <link>https://azure.microsoft.com/blog/...</link>
        <dc:creator>Author Name</dc:creator>
        <pubDate>Mon, 01 Mar 2026 00:00:00 GMT</pubDate>
        <category>Category1</category>
        <description>Brief description</description>
        <content:encoded>Full HTML content</content:encoded>
    </item>
"""

import argparse
import json
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


def parse_feed(feed_path: Path, days: int) -> dict:
    """Parse Azure Blog RSS 2.0 feed."""
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing feed: {e}", file=sys.stderr)
        return {"source": "azure-blog", "total_items": 0, "items": []}

    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

    # Namespaces
    ns = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "content": "http://purl.org/rss/1.0/modules/content/",
    }

    # Find all items in RSS 2.0 format
    items_elem = root.findall(".//item")

    items = []
    for item in items_elem:
        try:
            title_elem = item.find("title")
            link_elem = item.find("link")
            description_elem = item.find("description")
            pub_date_elem = item.find("pubDate")
            creator_elem = item.find("dc:creator", ns)
            category_elems = item.findall("category")
            content_elem = item.find("content:encoded", ns)

            if title_elem is None or title_elem.text is None:
                continue

            title = title_elem.text.strip()

            # Parse date
            if pub_date_elem is not None and pub_date_elem.text:
                published = parse_rfc2822_date(pub_date_elem.text)
            else:
                continue

            # Filter by date
            if published < cutoff_date:
                continue

            link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
            description = description_elem.text.strip() if description_elem is not None and description_elem.text else ""
            creator = creator_elem.text.strip() if creator_elem is not None and creator_elem.text else ""
            categories = [cat.text.strip() for cat in category_elems if cat.text]
            content = content_elem.text.strip() if content_elem is not None and content_elem.text else ""

            items.append({
                "title": title,
                "date": published.strftime("%Y-%m-%d"),
                "datetime": published.isoformat(),
                "url": link,
                "description": description,
                "author": creator,
                "categories": categories,
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "source": "azure-blog",
            })

        except Exception as e:
            print(f"Error parsing item: {e}", file=sys.stderr)
            continue

    # Sort by date (newest first)
    items.sort(key=lambda x: x["datetime"], reverse=True)

    return {
        "source": "azure-blog",
        "total_items": len(items),
        "items": items,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse Azure Blog RSS feed"
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
        default=Path("/tmp/azure_blog.xml"),
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
