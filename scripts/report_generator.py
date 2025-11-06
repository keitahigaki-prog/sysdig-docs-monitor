#!/usr/bin/env python3
"""
Japanese Report Generator using Claude API
Analyzes Sysdig documentation changes and generates customer-ready reports in Japanese
"""

import anthropic
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class JapaneseReportGenerator:
    def __init__(self, api_key: str = None, reports_dir: str = "reports"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)

    def analyze_with_claude(self, content: str, content_type: str) -> str:
        """Analyze content using Claude API and generate Japanese summary"""

        system_prompt = """あなたはSysdig製品の技術ドキュメント専門家です。
お客様向けの分かりやすい日本語レポートを作成してください。

以下の観点で分析してください:
1. 重要度（Critical/High/Medium/Low）を判定
2. 技術的な内容を分かりやすく要約
3. お客様への影響を説明
4. 必要なアクション（ある場合）を明確に記載

出力形式:
### [重要度] タイトル

**概要:**
（日本語で簡潔に）

**詳細:**
- ポイント1
- ポイント2

**お客様への影響:**
（具体的な影響を記載）

**推奨アクション:**
（必要に応じて）

---
"""

        user_prompt = f"""以下の{content_type}を分析して、お客様向けの日本語レポートを作成してください。

内容:
{content}

専門用語は必要に応じて日本語訳の後にカッコ書きで英語を併記してください。
セキュリティやEOL（サポート終了）に関する情報は特に重要度を高く評価してください。
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return f"**エラー:** Claude APIの呼び出しに失敗しました: {str(e)}"

    def generate_rss_analysis(self, feed_name: str, entries: List[Dict[str, Any]]) -> str:
        """Generate analysis for RSS feed entries"""
        if not entries:
            return ""

        content = f"RSS Feed: {feed_name}\n\n"
        for i, entry in enumerate(entries[:3], 1):  # Top 3 entries
            content += f"Entry {i}:\n"
            content += f"Title: {entry.get('title', 'N/A')}\n"
            content += f"Published: {entry.get('published', 'N/A')}\n"
            content += f"Summary: {entry.get('summary', 'N/A')}\n"
            content += f"Link: {entry.get('link', 'N/A')}\n\n"

        return self.analyze_with_claude(content, f"RSSフィード（{feed_name}）")

    def generate_webpage_analysis(self, page_name: str, page_data: Dict[str, Any]) -> str:
        """Generate analysis for web page content"""
        if "error" in page_data:
            return f"**エラー:** {page_data['error']}"

        content = f"Web Page: {page_name}\n"
        content += f"URL: {page_data.get('url', 'N/A')}\n\n"

        if "headings" in page_data:
            content += "主要セクション:\n"
            for heading in page_data["headings"]:
                content += f"- {heading.get('text', '')}\n"
            content += "\n"

        if "text_preview" in page_data:
            content += f"コンテンツプレビュー:\n{page_data['text_preview']}\n"

        return self.analyze_with_claude(content, f"Webページ（{page_name}）")

    def generate_full_report(self, monitoring_result: Dict[str, Any]) -> str:
        """Generate complete Japanese report"""
        current_data = monitoring_result["current_data"]
        changes = monitoring_result["changes"]

        timestamp = datetime.fromisoformat(current_data["timestamp"])

        report = f"""# Sysdig ドキュメント監視レポート

**レポート日時:** {timestamp.strftime('%Y年%m月%d日 %H:%M:%S')}
**変更検出:** {'あり ⚠️' if changes['has_changes'] else 'なし ✓'}

---

## エグゼクティブサマリー

"""

        # Generate executive summary using Claude
        summary_content = {
            "has_changes": changes["has_changes"],
            "rss_changes_count": len(changes.get("rss_changes", {})),
            "web_changes_count": len(changes.get("web_changes", {})),
            "feeds": list(current_data["rss_feeds"].keys()),
            "pages": list(current_data["web_pages"].keys())
        }

        summary_prompt = f"""以下の監視結果のエグゼクティブサマリーを3-5文で日本語で作成してください:

