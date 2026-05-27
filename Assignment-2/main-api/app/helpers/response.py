"""Format API responses as JSON, XML, or CSV based on the Accept header."""

import csv
import io
import xml.etree.ElementTree as ET
from typing import Any, Union
from fastapi import Request
from fastapi.responses import JSONResponse, Response


def _to_xml_element(data: Any, tag: str) -> ET.Element:
    safe_tag = str(tag).replace(" ", "_")
    elem = ET.Element(safe_tag)
    if isinstance(data, dict):
        for key, value in data.items():
            elem.append(_to_xml_element(value, str(key)))
    elif isinstance(data, list):
        for item in data:
            elem.append(_to_xml_element(item, "item"))
    else:
        elem.text = str(data) if data is not None else ""
    return elem


def to_xml_string(data: Any, root_tag: str = "response") -> str:
    root = _to_xml_element(data, root_tag)
    return ET.tostring(root, encoding="unicode")


def _flatten(data: Any, prefix: str = "") -> dict:
    items: dict = {}
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else str(key)
            items.update(_flatten(value, full_key))
    elif isinstance(data, list):
        for i, value in enumerate(data):
            full_key = f"{prefix}.{i}" if prefix else str(i)
            items.update(_flatten(value, full_key))
    else:
        items[prefix] = str(data) if data is not None else ""
    return items


def to_csv_string(data: Any) -> str:
    output = io.StringIO()
    rows = [_flatten(item) for item in data] if isinstance(data, list) else [_flatten(data)]
    if not rows:
        return ""
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def format_response(data: Any, request: Request) -> Union[JSONResponse, Response]:
    """Return JSON, XML, or CSV depending on the Accept header."""
    accept = request.headers.get("Accept", "application/json")
    if "application/xml" in accept:
        return Response(content=to_xml_string(data), media_type="application/xml")
    if "text/csv" in accept:
        return Response(content=to_csv_string(data), media_type="text/csv")
    return JSONResponse(content=data)
