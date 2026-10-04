"""Path bootstrap — ``import _path_setup`` at the top of any script in this
folder. Walks upward to the repository root (the directory containing ``.git``)
and adds ``<repo>/code`` and ``<repo>/code/src`` to ``sys.path`` so project
packages are importable.
"""

import sys as _sys
from pathlib import Path as _Path


def _bootstrap() -> None:
    d = _Path(__file__).resolve().parent
    while d != d.parent:
        if (d / ".git").is_dir():
            _code_root = d / "code"
            _code_src = _code_root / "src"
            if _code_root.is_dir() and str(_code_root) not in _sys.path:
                _sys.path.insert(0, str(_code_root))
            if _code_src.is_dir() and str(_code_src) not in _sys.path:
                _sys.path.insert(0, str(_code_src))
            return
        d = d.parent


_bootstrap()
