"""Helpers for deriving repository state for CDN tagging."""

from __future__ import annotations

import os
import re
import subprocess
from typing import List, Optional, Tuple

from .config import REPO_ROOT


SEMVER_PATTERN = re.compile(r"^v(\d+)(?:\.(\d+))?(?:\.(\d+))?$")


def resolve_release_tag() -> str:
    env_tag = os.getenv("CDN_RELEASE_TAG")
    if env_tag:
        return env_tag

    next_semver = _determine_next_semver_tag()
    if next_semver:
        return next_semver

    git_commands = [
        ["git", "describe", "--tags", "--abbrev=0"],
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        ["git", "rev-parse", "--short", "HEAD"],
    ]

    for cmd in git_commands:
        try:
            result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, cwd=REPO_ROOT)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

        tag = result.decode().strip()
        if tag and tag != "HEAD":
            return tag

    return "main"


def _determine_next_semver_tag() -> Optional[str]:
    try:
        tag_output = subprocess.check_output(
            ["git", "tag", "--list"], stderr=subprocess.DEVNULL, cwd=REPO_ROOT
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    tags = [line.strip() for line in tag_output.decode().splitlines() if line.strip()]
    parsed_tags: List[Tuple[Tuple[int, int, int], Tuple[int, ...]]] = []

    for tag in tags:
        match = SEMVER_PATTERN.match(tag)
        if not match:
            continue

        groups = match.groups()
        normalized = (
            int(groups[0]),
            int(groups[1]) if groups[1] is not None else 0,
            int(groups[2]) if groups[2] is not None else 0,
        )
        length = 1 + sum(1 for group in groups[1:] if group is not None)
        parsed_tags.append((normalized, normalized[:length]))

    if not parsed_tags:
        return None

    _, original = max(parsed_tags, key=lambda item: item[0])

    parts_list = list(original)
    if not parts_list:
        parts_list = [0]
    parts_list[-1] += 1

    return "v" + ".".join(str(part) for part in parts_list)
