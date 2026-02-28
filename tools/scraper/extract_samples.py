#!/usr/bin/env python3
"""Extract sample data from forum HTML for reference."""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, Comment


@dataclass
class ExtractedTopic:
    """Represents a topic from forum index."""
    title: str = ""
    url: str = ""
    author: str = ""
    replies: int = 0
    views: int = 0
    last_post_time: str = ""


@dataclass
class ExtractedPost:
    """Represents a post within a topic."""
    post_id: str = ""
    author: str = ""
    timestamp: str = ""
    raw_content: str = ""
    clean_content: str = ""
    is_spoiler: bool = False
    has_strikethrough: bool = False


def extract_forum_topics(html_path: Path) -> list[ExtractedTopic]:
    """Extract topics from forum index page."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")

    topics: list[ExtractedTopic] = []

    selectors_to_try = [
        "li.row",
        "tr.row",
        "div.row",
        "div.topic-row",
        "div.topic-item",
    ]

    topic_rows = None
    for selector in selectors_to_try:
        topic_rows = soup.select(selector)
        if topic_rows:
            break

    if not topic_rows:
        topic_rows = soup.select("table.topiclist tr, div.topic-list div")

    for row in topic_rows[:20]:
        topic = ExtractedTopic()

        title_link = row.select_one("a.topictitle, a[href*='/topic/'], .topic-title a")
        if title_link:
            topic.title = title_link.get_text(strip=True)
            topic.url = title_link.get("href", "")

        author_link = row.select_one(".author, .username, a.username, .topic-author a")
        if author_link:
            topic.author = author_link.get_text(strip=True)

        replies_elem = row.select_one(".replies, .posts, .topic-replies")
        if replies_elem:
            try:
                topic.replies = int(replies_elem.get_text(strip=True).replace(",", ""))
            except ValueError:
                pass

        views_elem = row.select_one(".views, .topic-views")
        if views_elem:
            try:
                topic.views = int(views_elem.get_text(strip=True).replace(",", ""))
            except ValueError:
                pass

        time_elem = row.select_one(".lastpost time, .last-post time, .topic-last-post time")
        if time_elem:
            topic.last_post_time = time_elem.get("datetime") or time_elem.get_text(strip=True)

        if topic.title:
            topics.append(topic)

    return topics


def clean_content(html_content: str) -> tuple[str, bool, bool]:
    """Clean HTML content and detect spoilers/strikethrough."""
    soup = BeautifulSoup(html_content, "lxml")

    has_spoiler = bool(soup.select(".spoiler, .spoiler-hidden, [class*=spoiler]"))
    for spoiler in soup.select(".spoiler, .spoiler-hidden, [class*=spoiler]"):
        spoiler.decompose()

    has_strikethrough = bool(soup.select("strike, del, s, .strikethrough, [class*=strikethrough]"))

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for unwanted in soup.select("script, style, nav, header, footer, .signature"):
        unwanted.decompose()

    clean_text = soup.get_text(separator="\n", strip=True)

    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
    clean_text = clean_text.strip()

    return clean_text, has_spoiler, has_strikethrough


def extract_topic_posts(html_path: Path) -> list[ExtractedPost]:
    """Extract posts from topic page."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "lxml")

    posts: list[ExtractedPost] = []

    post_selectors = [
        "div.post",
        "div.post-container",
        "div.message",
        "div.postbody",
        "div.topic-post",
    ]

    post_elements = None
    for selector in post_selectors:
        post_elements = soup.select(selector)
        if post_elements:
            break

    if not post_elements:
        post_elements = soup.select("div[id^=post], div.post[id]")

    for post_elem in post_elements:
        post = ExtractedPost()

        post_id_elem = post_elem.select_one("[id^=post], .post-id, .post_number")
        if post_id_elem:
            post.post_id = post_id_elem.get("id", "") or post_id_elem.get_text(strip=True)

        author_elem = post_elem.select_one(".author, .username, .post-author, [itemprop=author]")
        if author_elem:
            post.author = author_elem.get_text(strip=True)

        time_elem = post_elem.select_one(".time, .post-time, time[datetime], .post-date")
        if time_elem:
            post.timestamp = time_elem.get("datetime") or time_elem.get_text(strip=True)

        content_selectors = [".content", ".post-content", ".postbody-content", ".message-content", ".post_text"]
        content_elem = None
        for selector in content_selectors:
            content_elem = post_elem.select_one(selector)
            if content_elem:
                break

        if not content_elem:
            content_elem = post_elem

        raw_html = str(content_elem)
        post.raw_content = raw_html

        clean_text, has_spoiler, has_strikethrough = clean_content(raw_html)
        post.clean_content = clean_text
        post.is_spoiler = has_spoiler
        post.has_strikethrough = has_strikethrough

        posts.append(post)

    return posts


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract sample data from forum HTML")
    parser.add_argument(
        "html_files",
        nargs="+",
        type=Path,
        help="HTML files to extract from",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("samples.json"),
        help="Output JSON file",
    )
    parser.add_argument(
        "--max-topics",
        type=int,
        default=10,
        help="Maximum topics to extract from index pages",
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=5,
        help="Maximum posts to extract from topic pages",
    )

    args = parser.parse_args()

    results = {
        "topics": [],
        "topic_posts": [],
    }

    for html_path in args.html_files:
        if not html_path.exists():
            print(f"File not found: {html_path}", file=sys.stderr)
            continue

        print(f"Extracting from: {html_path}")

        if "topic" in html_path.name.lower():
            posts = extract_topic_posts(html_path)
            results["topic_posts"].append({
                "file": str(html_path),
                "posts": [
                    {
                        "post_id": p.post_id,
                        "author": p.author,
                        "timestamp": p.timestamp,
                        "raw_content_preview": p.raw_content[:500],
                        "clean_content_preview": p.clean_content[:500],
                        "is_spoiler": p.is_spoiler,
                        "has_strikethrough": p.has_strikethrough,
                    }
                    for p in posts[:args.max_posts]
                ],
            })
        else:
            topics = extract_forum_topics(html_path)
            results["topics"].extend([
                {
                    "title": t.title,
                    "url": t.url,
                    "author": t.author,
                    "replies": t.replies,
                    "views": t.views,
                    "last_post_time": t.last_post_time,
                }
                for t in topics[:args.max_topics]
            ])

    args.output.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\nExtracted:")
    print(f"  - {len(results['topics'])} topics")
    print(f"  - {len(results['topic_posts'])} topic pages with posts")
    print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
