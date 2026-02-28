import logging
import re

from bs4 import BeautifulSoup, Comment

logger = logging.getLogger(__name__)


def clean_content(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "lxml")

    for spoiler in soup.select(".spoiler, .spoiler-hidden, [class*=spoiler]"):
        spoiler.decompose()

    for strikethrough in soup.select("strike, del, s, .strikethrough, [class*=strikethrough]"):
        strikethrough.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for unwanted in soup.select("script, style, nav, header, footer, .signature"):
        unwanted.decompose()

    clean_text = soup.get_text(separator="\n", strip=True)

    clean_text = re.sub(r"[ \t]+", " ", clean_text)
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
    clean_text = clean_text.strip()

    logger.debug(
        "Content cleaned",
        extra={"original_length": len(html_content), "clean_length": len(clean_text)},
    )

    return clean_text
