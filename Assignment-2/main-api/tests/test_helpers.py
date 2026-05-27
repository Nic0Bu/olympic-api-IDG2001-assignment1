"""Unit tests for helper functions.

Run with:
    pytest tests/test_helpers.py
"""

import xml.etree.ElementTree as ET
from app.helpers.response import _to_xml_element, to_xml_string, to_csv_string
from app.routers.countries import _count_medals
from app.routers.sports import _aggregate_medals


class MockRow:
    """Minimal stand-in for an AthleteEvent row."""

    def __init__(self, sport: str, medal: str, noc: str = "NOR", year: int = 2014):
        self.sport = sport
        self.medal = medal
        self.noc = noc
        self.year = year


# ---------------------------------------------------------------------------
# _to_xml_element
# ---------------------------------------------------------------------------

class TestToXmlElement:

    def test_simple_dict(self):
        elem = _to_xml_element({"key": "value"}, "root")
        assert elem.tag == "root"
        child = elem.find("key")
        assert child is not None
        assert child.text == "value"

    def test_nested_dict(self):
        elem = _to_xml_element({"outer": {"inner": "val"}}, "root")
        assert elem.find("outer/inner").text == "val"

    def test_list_becomes_items(self):
        elem = _to_xml_element([1, 2, 3], "root")
        items = elem.findall("item")
        assert len(items) == 3
        assert items[0].text == "1"

    def test_none_becomes_empty_string(self):
        elem = _to_xml_element(None, "tag")
        assert elem.text == ""

    def test_int_stringified(self):
        elem = _to_xml_element(42, "num")
        assert elem.text == "42"

    def test_spaces_in_tag_replaced(self):
        elem = _to_xml_element("x", "my tag")
        assert elem.tag == "my_tag"


# ---------------------------------------------------------------------------
# to_xml_string
# ---------------------------------------------------------------------------

class TestToXmlString:

    def test_returns_string(self):
        assert isinstance(to_xml_string({"a": "b"}), str)

    def test_valid_xml(self):
        root = ET.fromstring(to_xml_string({"foo": "bar"}))
        assert root.tag == "response"

    def test_custom_root_tag(self):
        root = ET.fromstring(to_xml_string({"x": "1"}, root_tag="data"))
        assert root.tag == "data"

    def test_empty_dict(self):
        assert ET.fromstring(to_xml_string({})) is not None

    def test_list_input(self):
        root = ET.fromstring(to_xml_string([1, 2]))
        assert len(root.findall("item")) == 2


# ---------------------------------------------------------------------------
# to_csv_string
# ---------------------------------------------------------------------------

class TestToCsvString:

    def test_dict_produces_csv(self):
        result = to_csv_string({"a": 1, "b": 2})
        assert "a" in result
        assert "1" in result

    def test_list_of_dicts(self):
        result = to_csv_string([{"x": 1}, {"x": 2}])
        lines = result.strip().splitlines()
        # header + 2 rows
        assert len(lines) == 3

    def test_empty_list_returns_empty(self):
        assert to_csv_string([]) == ""


# ---------------------------------------------------------------------------
# _count_medals
# ---------------------------------------------------------------------------

class TestCountMedals:

    def test_gold_counted(self):
        rows = [MockRow("Swimming", "Gold"), MockRow("Swimming", "Gold")]
        result = _count_medals(rows)
        assert result["Swimming"]["gold"] == 2

    def test_silver_and_bronze(self):
        rows = [MockRow("Athletics", "Silver"), MockRow("Athletics", "Bronze")]
        result = _count_medals(rows)
        assert result["Athletics"]["silver"] == 1
        assert result["Athletics"]["bronze"] == 1

    def test_none_counted_as_na(self):
        rows = [MockRow("Gymnastics", None)]
        result = _count_medals(rows)
        assert result["Gymnastics"]["na"] == 1

    def test_total_correct(self):
        rows = [MockRow("Rowing", "Gold"), MockRow("Rowing", None)]
        result = _count_medals(rows)
        assert result["Rowing"]["total"] == 2

    def test_multiple_sports_separated(self):
        rows = [MockRow("Swimming", "Gold"), MockRow("Athletics", "Silver")]
        result = _count_medals(rows)
        assert "Swimming" in result
        assert "Athletics" in result

    def test_empty_rows(self):
        assert _count_medals([]) == {}


# ---------------------------------------------------------------------------
# _aggregate_medals
# ---------------------------------------------------------------------------

class TestAggregateMedals:

    def test_total_equals_row_count(self):
        rows = [MockRow("Ski", "Gold"), MockRow("Ski", "Silver")]
        assert _aggregate_medals(rows)["total"] == 2

    def test_all_types_counted(self):
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

    def test_empty(self):
        result = _aggregate_medals([])
        assert result["total"] == 0
        assert result["gold"] == 0

    def test_all_na(self):
        rows = [MockRow("Archery", None) for _ in range(5)]
        result = _aggregate_medals(rows)
        assert result["na"] == 5
        assert result["gold"] == 0
