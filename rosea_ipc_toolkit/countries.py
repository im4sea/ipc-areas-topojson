"""Country metadata loading from the project's CSV source."""

from __future__ import annotations

import csv
import sys
from typing import Dict, Optional

from .config import COUNTRIES_CSV

CountryRow = Dict[str, str]


def _normalise_fieldnames(reader: csv.DictReader) -> None:
    if reader.fieldnames:
        reader.fieldnames = [field.strip() for field in reader.fieldnames]


def load_countries(*, ocha_region: Optional[str]) -> Dict[str, CountryRow]:
    region_filter = (ocha_region or "").strip().lower()
    if region_filter in {"*", "all"}:
        region_filter = ""

    countries: Dict[str, CountryRow] = {}

    try:
        with COUNTRIES_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            _normalise_fieldnames(reader)

            for row in reader:
                if not row:
                    continue

                alpha_2 = (row.get("Alpha_2_Code") or "").strip()
                alpha_3 = (row.get("Alpha_3_Code") or "").strip()
                name = (row.get("English_Short_Name") or "").strip()
                ocha = (row.get("OCHA_Region") or "").strip()

                if region_filter and ocha.lower() != region_filter:
                    continue

                if not alpha_2 or not alpha_3:
                    print("    Skipping row with missing ISO codes")
                    continue

                countries[alpha_2] = {
                    "name": name or alpha_2,
                    "iso2": alpha_2,
                    "iso3": alpha_3,
                    "ocha_region": ocha or None,
                }
    except FileNotFoundError:
        print("Error: countries.csv file not found")
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 - escalate & exit
        print(f"Error reading countries.csv: {exc}")
        sys.exit(1)

    return countries
