#!/usr/bin/env python3
"""
Sysdig Documentation Monitor
Monitors Sysdig documentation for updates and generates Japanese reports
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import time

class SysdigMonitor:
    def __init__(self, data_dir: str = "data", reports_dir: str = "reports"):
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        self.rss_feeds = {
            "agent": "https://docs.sysdig.com/feed/agent-release-notes.xml",
            "serverless": "https://docs.sysdig.com/feed/serverless-agent-release-notes.xml",
            "monitor": "https://docs.sysdig.com/feed/monitor-saas-release-notes.xml",
            "secure": "https://docs.sysdig.com/feed/secure-saas-release-notes.xml",
            "onprem": "https://docs.sysdig.com/feed/on-premises-release-notes.xml",
            "falco": "https://docs.sysdig.com/feed/falco-rules-release-notes.xml"
        }

        self.web_urls = {
            "host_shield": "https://docs.sysdig.com/en/release-notes/linux-host-shield-release-notes/",
            "deprecation": "https://docs.sysdig.com/en/deprecation/"
        }

    def fetch_rss_feed(self, feed_name: str, feed_url: str) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed"""
        print(f"Fetching RSS feed: {feed_name}")
        try:
            feed = feedparser.parse(feed_url)
            entries = []

            for entry in feed.entries[:5]:  # Get latest 5 entries
                entries.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")[:500]  # First 500 chars
                })

            return entries
        except Exception as e:
            print(f"Error fetching RSS feed {feed_name}: {e}")
            return []

    def fetch_web_page(self, page_name: str, url: str) -> Dict[str, Any]:
        """Fetch and parse web page"""
        print(f"Fetching web page: {page_name}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract main content
            content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')

            if content:
                # Get text content
                text = content.get_text(separator='\n', strip=True)

                # Calculate hash for change detection
                content_hash = hashlib.sha256(text.encode()).hexdigest()

                # Extract headings for structure
                headings = []
                for heading in content.find_all(['h1', 'h2', 'h3'])[:10]:
                    headings.append({
                        "level": heading.name,
                        "text": heading.get_text(strip=True)
                    })

                return {
                    "url": url,
                    "fetched_at": datetime.now().isoformat(),
                    "content_hash": content_hash,
                    "headings": headings,
                    "text_preview": text[:1000]  # First 1000 chars
                }
            else:
                return {
                    "url": url,
                    "error": "Could not find main content"
                }

        except Exception as e:
            print(f"Error fetching web page {page_name}: {e}")
            return {
                "url": url,
                "error": str(e)
            }

    def load_previous_data(self, filename: str) -> Dict[str, Any]:
        """Load previous monitoring data"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_current_data(self, filename: str, data: Dict[str, Any]):
        """Save current monitoring data"""
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def detect_changes(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes between previous and current data"""
        changes = {
            "has_changes": False,
            "rss_changes": {},
            "web_changes": {}
        }

        # Check RSS feed changes
        if "rss_feeds" in current:
            for feed_name, entries in current["rss_feeds"].items():
                if feed_name not in previous.get("rss_feeds", {}):
                    changes["rss_changes"][feed_name] = {
                        "status": "new_feed",
                        "new_entries": len(entries)
                    }
                    changes["has_changes"] = True
                else:
                    prev_titles = {e["title"] for e in previous["rss_feeds"][feed_name]}
                    curr_titles = {e["title"] for e in entries}
                    new_titles = curr_titles - prev_titles

                    if new_titles:
                        changes["rss_changes"][feed_name] = {
                            "status": "updated",
                            "new_entries": list(new_titles)
                        }
                        changes["has_changes"] = True

        # Check web page changes
        if "web_pages" in current:
            for page_name, page_data in current["web_pages"].items():
                if "content_hash" not in page_data:
                    continue

                prev_hash = previous.get("web_pages", {}).get(page_name, {}).get("content_hash", "")
                curr_hash = page_data["content_hash"]

                if prev_hash != curr_hash:
                    changes["web_changes"][page_name] = {
                        "status": "updated",
                        "url": page_data["url"]
                    }
                    changes["has_changes"] = True

        return changes

    def run_monitoring(self) -> Dict[str, Any]:
        """Run full monitoring cycle"""
        print("=" * 60)
        print(f"Starting Sysdig Documentation Monitoring")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)

        current_data = {
            "timestamp": datetime.now().isoformat(),
            "rss_feeds": {},
            "web_pages": {}
        }

        # Fetch RSS feeds
        print("\n[1/2] Fetching RSS Feeds...")
        for feed_name, feed_url in self.rss_feeds.items():
            entries = self.fetch_rss_feed(feed_name, feed_url)
            current_data["rss_feeds"][feed_name] = entries
            time.sleep(1)  # Be nice to the server

        # Fetch web pages
        print("\n[2/2] Fetching Web Pages...")
        for page_name, url in self.web_urls.items():
            page_data = self.fetch_web_page(page_name, url)
            current_data["web_pages"][page_name] = page_data
            time.sleep(1)  # Be nice to the server

        # Load previous data and detect changes
        print("\n[3/3] Detecting Changes...")
        previous_data = self.load_previous_data("latest.json")
        changes = self.detect_changes(previous_data, current_data)

        # Save current data
        self.save_current_data("latest.json", current_data)

        # Save changes if any
        if changes["has_changes"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.save_current_data(f"changes_{timestamp}.json", {
                "timestamp": current_data["timestamp"],
                "changes": changes,
                "data": current_data
            })

        print("\n" + "=" * 60)
        print(f"Monitoring Complete!")
        print(f"Changes detected: {changes['has_changes']}")
        print("=" * 60)

        return {
            "current_data": current_data,
            "changes": changes
        }

if __name__ == "__main__":
    monitor = SysdigMonitor()
    result = monitor.run_monitoring()

    if result["changes"]["has_changes"]:
        print("\n✓ Changes detected - Report generation will follow")
    else:
        print("\n✓ No changes detected since last run")
