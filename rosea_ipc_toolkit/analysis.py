"""Utilities for grouping IPC features by analysis releases."""

from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .dates import (
    ANALYSIS_ID_KEYS,
    ANALYSIS_LABEL_KEYS,
    DATE_FROM_KEYS,
    DATE_PUBLISHED_KEYS,
    DATE_TO_KEYS,
    DATE_UPDATED_KEYS,
    first_present,
    parse_iso_datetime,
)

Feature = Dict[str, Any]
AnalysisBucket = Dict[str, Any]


def _initial_bucket(props: Dict[str, Any]) -> AnalysisBucket:
    return {
        "features": [],
        "analysis_id": first_present(props, ANALYSIS_ID_KEYS),
        "analysis_label": first_present(props, ANALYSIS_LABEL_KEYS),
        "from_raw": first_present(props, DATE_FROM_KEYS),
        "to_raw": first_present(props, DATE_TO_KEYS),
        "updated_raw": first_present(props, DATE_UPDATED_KEYS),
        "published_raw": first_present(props, DATE_PUBLISHED_KEYS),
        "from_dt": None,
        "to_dt": None,
        "updated_dt": None,
        "published_dt": None,
    }


def _bucket_key(props: Dict[str, Any]) -> str:
    parts = [
        first_present(props, ANALYSIS_ID_KEYS),
        first_present(props, DATE_FROM_KEYS),
        first_present(props, DATE_TO_KEYS),
    ]
    filtered = [str(part) for part in parts if part not in (None, "")]
    return "|".join(filtered) if filtered else "default"


def _hydrate_dates(bucket: AnalysisBucket) -> None:
    bucket["from_dt"] = parse_iso_datetime(bucket.get("from_raw"))
    bucket["to_dt"] = parse_iso_datetime(bucket.get("to_raw"))
    bucket["updated_dt"] = parse_iso_datetime(bucket.get("updated_raw"))
    bucket["published_dt"] = parse_iso_datetime(bucket.get("published_raw"))


def _covers_current_period(bucket: AnalysisBucket, current_day: Optional[date]) -> bool:
    """Determine whether the analysis period covers the provided day."""

    if current_day is None:
        return False

    from_dt = bucket.get("from_dt")
    to_dt = bucket.get("to_dt")

    from_day = from_dt.date() if isinstance(from_dt, datetime) else None
    to_day = to_dt.date() if isinstance(to_dt, datetime) else None

    if from_day and to_day:
        return from_day <= current_day <= to_day
    if from_day and not to_day:
        return from_day <= current_day
    if to_day and not from_day:
        return current_day <= to_day
    return False


def select_latest_analysis(
    raw_features: Iterable[Feature],
    *,
    target_year: Optional[int] = None,
    current_date: Optional[date] = None,
) -> Tuple[List[Feature], Dict[str, Any]]:
    """Pick the most relevant analysis from a pool of IPC features.

    Historical years favour the latest validity window. For the current year,
    prefer analyses whose validity period includes the current date.
    """

    analyses: Dict[str, AnalysisBucket] = {}

    for feature in raw_features:
        if not isinstance(feature, dict):
            continue
        props = feature.get("properties") or {}
        key = _bucket_key(props)
        bucket = analyses.setdefault(key, _initial_bucket(props))
        bucket["features"].append(feature)

        # Backfill missing metadata when later features include richer fields.
        for field, keys in (
            ("analysis_id", ANALYSIS_ID_KEYS),
            ("analysis_label", ANALYSIS_LABEL_KEYS),
            ("from_raw", DATE_FROM_KEYS),
            ("to_raw", DATE_TO_KEYS),
            ("updated_raw", DATE_UPDATED_KEYS),
            ("published_raw", DATE_PUBLISHED_KEYS),
        ):
            if bucket.get(field) in (None, ""):
                candidate = first_present(props, keys)
                if candidate not in (None, ""):
                    bucket[field] = candidate

    if not analyses:
        return [], {}

    today: Optional[date] = current_date or datetime.utcnow().date()
    is_current_year = bool(target_year is not None and today and target_year == today.year)

    for bucket in analyses.values():
        _hydrate_dates(bucket)
        bucket["covers_current_period"] = _covers_current_period(bucket, today)

    def coverage_score(meta: AnalysisBucket) -> int:
        return 1 if meta.get("covers_current_period") else 0

    def sort_key(item: Tuple[str, AnalysisBucket]) -> Tuple:
        _, meta = item
        return (
            coverage_score(meta),
            meta.get("to_dt") or datetime.min,
            meta.get("from_dt") or datetime.min,
            meta.get("updated_dt") or datetime.min,
            meta.get("published_dt") or datetime.min,
            len(meta.get("features") or []),
        )

    items = list(analyses.items())

    if is_current_year:
        covering = [item for item in items if item[1].get("covers_current_period")]
        if covering:
            items = covering

    selected_key, selected_meta = max(items, key=sort_key)

    return selected_meta.get("features", []), {
        "analysis_id": selected_meta.get("analysis_id"),
        "analysis_label": selected_meta.get("analysis_label"),
        "from_date": selected_meta.get("from_raw"),
        "to_date": selected_meta.get("to_raw"),
        "updated_at": selected_meta.get("updated_raw"),
        "published_at": selected_meta.get("published_raw"),
        "bucket_key": selected_key,
        "covers_current_period": bool(selected_meta.get("covers_current_period")),
    }
