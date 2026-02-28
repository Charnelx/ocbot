from scraper.ingestion.cleaner import clean_content


class TestCleanContent:
    def test_removes_spoiler_tags(self):
        html = """
        <div>Normal content here</div>
        <div class="spoiler">Hidden content</div>
        <div class="spoiler-hidden">Also hidden</div>
        """
        result = clean_content(html)
        assert "Hidden content" not in result
        assert "Normal content here" in result

    def test_removes_spoiler_by_class_pattern(self):
        html = """
        <div>Visible</div>
        <div class="spoiler-123">Hidden</div>
        <div class="my-spoiler">Also hidden</div>
        """
        result = clean_content(html)
        assert "Hidden" not in result
        assert "Visible" in result

    def test_removes_strikethrough(self):
        html = """
        <div>Available item</div>
        <strike>Sold item</strike>
        <del>Also sold</del>
        <s>Old price</s>
        <span class="strikethrough">Crossed out</span>
        """
        result = clean_content(html)
        assert "Sold item" not in result
        assert "Also sold" not in result
        assert "Old price" not in result
        assert "Crossed out" not in result
        assert "Available item" in result

    def test_removes_scripts_and_styles(self):
        html = """
        <script>alert('evil')</script>
        <style>.evil{display:none}</style>
        <div>Good content</div>
        """
        result = clean_content(html)
        assert "alert" not in result
        assert ".evil" not in result
        assert "Good content" in result

    def test_removes_unwanted_elements(self):
        html = """
        <nav>Navigation</nav>
        <header>Header</header>
        <footer>Footer</footer>
        <div class="signature">Signature text</div>
        <div>Main content</div>
        """
        result = clean_content(html)
        assert "Navigation" not in result
        assert "Header" not in result
        assert "Footer" not in result
        assert "Signature text" not in result
        assert "Main content" in result

    def test_removes_comments(self):
        html = """
        <div>Content</div>
        <!-- This is a comment -->
        <div>More content</div>
        """
        result = clean_content(html)
        assert "This is a comment" not in result

    def test_normalizes_whitespace(self):
        html = "<div>Content   with    extra    spaces</div>"
        result = clean_content(html)
        assert "  " not in result
        assert "Content with extra spaces" in result

    def test_normalizes_multiple_newlines(self):
        html = "<div>Line 1</div>\n\n\n\n<div>Line 2</div>\n\n\n\n\n<div>Line 3</div>"
        result = clean_content(html)
        assert "\n\n\n\n" not in result

    def test_handles_empty_input(self):
        result = clean_content("")
        assert result == ""

    def test_handles_plain_text(self):
        result = clean_content("Just plain text")
        assert result == "Just plain text"

    def test_handles_unicode_content(self):
        html = "<div>Ukrainian: Проба Russian: Тест English: Test</div>"
        result = clean_content(html)
        assert "Проба" in result
        assert "Тест" in result
        assert "Test" in result

    def test_strips_leading_trailing_whitespace(self):
        html = "   <div>   Content   </div>   "
        result = clean_content(html)
        assert result == "Content"
