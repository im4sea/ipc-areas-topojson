"""Helpers for normalising IPC metadata timestamps."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Optional

DATE_FROM_KEYS = (
    "from_date",
    "fromDate",
    "analysis_from",
    "period_from",
    "start_date",
    "from",
)
DATE_TO_KEYS = (
    "to_date",
    "toDate",
    "analysis_to",
    "period_to",
    "end_date",
    "to",
)
DATE_UPDATED_KEYS = (
    "updated_at",
    "updatedAt",
    "last_updated",
    "modified_at",
)
DATE_PUBLISHED_KEYS = (
    "published_at",
    "publishedAt",
)
ANALYSIS_ID_KEYS = (
    "analysis_id",
    "analysisId",
    "analysisID",
    "analysisid",
    "anl_id",
)
ANALYSIS_LABEL_KEYS = (
    "analysis_label",
    "analysisLabel",
    "analysis_name",
    "analysisName",
    "analysis",
)


def first_present(props: dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
    """Return the first non-empty value for the given keys."""

    for key in keys:
        value = props.get(key)
        if value not in (None, ""):
            return value
    return None


def parse_iso_datetime(value: Any) -> Optional[datetime]:
    """Parse mixed IPC timestamps into naive UTC datetimes when possible."""

    if value in (None, ""):
        return None

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)
        except (OSError, OverflowError, ValueError):
            return None

    text = str(value).strip()
    if not text:
        return None

    normalised = text[:-1] + "+00:00" if text.endswith("Z") else text

    try:
        parsed = datetime.fromisoformat(normalised)
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    for fmt in ("%b %Y", "%B %Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None
