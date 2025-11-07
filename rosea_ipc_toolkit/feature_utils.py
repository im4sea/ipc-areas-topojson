"""Feature-level helpers shared across the IPC toolkit and CLI."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, List, Optional

Feature = Dict[str, Any]

Geometry = Dict[str, Any]


def normalize_title(title: str | None) -> str:
    if not title:
        return ""
    return " ".join(title.split()).strip().lower()


def feature_key(feature: Feature) -> str:
    props = feature.get("properties") or {}
    area_id = props.get("id")
    iso_value = (props.get("iso3") or props.get("country") or "").strip().lower()

    if area_id is not None:
        return f"id::{iso_value}::{str(area_id).strip()}"

    title_key = normalize_title(props.get("title"))
    if title_key:
        return f"title::{iso_value}::{title_key}" if iso_value else f"title::{title_key}"

    geometry = feature.get("geometry")
    if geometry:
        geometry_str = json.dumps(geometry, sort_keys=True)
        digest = hashlib.sha1(geometry_str.encode("utf-8")).hexdigest()
        return f"geometry::{digest}"

    fallback_str = json.dumps(feature, sort_keys=True)
    digest = hashlib.sha1(fallback_str.encode("utf-8")).hexdigest()
    return f"feature::{digest}"


def sanitise_geometry(geometry: Any) -> Optional[Geometry]:
    """Return a deep-copied GeoJSON geometry or ``None`` if invalid."""

    if not isinstance(geometry, dict):
        return None

    geom_type = geometry.get("type")

    if geom_type == "GeometryCollection":
        geometries_field = geometry.get("geometries")
        if not isinstance(geometries_field, list):
            return None
        members: List[Geometry] = []
        for child in geometries_field:
            cleaned = sanitise_geometry(child)
            if cleaned is not None:
                members.append(cleaned)

        if not members:
            return None

        result: Geometry = {"type": "GeometryCollection", "geometries": members}
        if "bbox" in geometry and isinstance(geometry["bbox"], list):
            result["bbox"] = copy.deepcopy(geometry["bbox"])
        return result

    if geom_type in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}:
        coordinates = geometry.get("coordinates")
        if coordinates is None:
            return None
        result = {"type": geom_type, "coordinates": copy.deepcopy(coordinates)}
        if "bbox" in geometry and isinstance(geometry["bbox"], list):
            result["bbox"] = copy.deepcopy(geometry["bbox"])
        return result

    if geom_type in {"CircularString", "CompoundCurve", "CurvePolygon"}:
        # Non-standard GeoJSON types sometimes returned by upstream sources.
        coordinates = geometry.get("coordinates")
        if coordinates is None:
            return None
        result = {"type": geom_type, "coordinates": copy.deepcopy(coordinates)}
        if "bbox" in geometry and isinstance(geometry["bbox"], list):
            result["bbox"] = copy.deepcopy(geometry["bbox"])
        return result

    try:
        return json.loads(json.dumps(geometry))
    except (TypeError, ValueError):
        return None
