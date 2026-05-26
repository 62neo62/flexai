from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any


def _load_pose_engine_module() -> ModuleType:
    """
    flexbot expects the Coral PoseNet `pose_engine.py` implementation.

    This project currently vendors it in:
      /home/sebastian/projects/cnnproj/project-posenet/pose_engine.py
    (directory name contains a hyphen, so it can't be imported normally).
    """

    candidate = (
        Path(__file__).resolve().parents[1]
        / "cnnproj"
        / "project-posenet"
        / "pose_engine.py"
    )
    if not candidate.exists():
        raise ModuleNotFoundError(
            "Could not locate pose_engine.py. Expected at "
            f"{candidate}. Either vendor it there or update flexbot/pose_engine.py."
        )

    spec = importlib.util.spec_from_file_location("_flexbot_pose_engine", str(candidate))
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(f"Could not load pose_engine module from {candidate}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # The upstream module sets POSENET_SHARED_LIB to a relative path like:
    #   posenet_lib/<arch>/posenet_decoder.so
    # which breaks when flexbot is run from a different cwd.
    try:
        base_dir = candidate.parent
        rel = getattr(mod, "POSENET_SHARED_LIB", None)
        if isinstance(rel, str):
            abs_path = (base_dir / rel).resolve()
            mod.POSENET_SHARED_LIB = str(abs_path)
    except Exception:
        # If anything changes upstream, fail later with a clearer error.
        pass
    return mod


_CACHED: ModuleType | None = None


def __getattr__(name: str) -> Any:  # pragma: no cover
    global _CACHED
    if name not in {"PoseEngine", "Point", "Keypoint"}:
        raise AttributeError(name)
    if _CACHED is None:
        _CACHED = _load_pose_engine_module()
    return getattr(_CACHED, name)


