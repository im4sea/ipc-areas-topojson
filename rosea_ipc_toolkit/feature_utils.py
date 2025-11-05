"""Feature-level helpers shared across the IPC toolkit and CLI."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, List, Optional

Feature = Dict[str, Any]


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


def normalise_polygon_geometry(geometry: Any) -> Optional[Dict[str, Any]]:
    """Return a polygonal geometry (Polygon/MultiPolygon) or ``None``.

    Geometry collections are flattened so that any polygonal members are
    retained, while non-polygonal members (e.g. points, lines) are ignored.
    """

    if not isinstance(geometry, dict):
        return None

    geom_type = geometry.get("type")

    if geom_type == "Polygon":
        coordinates = geometry.get("coordinates")
        if not coordinates:
            return None
        return {"type": "Polygon", "coordinates": copy.deepcopy(coordinates)}

    if geom_type == "MultiPolygon":
        coordinates = geometry.get("coordinates")
        if not coordinates:
            return None
        return {"type": "MultiPolygon", "coordinates": copy.deepcopy(coordinates)}

    if geom_type == "GeometryCollection":
        polygons: List[Any] = []
        multi_detected = False

        for child in geometry.get("geometries") or []:
            normalised = normalise_polygon_geometry(child)
            if not normalised:
                continue

            if normalised["type"] == "Polygon":
                polygons.append(copy.deepcopy(normalised["coordinates"]))
            elif normalised["type"] == "MultiPolygon":
                multi_detected = True
                polygons.extend(copy.deepcopy(normalised["coordinates"]))

        if not polygons:
            return None

        if multi_detected or len(polygons) > 1:
            return {"type": "MultiPolygon", "coordinates": polygons}

        return {"type": "Polygon", "coordinates": polygons[0]}

    return None


def is_supported_geometry(geometry: Any) -> bool:
    return normalise_polygon_geometry(geometry) is not None
