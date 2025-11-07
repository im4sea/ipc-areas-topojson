# ROSEA IPC Areas Toolkit

Automation for downloading and harmonising IPC (Integrated Food Security Phase Classification) boundary data. The toolkit keeps the latest analysis per year, merges country datasets, and publishes global artefacts ready for maps or dashboards.

## Outputs

- `data/{ISO3}/{ISO3}_combined_areas.topojson` – all assessments for a country, deduplicated by IPC ID with rounded coordinates.
- `data/global_areas.topojson` – aggregation of every combined country file with configurable rounding and simplification (defaults to conservative values).
- `data/index.json` – catalogue of exported datasets, feature counts, timestamps, and optional CDN URLs.
- `data/**/*_unsimplified.json` – optional reports listing features kept at full detail when simplification fails or has no effect.

## Quick Start

1. Install Python 3.11.
2. `pip install -r requirements.txt`
3. Set your IPC API token: PowerShell → `$env:IPC_KEY = 'your_api_key'`.
4. Run `python -m cli.download_ipc_areas`.

## Common Commands

- Limit scope: `python -m cli.download_ipc_areas --countries SD --years 2025 2024`
- Custom precision: `python -m cli.download_ipc_areas --precision 4 --simplify-tolerance 0.001`
- Rebuild global only: `python -m cli.combine_ipc_areas`
- Simplify an existing file: `python -m cli.simplify_ipc_global_areas --help`
- Programmatic use: `from rosea_ipc_toolkit import DownloadConfig, IPCAreaDownloader`
- Skip index generation: `python -m cli.download_ipc_areas --skip-index`

## GitHub Workflow

- `.github/workflows/refresh-ipc-areas.yml` runs every Monday at 06:00 UTC and supports manual dispatch.
- Inputs:
  - `full_refresh` – include all historical years.
  - `specific_years` – comma-separated override for exact years.
  - `country_codes` – comma-separated ISO2/ISO3 filter.
  - `skip_index` – omit index generation, useful for exploratory runs.
- Workflow regenerates combined/global files, refreshes `data/index.json` (unless skipped), and opens a pull request.

## Development Notes

- Core logic lives under `rosea_ipc_toolkit/`; CLI wrappers sit in `cli/`.
- `DownloadConfig` controls years, precision, simplification, rate limiting, and country filters.
- Geometry content now mirrors the source analysis: every geometry type (points, lines, polygons, collections) is retained after sanitisation.
- Update `DEFAULT_YEARS` in `rosea_ipc_toolkit.config` when IPC adds assessments.
- CDN URLs default to the next semantic git tag; set `CDN_RELEASE_TAG` to override.

For IPC API issues contact the IPC Info team; for toolkit questions open a GitHub issue or review CLI logs.