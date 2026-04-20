"""Unit tests for helper functions.

Run with:
    pytest tests/test_helpers.py
"""

import xml.etree.ElementTree as ET
import pytest
from app.helpers.response import _to_xml_element, to_xml_string
from app.routers.countries import _count_medals
from app.routers.sports import _aggregate_medals


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class MockRow:
    """Minimal stand-in for an AthleteEvent row used in aggregation tests."""

    def __init__(self, sport: str, medal: str, noc: str = "NOR", year: int = 2014):
        self.sport = sport
        self.medal = medal
        self.noc = noc
        self.year = year


# ---------------------------------------------------------------------------
# _to_xml_element
# ---------------------------------------------------------------------------

class TestToXmlElement:
    """Tests for the recursive XML element builder."""

    def test_simple_dict_structure(self):
        elem = _to_xml_element({"key": "value"}, "root")
        assert elem.tag == "root"
        child = elem.find("key")
        assert child is not None
        assert child.text == "value"

    def test_nested_dict(self):
        elem = _to_xml_element({"outer": {"inner": "val"}}, "root")
        inner = elem.find("outer/inner")
        assert inner is not None
        assert inner.text == "val"

    def test_list_creates_item_elements(self):
        elem = _to_xml_element([1, 2, 3], "root")
        items = elem.findall("item")
        assert len(items) == 3
        assert items[0].text == "1"
        assert items[2].text == "3"

    def test_none_value_becomes_empty_string(self):
        elem = _to_xml_element(None, "tag")
        assert elem.text == ""

    def test_numeric_value_is_stringified(self):
        elem = _to_xml_element(42, "num")
        assert elem.text == "42"

    def test_spaces_in_tag_replaced_with_underscores(self):
        elem = _to_xml_element("x", "my tag")
        assert elem.tag == "my_tag"


# ---------------------------------------------------------------------------
# to_xml_string
# ---------------------------------------------------------------------------

class TestToXmlString:
    """Tests for the dict-to-XML-string converter."""

    def test_returns_string(self):
        result = to_xml_string({"foo": "bar"})
        assert isinstance(result, str)

    def test_produces_valid_xml(self):
        result = to_xml_string({"foo": "bar"})
        root = ET.fromstring(result)  # raises if invalid XML
        assert root.tag == "response"

    def test_custom_root_tag(self):
        result = to_xml_string({"x": "1"}, root_tag="data")
        root = ET.fromstring(result)
        assert root.tag == "data"

    def test_empty_dict_is_valid_xml(self):
        result = to_xml_string({})
        assert ET.fromstring(result) is not None

    def test_list_input(self):
        result = to_xml_string([1, 2])
        root = ET.fromstring(result)
        assert len(root.findall("item")) == 2


# ---------------------------------------------------------------------------
# _count_medals (countries router)
# ---------------------------------------------------------------------------

class TestCountMedals:
    """Tests for the per-sport medal aggregation used by the country endpoint."""

    def test_counts_gold_medals(self):
        rows = [MockRow("Swimming", "Gold"), MockRow("Swimming", "Gold")]
        result = _count_medals(rows)
        assert result["Swimming"]["gold"] == 2

    def test_counts_silver_and_bronze(self):
        rows = [MockRow("Athletics", "Silver"), MockRow("Athletics", "Bronze")]
        result = _count_medals(rows)
        assert result["Athletics"]["silver"] == 1
        assert result["Athletics"]["bronze"] == 1

    def test_none_medal_counted_as_na(self):
        rows = [MockRow("Gymnastics", None)]
        result = _count_medals(rows)
        assert result["Gymnastics"]["na"] == 1

    def test_total_reflects_all_rows(self):
        rows = [MockRow("Rowing", "Gold"), MockRow("Rowing", None)]
        result = _count_medals(rows)
        assert result["Rowing"]["total"] == 2

    def test_multiple_sports_separated(self):
        rows = [MockRow("Swimming", "Gold"), MockRow("Athletics", "Silver")]
        result = _count_medals(rows)
        assert "Swimming" in result
        assert "Athletics" in result
        assert result["Swimming"]["gold"] == 1
        assert result["Athletics"]["silver"] == 1

    def test_empty_rows_returns_empty_dict(self):
        result = _count_medals([])
        assert result == {}


# ---------------------------------------------------------------------------
# _aggregate_medals (sports router)
# ---------------------------------------------------------------------------

class TestAggregateMedals:
    """Tests for the medal aggregation used by the sport endpoint."""

    def test_total_equals_row_count(self):
        rows = [MockRow("Ski", "Gold"), MockRow("Ski", "Silver")]
        result = _aggregate_medals(rows)
        assert result["total"] == 2

    def test_all_medal_types_counted(self):
        rows = [
            MockRow("Ski", "Gold"),
            MockRow("Ski", "Silver"),
            MockRow("Ski", "Bronze"),
            MockRow("Ski", None),
        ]
        result = _aggregate_medals(rows)
        assert result["gold"] == 1
        assert result["silver"] == 1
        assert result["bronze"] == 1
        assert result["na"] == 1

    def test_empty_rows(self):
        result = _aggregate_medals([])
        assert result["total"] == 0
        assert result["gold"] == 0

    def test_all_na_when_no_medals(self):
        rows = [MockRow("Archery", None) for _ in range(5)]
        result = _aggregate_medals(rows)
        assert result["na"] == 5
        assert result["gold"] == 0
