"""TopoJSON IO helpers shared across the IPC toolkit and CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import topojson as tp

from .config import REPO_ROOT

Feature = Dict[str, Any]


def convert_geojson_to_topology(geojson: Dict[str, Any]) -> Dict[str, Any]:
    topology = tp.Topology(geojson, prequantize=False)
    return topology.to_dict()


def load_topojson_features(path: Path) -> List[Feature]:
    with path.open("r", encoding="utf-8") as handle:
        topo_payload = json.load(handle)

    topology = tp.Topology(topo_payload, topology=True, prequantize=False)
    geojson_payload = json.loads(topology.to_geojson())

    features = geojson_payload.get("features") if isinstance(geojson_payload, dict) else None
    if not isinstance(features, list):
        return []

    return [feature for feature in features if isinstance(feature, dict)]


def save_topology(topojson_data: Dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(topojson_data, handle, separators=(",", ":"))

    return path


def display_relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def infer_feature_count(path: Path) -> Optional[int]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None

    objects = payload.get("objects") if isinstance(payload, dict) else None
    if not isinstance(objects, dict) or not objects:
        return None

    first_object = next(iter(objects.values()), None)
    geometries = first_object.get("geometries") if isinstance(first_object, dict) else None
    if isinstance(geometries, list):
        return len(geometries)

    return None
