"""Guard against Streamlit duplicate-element-key crashes.

Every `key="..."` in app.py and pages/ must be globally unique, because app.py's
sidebar renders on the same script run as whichever page is active. Run this
after any edit:  python check_keys.py
"""

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
FILES = [ROOT / "app.py"] + sorted((ROOT / "pages").glob("*.py"))

# f-string keys are templated per item; compare their literal prefix instead.
KEY_RE = re.compile(r'key\s*=\s*(f?)"([^"]*)"')
PREFIX = {"app.py": "nav_", "login.py": "lg_", "onboarding.py": "ob_",
          "dashboard.py": "db_", "timetable.py": "tt_", "settings.py": "sg_",
          "_ui.py": "ui_", "_tasks.py": "tk_"}


def literal_prefix(name):
    """Text before the first f-string placeholder."""
    return name.split("{", 1)[0]


def main():
    seen = {}
    problems = []

    for path in FILES:
        if not path.exists():
            continue
        src = path.read_text(encoding="utf-8")
        try:
            ast.parse(src)
        except SyntaxError as exc:
            problems.append(f"{path.name}: syntax error — {exc}")
            continue

        for is_f, name in KEY_RE.findall(src):
            stem = literal_prefix(name)
            # container keys (layout only) live in their own `cad*` namespace
            if stem.startswith("cad"):
                continue
            want = PREFIX.get(path.name)
            if want and not stem.startswith(want):
                problems.append(
                    f"{path.name}: key {name!r} should start with {want!r}")
            if not is_f and name in seen and seen[name] != path.name:
                problems.append(
                    f"duplicate key {name!r} in {seen[name]} and {path.name}")
            if not is_f:
                seen[name] = path.name

    # container keys must also not collide across files
    containers = {}
    for path in FILES:
        if not path.exists():
            continue
        for is_f, name in KEY_RE.findall(path.read_text(encoding="utf-8")):
            if not literal_prefix(name).startswith("cad") or is_f:
                continue
            if name in containers and containers[name] != path.name:
                problems.append(
                    f"duplicate container key {name!r} in "
                    f"{containers[name]} and {path.name}")
            containers[name] = path.name

    if problems:
        print("FAIL")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK — {len(seen)} widget keys and {len(containers)} container keys, "
          f"all unique and namespaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
