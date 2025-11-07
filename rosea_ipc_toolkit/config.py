"""Shared configuration constants for IPC area utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
COUNTRIES_CSV = REPO_ROOT / "countries.csv"
COUNTRY_FILENAME_SUFFIX = "_areas.topojson"
COUNTRY_COMBINED_SUFFIX = "_combined_areas.topojson"
GLOBAL_FILENAME = "global_areas.topojson"
GLOBAL_OUTPUT_PATH = DATA_DIR / GLOBAL_FILENAME
GLOBAL_INFO = {"name": "Global", "iso2": "GL", "iso3": "GLB"}

API_BASE_URL = "https://api.ipcinfo.org/areas"
CURRENT_YEAR = datetime.utcnow().year
AVAILABLE_YEARS = list(range(CURRENT_YEAR, CURRENT_YEAR - 6, -1))
DEFAULT_YEARS = [CURRENT_YEAR]
