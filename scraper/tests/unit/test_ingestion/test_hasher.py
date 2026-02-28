from scraper.ingestion.hasher import compute_hash


class TestComputeHash:
    def test_returns_sha256_hexdigest(self):
        result = compute_hash("test content")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic_output(self):
        content = "same content"
        hash1 = compute_hash(content)
        hash2 = compute_hash(content)
        assert hash1 == hash2

    def test_different_inputs_different_hashes(self):
        hash1 = compute_hash("content A")
        hash2 = compute_hash("content B")
        assert hash1 != hash2

    def test_handles_unicode(self):
        result = compute_hash("Ukrainian: Проба Russian: Тест")
        assert len(result) == 64

    def test_handles_unicode_mixed(self):
        result = compute_hash("English Ukrainian Русский")
        assert len(result) == 64

    def test_handles_empty_string(self):
        result = compute_hash("")
        assert len(result) == 64

    def test_handles_large_content(self):
        large = "x" * 1_000_000
        result = compute_hash(large)
        assert len(result) == 64

    def test_handles_special_characters(self):
        result = compute_hash("!@#$%^&*()_+-=[]{}|;':\",./<>?")
        assert len(result) == 64

    def test_handles_newlines_and_tabs(self):
        result = compute_hash("line1\nline2\ttabbed")
        assert len(result) == 64

    def test_handles_single_character(self):
        result = compute_hash("a")
        assert len(result) == 64

    def test_known_hash_value(self):
        result = compute_hash("hello")
        assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
