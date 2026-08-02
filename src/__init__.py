"""
Multi-Agent Appointment Booking System.

This package init applies a compatibility shim before any submodules are
imported (see below). Keep it first in the module so the patch is active
before `src.agents`, `src.main`, etc. pull in `langchain`/`langsmith`.
"""

import sys
import typing

# --- Python 3.12.13 `typing.ForwardRef._evaluate` compatibility shim ---
#
# A recent Python 3.12 patch release (present in this project's pinned
# 3.12.13 runtime, see CI: .github/workflows/ci.yml) made the
# `recursive_guard` parameter of `typing.ForwardRef._evaluate` keyword-only
# with NO default value. Older code (notably pydantic's bundled
# `pydantic.v1` compatibility shim, still used internally by `langsmith`
# even on the latest release as of this writing) calls `_evaluate()`
# positionally without `recursive_guard`, which now raises:
#
#   TypeError: ForwardRef._evaluate() missing 1 required keyword-only
#   argument: 'recursive_guard'
#
# This breaks the `langchain_openai -> langchain_core -> langsmith` import
# chain used by `NLPAgent` (src/agents/base.py). We intentionally stay on
# Python 3.12 (per project requirements) rather than downgrading, so we
# patch `ForwardRef._evaluate` here to fall back to an empty
# `recursive_guard` when the caller omits it. This is a narrow, backwards
# compatible shim: modern callers that already pass `recursive_guard`
# explicitly are unaffected.
if sys.version_info[:2] == (3, 12):
    _original_forwardref_evaluate = typing.ForwardRef._evaluate

    def _patched_forwardref_evaluate(self, globalns, localns, type_params=None, *, recursive_guard=None):
        if recursive_guard is None:
            recursive_guard = frozenset()
        return _original_forwardref_evaluate(
            self, globalns, localns, type_params, recursive_guard=recursive_guard
        )

    typing.ForwardRef._evaluate = _patched_forwardref_evaluate
