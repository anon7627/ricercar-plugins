#!/usr/bin/env python3
"""Validate plugins/*.toml, then write index.json and the README table.

    python3 scripts/build.py           # rewrite index.json and README.md
    python3 scripts/build.py --check   # fail if an entry is invalid or the
                                       # generated files are out of date (CI)

The rules match what ricercar accepts (crates/ricercar-core/src/plugin/
catalog.rs in the ricercar repository): an entry the app would ignore is
refused here.
"""

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID = re.compile(r"^[a-z0-9-]{1,64}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
ARCHES = {"x86_64", "aarch64"}
CAPS = {
    "auth", "browse", "search", "resolve", "favorites", "reporting", "remote_control", "library",
    "lyrics", "details", "radio", "playlist_edit",
}
REQUIRED = ("id", "name", "description", "author", "license", "repository", "version", "protocol")
KNOWN = set(REQUIRED) | {"homepage", "capabilities", "args", "assets"}
BEGIN, END = "<!-- catalogue:begin -->", "<!-- catalogue:end -->"


def https(url):
    return isinstance(url, str) and url.startswith("https://") and len(url) > len("https://")


def check(path, e):
    errs = []
    for k in REQUIRED:
        if k not in e or e[k] in ("", None):
            errs.append(f"missing `{k}`")
    for k in e:
        if k not in KNOWN:
            errs.append(f"unknown field `{k}`")
    if not ID.match(str(e.get("id", ""))):
        errs.append("`id` must be [a-z0-9-], at most 64 characters")
    if path.stem != e.get("id"):
        errs.append(f"file name must be `{e.get('id')}.toml`")
    if not https(e.get("repository")):
        errs.append("`repository` must be an https URL")
    if "homepage" in e and not https(e["homepage"]):
        errs.append("`homepage` must be an https URL")
    if not isinstance(e.get("protocol"), int) or e.get("protocol", 0) < 1:
        errs.append("`protocol` must be a positive integer")
    for c in e.get("capabilities", []):
        if c not in CAPS:
            errs.append(f"unknown capability `{c}`")
    if not all(isinstance(a, str) for a in e.get("args", [])):
        errs.append("`args` must be a list of strings")
    seen = set()
    for a in e.get("assets", []):
        if a.get("arch") not in ARCHES:
            errs.append(f"asset arch must be one of {sorted(ARCHES)}")
        elif a["arch"] in seen:
            errs.append(f"two assets for {a['arch']}")
        seen.add(a.get("arch"))
        if not https(a.get("url")):
            errs.append("asset `url` must be an https URL")
        if not SHA.match(str(a.get("sha256", ""))):
            errs.append("asset `sha256` must be 64 lowercase hex digits")
        extra = set(a) - {"arch", "url", "sha256"}
        if extra:
            errs.append(f"unknown asset field(s) {sorted(extra)}")
    for k in ("name", "description", "author", "license", "version"):
        if k in e and not isinstance(e[k], str):
            errs.append(f"`{k}` must be a string")
    if len(str(e.get("description", ""))) > 400:
        errs.append("`description` is longer than 400 characters")
    return errs


def cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def table(entries):
    rows = [
        "| Plugin | Description | Author | Licence | Version | Builds |",
        "|---|---|---|---|---|---|",
    ]
    for e in entries:
        builds = ", ".join(a["arch"] for a in e.get("assets", [])) or "from source"
        rows.append(
            f"| [{cell(e['name'])}]({e['repository']}) | {cell(e['description'])} "
            f"| {cell(e['author'])} | {cell(e['license'])} | {cell(e['version'])} | {builds} |"
        )
    return "\n".join(rows)


def main():
    check_only = "--check" in sys.argv[1:]
    entries, failed = [], False
    for path in sorted((ROOT / "plugins").glob("*.toml")):
        try:
            e = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as err:
            print(f"{path.name}: {err}")
            failed = True
            continue
        errs = check(path, e)
        for m in errs:
            print(f"{path.name}: {m}")
        failed |= bool(errs)
        entries.append(e)
    ids = [e.get("id") for e in entries]
    for dup in {i for i in ids if ids.count(i) > 1}:
        print(f"duplicate id `{dup}`")
        failed = True
    if failed:
        sys.exit(1)

    entries.sort(key=lambda e: e["name"].lower())
    index = json.dumps({"version": 1, "plugins": entries}, indent=2, ensure_ascii=False) + "\n"
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    start, end = readme.index(BEGIN) + len(BEGIN), readme.index(END)
    new_readme = readme[:start] + "\n" + table(entries) + "\n" + readme[end:]

    index_path = ROOT / "index.json"
    if check_only:
        stale = []
        if not index_path.exists() or index_path.read_text(encoding="utf-8") != index:
            stale.append("index.json")
        if readme != new_readme:
            stale.append("README.md")
        if stale:
            print(f"out of date: {', '.join(stale)}; run python3 scripts/build.py")
            sys.exit(1)
        print(f"{len(entries)} plugin(s), all valid")
        return
    index_path.write_text(index, encoding="utf-8")
    readme_path.write_text(new_readme, encoding="utf-8")
    print(f"{len(entries)} plugin(s) written")


if __name__ == "__main__":
    main()
