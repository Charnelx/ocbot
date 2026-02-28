import pytest
from pydantic import ValidationError

from enrichment.extraction.schemas import (
    ExtractionResult,
    ExtractedItem,
    ItemCategory,
    ItemCurrency,
)


class TestExtractedItem:
    def test_valid_extracted_item(self):
        item = ExtractedItem(
            title="Intel Core i7-12700K",
            raw_text_segment="Intel Core i7-12700K - 5000 UAH",
            category=ItemCategory.cpu,
            labels=["intel", "core-i7", "12th-gen"],
            price=5000.0,
            currency=ItemCurrency.UAH,
        )
        assert item.title == "Intel Core i7-12700K"
        assert item.category == ItemCategory.cpu

    def test_valid_item_without_price(self):
        item = ExtractedItem(
            title="Intel Core i7-12700K",
            raw_text_segment="Intel Core i7-12700K",
            category=ItemCategory.cpu,
            labels=["intel", "core-i7"],
            price=None,
            currency=None,
        )
        assert item.price is None
        assert item.currency is None

    def test_valid_item_with_usd(self):
        item = ExtractedItem(
            title="ASUS ROG STRIX RTX 3080",
            raw_text_segment="ASUS ROG STRIX RTX 3080 - $150",
            category=ItemCategory.gpu,
            labels=["asus", "rog-strix", "rtx-3080"],
            price=150.0,
            currency=ItemCurrency.USD,
        )
        assert item.currency == ItemCurrency.USD

    def test_valid_item_with_eur(self):
        item = ExtractedItem(
            title="AMD Ryzen 7 5800X3D",
            raw_text_segment="AMD Ryzen 7 5800X3D - 200 EUR",
            category=ItemCategory.cpu,
            labels=["amd", "ryzen-7", "5800x3d"],
            price=200.0,
            currency=ItemCurrency.EUR,
        )
        assert item.currency == ItemCurrency.EUR

    def test_invalid_category_raises_error(self):
        with pytest.raises(ValidationError):
            ExtractedItem(
                title="Test Item",
                raw_text_segment="Test",
                category="invalid_category",
                labels=["test"],
                price=100.0,
                currency=ItemCurrency.UAH,
            )

    def test_price_negative_fails(self):
        with pytest.raises(ValidationError):
            ExtractedItem(
                title="Test Item",
                raw_text_segment="Test",
                category=ItemCategory.cpu,
                labels=["test"],
                price=-100.0,
                currency=ItemCurrency.UAH,
            )

    def test_price_zero_allowed(self):
        item = ExtractedItem(
            title="Free Item",
            raw_text_segment="Free item",
            category=ItemCategory.cpu,
            labels=["test"],
            price=0.0,
            currency=ItemCurrency.UAH,
        )
        assert item.price == 0.0

    def test_empty_labels_fails(self):
        with pytest.raises(ValidationError):
            ExtractedItem(
                title="Test Item",
                raw_text_segment="Test",
                category=ItemCategory.cpu,
                labels=[],
                price=100.0,
                currency=ItemCurrency.UAH,
            )

    def test_single_label_allowed(self):
        item = ExtractedItem(
            title="Test Item",
            raw_text_segment="Test",
            category=ItemCategory.cpu,
            labels=["intel"],
            price=100.0,
            currency=ItemCurrency.UAH,
        )
        assert len(item.labels) == 1

    def test_currency_mapping_uah_variants(self):
        item = ExtractedItem(
            title="Test",
            raw_text_segment="Test",
            category=ItemCategory.cpu,
            labels=["test"],
            price=100.0,
            currency=ItemCurrency.UAH,
        )
        assert item.currency == ItemCurrency.UAH


class TestExtractionResult:
    def test_extraction_result_with_items(self, sample_extracted_items):
        result = ExtractionResult(items=sample_extracted_items)
        assert len(result.items) == 2
        assert result.items[0].title == "Intel Core i7-12700K"

    def test_extraction_result_empty(self):
        result = ExtractionResult(items=[])
        assert len(result.items) == 0

    def test_extraction_result_single_item(self):
        item = ExtractedItem(
            title="Intel Core i7-12700K",
            raw_text_segment="Test",
            category=ItemCategory.cpu,
            labels=["intel"],
            price=100.0,
            currency=ItemCurrency.UAH,
        )
        result = ExtractionResult(items=[item])
        assert len(result.items) == 1


class TestItemCategory:
    def test_all_categories_valid(self):
        for category in ItemCategory:
            item = ExtractedItem(
                title="Test",
                raw_text_segment="Test",
                category=category,
                labels=["test"],
                price=100.0,
                currency=ItemCurrency.UAH,
            )
            assert item.category == category


class TestItemCurrency:
    def test_all_currencies_valid(self):
        for currency in ItemCurrency:
            item = ExtractedItem(
                title="Test",
                raw_text_segment="Test",
                category=ItemCategory.cpu,
                labels=["test"],
                price=100.0,
                currency=currency,
            )
            assert item.currency == currency
