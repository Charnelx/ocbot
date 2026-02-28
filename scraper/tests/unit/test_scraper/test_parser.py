from scraper.scraper.parser import parse_forum_index, parse_topic_page


class TestParseForumIndex:
    def test_parses_topics_from_html(self, forum_index_html):
        topics = parse_forum_index(forum_index_html)

        assert len(topics) > 0
        topic = topics[0]
        assert topic.external_id
        assert topic.title
        assert topic.url
        assert topic.author is not None

    def test_returns_empty_list_for_empty_html(self):
        topics = parse_forum_index("<html><body></body></html>")
        assert topics == []

    def test_handles_missing_author(self):
        html = """
        <html>
            <dl class="row">
                <a class="topictitle" href="/topic/123">Test Title</a>
            </dl>
        </html>
        """
        topics = parse_forum_index(html)
        assert len(topics) == 1
        assert topics[0].author == ""

    def test_handles_missing_time(self):
        html = """
        <html>
            <dl class="row">
                <a class="topictitle" href="/topic/123">Test Title</a>
                <a class="username" href="#">Author</a>
            </dl>
        </html>
        """
        topics = parse_forum_index(html)
        assert len(topics) == 1
        assert topics[0].last_update_at is None

    def test_parses_multiple_topics(self, forum_index_html):
        topics = parse_forum_index(forum_index_html)
        assert len(topics) >= 3

    def test_topic_has_valid_external_id(self, forum_index_html):
        topics = parse_forum_index(forum_index_html)
        for topic in topics:
            assert topic.external_id.isdigit() or topic.external_id

    def test_topic_url_contains_base_domain(self, forum_index_html):
        topics = parse_forum_index(forum_index_html)
        for topic in topics:
            assert "forum.overclockers.ua" in topic.url


class TestParseTopicPage:
    def test_extracts_post_content(self, topic_page_html):
        result = parse_topic_page(topic_page_html)

        assert result
        assert len(result) > 0

    def test_returns_empty_for_no_posts(self):
        result = parse_topic_page("<html><body>No posts here</body></html>")
        assert result == ""

    def test_handles_multiple_posts(self):
        html = """
        <html>
            <div class="post">
                <div class="content">First post content</div>
            </div>
            <div class="post">
                <div class="content">Second post content</div>
            </div>
        </html>
        """
        result = parse_topic_page(html)

        assert "First post content" in result
        assert "Second post content" in result

    def test_uses_post_body_as_fallback(self):
        html = """
        <html>
            <div class="post">
                Direct content here
            </div>
        </html>
        """
        result = parse_topic_page(html)

        assert "Direct content here" in result

    def test_handles_different_content_selectors(self):
        html = """
        <html>
            <div class="post">
                <div class="post-content">Post content 1</div>
            </div>
            <div class="post">
                <div class="postbody-content">Post content 2</div>
            </div>
            <div class="post">
                <div class="message-content">Post content 3</div>
            </div>
        </html>
        """
        result = parse_topic_page(html)

        assert "Post content 1" in result
        assert "Post content 2" in result
        assert "Post content 3" in result

    def test_handles_post_text_class(self):
        html = """
        <html>
            <div class="post">
                <div class="post_text">Post text content</div>
            </div>
        </html>
        """
        result = parse_topic_page(html)

        assert "Post text content" in result


class TestTopicData:
    def test_topic_data_creation(self):
        from scraper.scraper.parser import TopicData

        topic = TopicData(
            external_id="123",
            title="Test Title",
            url="https://forum.overclockers.ua/topic/123",
            author="test_user",
            raw_content="<html>content</html>",
            last_update_at="2024-01-15T10:30:00Z",
        )
        assert topic.external_id == "123"
        assert topic.title == "Test Title"
        assert topic.raw_content == "<html>content</html>"