{json.dumps(summary_content, indent=2, ensure_ascii=False)}

変更があった場合は特に注意を促し、変更がない場合は安定稼働中であることを伝えてください。
"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=512,
                temperature=0,
                messages=[
                    {"role": "user", "content": summary_prompt}
                ]
            )
            report += message.content[0].text + "\n\n"
        except Exception as e:
            report += f"監視を実行しました。変更検出: {changes['has_changes']}\n\n"

        report += "---\n\n"

        # Analyze RSS feeds if there are changes
        if changes.get("rss_changes"):
            report += "## 📡 RSSフィード更新情報\n\n"

            for feed_name in changes["rss_changes"]:
                if feed_name in current_data["rss_feeds"]:
                    entries = current_data["rss_feeds"][feed_name]
                    report += self.generate_rss_analysis(feed_name, entries)
                    report += "\n\n"

        # Analyze web pages if there are changes
        if changes.get("web_changes"):
            report += "## 🌐 Webページ更新情報\n\n"

            for page_name in changes["web_changes"]:
                if page_name in current_data["web_pages"]:
                    page_data = current_data["web_pages"][page_name]
                    report += self.generate_webpage_analysis(page_name, page_data)
                    report += "\n\n"

        # If no changes, still provide status of monitored sources
        if not changes["has_changes"]:
            report += "## 📊 監視対象ステータス\n\n"
            report += "### RSSフィード\n\n"

            for feed_name, entries in current_data["rss_feeds"].items():
                if entries:
                    latest = entries[0]
                    report += f"- **{feed_name}**: 最新エントリー「{latest.get('title', 'N/A')}」（{latest.get('published', 'N/A')}）\n"
                else:
                    report += f"- **{feed_name}**: エントリーなし\n"

            report += "\n### Webページ\n\n"

            for page_name, page_data in current_data["web_pages"].items():
                if "error" in page_data:
                    report += f"- **{page_name}**: エラー（{page_data['error']}）\n"
                else:
                    report += f"- **{page_name}**: 正常に取得\n"

        report += "\n---\n\n"
        report += "## 📎 参考リンク\n\n"
        report += "- [Sysdig Release Notes](https://docs.sysdig.com/en/release-notes/)\n"
        report += "- [Linux Host Shield Release Notes](https://docs.sysdig.com/en/release-notes/linux-host-shield-release-notes/)\n"
        report += "- [Deprecation Notice](https://docs.sysdig.com/en/deprecation/)\n"
        report += "\n---\n\n"
        report += f"*このレポートは自動生成されました（Claude API使用）*\n"

        return report

    def save_report(self, report: str, filename: str = None) -> str:
        """Save report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sysdig_report_{timestamp}.md"

        filepath = self.reports_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Report saved: {filepath}")
        return str(filepath)

def main():
    """Main function to generate report from latest monitoring data"""
    import sys

    # Load monitoring result
    data_file = Path("data/latest.json")
    if not data_file.exists():
        print("Error: No monitoring data found. Run monitor.py first.")
        sys.exit(1)

    with open(data_file, 'r', encoding='utf-8') as f:
        latest_data = json.load(f)

    # Mock up changes structure if not present
    monitoring_result = {
        "current_data": latest_data,
        "changes": {
            "has_changes": False,
            "rss_changes": {},
            "web_changes": {}
        }
    }

    # Check for changes file
    changes_files = sorted(Path("data").glob("changes_*.json"))
    if changes_files:
        latest_changes = changes_files[-1]
        with open(latest_changes, 'r', encoding='utf-8') as f:
            changes_data = json.load(f)
            monitoring_result["changes"] = changes_data.get("changes", monitoring_result["changes"])

    # Generate report
    try:
        generator = JapaneseReportGenerator()
        report = generator.generate_full_report(monitoring_result)
        filepath = generator.save_report(report)
        print(f"\n✓ Japanese report generated successfully: {filepath}")

    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
