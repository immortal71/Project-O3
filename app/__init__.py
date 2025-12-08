
This module registers a meta-path finder that maps imports starting with
`app.` to modules under the existing `backend` package. It avoids moving
or duplicating source files and makes the code runnable as-is.

Behavior:
- When `import app.foo.bar` is requested, the finder will attempt to import
  `backend.foo.bar`, `backend.foo`, or `backend.foo.bar.baz` (decreasing
  suffix) and then expose the imported module's attributes under the
  requested `app.*` module name.

"""
App import shim
This is a non-invasive shim for local development only.
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com
import importlib
import importlib.util
import importlib.abc
import sys
from types import ModuleType


class _AppShimFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path, target=None):
        # Only handle modules that start with 'app.' (not the root 'app')
        if not fullname.startswith("app."):
            return None

        target_mod = fullname[4:]
        parts = target_mod.split('.') if target_mod else []

        # Try decreasing-length candidates under the 'backend' package
        for i in range(len(parts), 0, -1):
            candidate = 'backend.' + '.'.join(parts[:i])
            if importlib.util.find_spec(candidate):
                return importlib.util.spec_from_loader(fullname, self)

        # As a last resort, try mapping directly to top-level backend module
        candidate = 'backend.' + target_mod
        if importlib.util.find_spec(candidate):
            return importlib.util.spec_from_loader(fullname, self)

        return None

    def create_module(self, spec):
        return None  # use default module creation

    def exec_module(self, module: ModuleType):
        fullname = module.__name__
        target_mod = fullname[4:]
        parts = target_mod.split('.') if target_mod else []

        # Try decreasing-length candidates under backend
        for i in range(len(parts), 0, -1):
            candidate = 'backend.' + '.'.join(parts[:i])
            spec = importlib.util.find_spec(candidate)
            if spec:
                target = importlib.import_module(candidate)
                # Copy attributes from target into the shim module
                for k, v in target.__dict__.items():
                    if k.startswith('__') and k.endswith('__'):
                        continue
                    module.__dict__[k] = v
                # Keep module metadata
                module.__dict__['__loader__'] = self
                module.__dict__['__package__'] = fullname.rpartition('.')[0]
                return

        # Fallback: try backend.<target_mod>
        candidate = 'backend.' + target_mod
        spec = importlib.util.find_spec(candidate)
        if spec:
            target = importlib.import_module(candidate)
            for k, v in target.__dict__.items():
                if k.startswith('__') and k.endswith('__'):
                    continue
                module.__dict__[k] = v
            module.__dict__['__loader__'] = self
            module.__dict__['__package__'] = fullname.rpartition('.')[0]
            return


# Register the finder at the front of meta_path so it runs early
sys.meta_path.insert(0, _AppShimFinder())

# Also expose a small helper to check mapping
def _mapped_target(import_name: str) -> str | None:
    """Return the first backend candidate that exists for a given app import."""
    if not import_name.startswith('app.'):
        return None
    target_mod = import_name[4:]
    parts = target_mod.split('.') if target_mod else []
    for i in range(len(parts), 0, -1):
        candidate = 'backend.' + '.'.join(parts[:i])
        if importlib.util.find_spec(candidate):
            return candidate
    candidate = 'backend.' + target_mod
    return candidate if importlib.util.find_spec(candidate) else None


__all__ = ['_mapped_target']
