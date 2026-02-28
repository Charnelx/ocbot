#!/usr/bin/env python3
"""Analyze HTML structure of forum pages to understand selectors and patterns."""

import argparse
import json
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup


def analyze_forum_index(html_path: Path) -> dict:
    """Analyze forum index page structure."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")

    results = {
        "file": str(html_path),
        "type": "forum_index",
        "structure": {},
    }

    results["structure"]["all_ids"] = list(set(
        tag.get("id") for tag in soup.find_all(id=True)
    ))

    results["structure"]["common_classes"] = Counter(
        cls for tag in soup.find_all(class_=True) for cls in tag.get("class", [])
    ).most_common(20)

    topic_rows = soup.select("li.row, tr.row, div.row, div.topic-row")
    if not topic_rows:
        topic_rows = soup.select("table.topiclist tr, div.topic-list div")

    topics = []
    for row in topic_rows[:10]:
        topic_info = {
            "selectors_used": list(row.get("class", [])),
            "has_id": bool(row.get("id")),
            "children": [],
        }

        for child in row.children:
            if hasattr(child, "name") and child.name:
                child_info = {
                    "tag": child.name,
                    "classes": child.get("class", []),
                    "text_preview": child.get_text(strip=True)[:100] if child.get_text() else None,
                }
                links = child.find_all("a", href=True)
                if links:
                    child_info["links"] = [
                        {"text": a.get_text(strip=True)[:50], "href": a.get("href")}
                        for a in links[:3]
                    ]
                topic_info["children"].append(child_info)

        topics.append(topic_info)

    results["structure"]["sample_topics"] = topics

    links = soup.find_all("a", href=True)
    topic_links = [a for a in links if "/topic/" in a.get("href", "")]
    if topic_links:
        results["structure"]["sample_topic_link"] = {
            "text": topic_links[0].get_text(strip=True),
            "href": topic_links[0].get("href"),
            "classes": topic_links[0].get("class", []),
        }

    return results


def analyze_topic_page(html_path: Path) -> dict:
    """Analyze single topic page structure."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")

    results = {
        "file": str(html_path),
        "type": "topic",
        "structure": {},
    }

    results["structure"]["all_ids"] = list(set(
        tag.get("id") for tag in soup.find_all(id=True)
    ))

    results["structure"]["common_classes"] = Counter(
        cls for tag in soup.find_all(class_=True) for cls in tag.get("class", [])
    ).most_common(30)

    post_selectors = [
        "div.post",
        "div.post-container",
        "div.message",
        "div.postbody",
        "div.topic-post",
    ]
    posts = None
    for selector in post_selectors:
        posts = soup.select(selector)
        if posts:
            results["structure"]["post_selector"] = selector
            break

    if posts:
        sample_posts = []
        for post in posts[:3]:
            post_info = {
                "selectors": post.get("class", []),
                "id": post.get("id"),
            }

            post_id_elem = post.select_one("[id^=post], .post-id, .post_number")
            if post_id_elem:
                post_info["post_id_element"] = {
                    "tag": post_id_elem.name,
                    "classes": post_id_elem.get("class", []),
                    "id": post_id_elem.get("id"),
                    "text": post_id_elem.get_text(strip=True),
                }

            author_elem = post.select_one(".author, .username, .post-author, [itemprop=author]")
            if author_elem:
                post_info["author"] = {
                    "tag": author_elem.name,
                    "classes": author_elem.get("class", []),
                    "text": author_elem.get_text(strip=True),
                }

            content_elem = post.select_one(".content, .post-content, .postbody-content, .message-content")
            if content_elem:
                raw_html = str(content_elem)[:500]
                clean_text = content_elem.get_text(separator=" ", strip=True)[:200]
                post_info["content"] = {
                    "classes": content_elem.get("class", []),
                    "raw_html_preview": raw_html,
                    "clean_text_preview": clean_text,
                }

            time_elem = post.select_one(".time, .post-time, time[datetime], .post-date")
            if time_elem:
                post_info["timestamp"] = {
                    "tag": time_elem.name,
                    "classes": time_elem.get("class", []),
                    "datetime_attr": time_elem.get("datetime"),
                    "text": time_elem.get_text(strip=True),
                }

            sample_posts.append(post_info)

        results["structure"]["sample_posts"] = sample_posts

    spoiler_elements = soup.select(".spoiler, .spoiler-hidden, [class*=spoiler]")
    if spoiler_elements:
        results["structure"]["spoiler_found"] = True
        results["structure"]["spoiler_classes"] = list({
            tuple(cls) for el in spoiler_elements for cls in el.get("class", [])
        })[:5]
    else:
        results["structure"]["spoiler_found"] = False

    strikethrough = soup.select("strike, del, s, .strikethrough, [class*=strikethrough]")
    if strikethrough:
        results["structure"]["strikethrough_found"] = True
        results["structure"]["strikethrough_tags"] = list(set(el.name for el in strikethrough))[:5]
    else:
        results["structure"]["strikethrough_found"] = False

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze HTML structure of forum pages")
    parser.add_argument(
        "html_files",
        nargs="+",
        type=Path,
        help="HTML files to analyze",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON file (optional)",
    )

    args = parser.parse_args()

    all_results = []

    for html_path in args.html_files:
        if not html_path.exists():
            print(f"File not found: {html_path}")
            continue

        print(f"Analyzing: {html_path}")

        if "topic" in html_path.name.lower():
            results = analyze_topic_page(html_path)
        else:
            results = analyze_forum_index(html_path)

        all_results.append(results)
        print(json.dumps(results, indent=2, ensure_ascii=False))

    if args.output:
        args.output.write_text(
            json.dumps(all_results, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"\nSaved analysis to: {args.output}")


if __name__ == "__main__":
    main()
