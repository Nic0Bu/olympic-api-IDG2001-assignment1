"""Helpers for formatting API responses as JSON or XML."""

import xml.etree.ElementTree as ET
from typing import Any, Union
from fastapi import Request
from fastapi.responses import JSONResponse, Response


def _to_xml_element(data: Any, tag: str) -> ET.Element:
    """Recursively build an XML element tree from a dict, list, or scalar."""
    safe_tag = str(tag).replace(" ", "_")
    elem = ET.Element(safe_tag)
    if isinstance(data, dict):
        for key, value in data.items():
            child = _to_xml_element(value, str(key))
            elem.append(child)
    elif isinstance(data, list):
        for item in data:
            child = _to_xml_element(item, "item")
            elem.append(child)
    else:
        elem.text = str(data) if data is not None else ""
    return elem


def to_xml_string(data: Any, root_tag: str = "response") -> str:
    """Convert a Python dict or list to an XML string."""
    root = _to_xml_element(data, root_tag)
    return ET.tostring(root, encoding="unicode")


def format_response(
    data: Any, request: Request
) -> Union[JSONResponse, Response]:
    """Return a JSON or XML response based on the request Accept header."""
    accept = request.headers.get("Accept", "application/json")
    if "application/xml" in accept:
        xml_str = to_xml_string(data)
        return Response(content=xml_str, media_type="application/xml")
    return JSONResponse(content=data)
