"""API authentication helpers for IPC services."""

from __future__ import annotations

import os
from typing import Optional


def resolve_ipc_key() -> Optional[str]:
    """Resolve IPC API key from environment or Windows user variables."""

    key = os.getenv("IPC_KEY")
    if key:
        return key

    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as reg_key:
                value, _ = winreg.QueryValueEx(reg_key, "IPC_KEY")
                if value:
                    return value
        except FileNotFoundError:
            pass
        except OSError as exc:
            print(f"Warning: unable to read user environment variables: {exc}")

    return None
