import pytest

from enrichment.extraction.prompt import SYSTEM_PROMPT, build_user_message


class TestBuildUserMessage:
    def test_build_user_message_format(self):
        topic_title = "Продам Intel Core i7-12700K"
        clean_content = "Продам процессор Intel Core i7-12700K, цена 5000 грн"

        result = build_user_message(topic_title, clean_content)

        assert result.startswith("Topic title: Продам Intel Core i7-12700K")
        assert "Post content:" in result
        assert "```" in result
        assert "Продам процессор Intel Core i7-12700K, цена 5000 грн" in result

    def test_build_user_message_multiline_content(self):
        topic_title = "Тестовая тема"
        clean_content = "Строка 1\nСтрока 2\nСтрока 3"

        result = build_user_message(topic_title, clean_content)

        assert "Строка 1" in result
        assert "Строка 2" in result
        assert "Строка 3" in result

    def test_build_user_message_empty_content(self):
        topic_title = "Тестовая тема"
        clean_content = ""

        result = build_user_message(topic_title, clean_content)

        assert "Topic title: Тестовая тема" in result
        assert "Post content:" in result


class TestSystemPrompt:
    def test_system_prompt_not_empty(self):
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 0

    def test_system_prompt_contains_instructions(self):
        assert "structured data extractor" in SYSTEM_PROMPT.lower()
        assert "overclockers.ua" in SYSTEM_PROMPT.lower()

    def test_system_prompt_contains_categories(self):
        assert "cpu" in SYSTEM_PROMPT.lower()
        assert "gpu" in SYSTEM_PROMPT.lower()
        assert "motherboard" in SYSTEM_PROMPT.lower()

    def test_system_prompt_contains_output_format(self):
        assert "json" in SYSTEM_PROMPT.lower()
        assert "items" in SYSTEM_PROMPT.lower()

    def test_system_prompt_contains_currency_rules(self):
        assert "UAH" in SYSTEM_PROMPT
        assert "USD" in SYSTEM_PROMPT
        assert "EUR" in SYSTEM_PROMPT
