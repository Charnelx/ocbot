import logging
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup

from scraper.config import scraper_settings
from scraper.scraper.client import TopicSummary, extract_topic_id_from_url

logger = logging.getLogger(__name__)


@dataclass
class TopicPageData:
    raw_html: str
    created_at: str | None


@dataclass
class TopicData:
    external_id: str
    title: str
    url: str
    author: str
    raw_content: str
    last_update_at: str | None


def parse_forum_index(html: str) -> list[TopicSummary]:
    soup = BeautifulSoup(html, "lxml")
    topics: list[TopicSummary] = []

    selectors = [
        "dl.row",
        "li.row",
        "tr.row",
        "div.row",
        "div.topic-row",
        "div.topic-item",
    ]

    topic_rows = None
    for selector in selectors:
        topic_rows = soup.select(selector)
        if topic_rows:
            logger.debug("Found topic rows with selector", extra={"selector": selector})
            break

    if not topic_rows:
        topic_rows = soup.select("table.topiclist tr, div.topic-list div")

    for row in topic_rows:
        title_link = row.select_one("a.topictitle")
        if not title_link:
            title_link = row.select_one("a[href*='/topic/']")

        if not title_link:
            continue

        title = title_link.get_text(strip=True)
        url = title_link.get("href", "")[1:]
        url = scraper_settings.forum_base_domain + url

        if not url or not title:
            continue

        external_id = extract_topic_id_from_url(url)

        author_link = row.select_one("a.username, .author a, .username-colored")
        author = author_link.get_text(strip=True) if author_link else ""

        time_elem = row.select_one("time, .lastpost time, .last-post time")
        last_update_at = None
        if time_elem:
            last_update_at = time_elem.get("datetime") or time_elem.get_text(strip=True)

        row_classes = row.get("class", "") or ""
        if isinstance(row_classes, list):
            row_classes = " ".join(row_classes)
        is_closed = "topic_read_locked" in row_classes

        topics.append(
            TopicSummary(
                external_id=external_id,
                title=title,
                url=url,
                author=author,
                last_update_at=last_update_at,
                is_closed=is_closed,
            )
        )

    logger.info("Parsed forum index", extra={"topic_count": len(topics)})
    return topics


def parse_topic_page(html: str) -> TopicPageData:
    soup = BeautifulSoup(html, "lxml")

    post_selectors = [
        "div.post",
        "div.post-container",
        "div.message",
        "div.postbody",
        "div.topic-post",
    ]

    first_post = None
    for selector in post_selectors:
        first_post = soup.select_one(selector)
        if first_post:
            break

    if not first_post:
        first_post = soup.select_one("div[id^=post], div.post[id]")

    created_at = None
    if first_post:
        time_elem = first_post.select_one(".author time, .post-author time, time")
        if time_elem:
            created_at = time_elem.get("datetime") or time_elem.get_text(strip=True)

    if not first_post:
        logger.warning("No post found in topic page")
        return TopicPageData(raw_html="", created_at=None)

    content_selectors = [
        ".content",
        ".post-content",
        ".postbody-content",
        ".message-content",
        ".post_text",
    ]

    content_elem = None
    for selector in content_selectors:
        content_elem = first_post.select_one(selector)
        if content_elem:
            break

    if not content_elem:
        content_elem = first_post

    raw_html = str(content_elem)
    logger.debug("Parsed topic page", extra={"post_count": 1, "created_at": created_at})
    return TopicPageData(raw_html=raw_html, created_at=created_at)
