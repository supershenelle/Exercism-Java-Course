"""
update_readme.py
────────────────
Fetches your completed Exercism Java solutions, downloads each solution's
actual source code, scans it for Java concepts using keyword/pattern matching,
then rewrites the <!-- EXERCISM-START --> … <!-- EXERCISM-END --> block in README.md.

Requirements
  pip install requests

Environment variables (set as GitHub Actions secrets)
  EXERCISM_TOKEN – your Exercism API token (exercism.org/settings/api_cli)
"""

import os
import re
import sys
import json
import time
import requests

# ── Config ────────────────────────────────────────────────────────────────────

EXERCISM_API  = "https://exercism.org/api/v2"
TRACK         = "java"
README_PATH   = "README.md"
MARKER_START  = "<!-- EXERCISM-START -->"
MARKER_END    = "<!-- EXERCISM-END -->"
CACHE_PATH    = "scripts/.concepts_cache.json"

# ── Concept detection rules ───────────────────────────────────────────────────

CONCEPT_RULES = [
    ("Classes",             [r"\bclass\b"]),
    ("Inheritance",         [r"\bextends\b"]),
    ("Interfaces",          [r"\bimplements\b", r"\binterface\b"]),
    ("Constructors",        [r"public\s+[A-Z]\w+\s*\("]),
    ("Access modifiers",    [r"\b(private|protected)\b"]),
    ("Static members",      [r"\bstatic\b"]),
    ("Enums",               [r"\benum\b"]),
    ("Abstract classes",    [r"\babstract\b"]),
    ("Generics",            [r"<[A-Z]\w*>"]),
    ("If/else",             [r"\bif\s*\(", r"\belse\b"]),
    ("Switch statement",    [r"\bswitch\s*\("]),
    ("For loop",            [r"\bfor\s*\("]),
    ("While loop",          [r"\bwhile\s*\("]),
    ("Do-while loop",       [r"\bdo\s*\{"]),
    ("Ternary operator",    [r"\?[^:\n]+:"]),
    ("Break/continue",      [r"\b(break|continue)\b"]),
    ("Booleans",            [r"\bboolean\b"]),
    ("Integers",            [r"\b(int|long|short|byte)\b"]),
    ("Doubles/floats",      [r"\b(double|float)\b"]),
    ("Constants",           [r"\bfinal\b"]),
    ("Type casting",        [r"\([a-z]+\)\s*\w"]),
    ("Null checks",         [r"\bnull\b"]),
    ("String methods",      [r"\.(toUpperCase|toLowerCase|substring|indexOf|contains|replace|split|trim|startsWith|endsWith|charAt|length)\s*\("]),
    ("String concatenation",[r'"\s*\+']),
    ("String formatting",   [r"String\.format\s*\(", r"\.formatted\s*\("]),
    ("StringBuilder",       [r"\bStringBuilder\b"]),
    ("Char operations",     [r"\bchar\b"]),
    ("Math class",          [r"\bMath\."]),
    ("Arrays",              [r"\w+\s*\[\]", r"\bArrays\."]),
    ("ArrayList",           [r"\bArrayList\b"]),
    ("HashMap",             [r"\bHashMap\b"]),
    ("HashSet",             [r"\bHashSet\b"]),
    ("Collections API",     [r"\bCollections\."]),
    ("Lambda expressions",  [r"->"]),
    ("Streams API",         [r"\.stream\(\)"]),
    ("Optional",            [r"\bOptional\b"]),
    ("Try/catch",           [r"\btry\s*\{", r"\bcatch\s*\("]),
    ("Throws",              [r"\bthrows\b"]),
]

MAX_CONCEPTS = 6

def detect_concepts(code: str) -> str:
    if not code.strip():
        return "—"
    found = []
    for label, patterns in CONCEPT_RULES:
        for pattern in patterns:
            if re.search(pattern, code):
                found.append(label)
                break
    return ", ".join(found[:MAX_CONCEPTS]) if found else "Basic output"

# ── Auth ──────────────────────────────────────────────────────────────────────

def exercism_headers():
    token = os.environ.get("EXERCISM_TOKEN", "").strip()
    if not token:
        print("❌  EXERCISM_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}

# ── Cache ─────────────────────────────────────────────────────────────────────

def load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

# ── Fetch solutions ───────────────────────────────────────────────────────────

def fetch_solutions(headers: dict) -> list:
    print("📥  Fetching your Exercism solutions …")
    solutions = []

    url = f"{EXERCISM_API}/solutions?track_slug={TRACK}"
    while url:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 401:
            print("❌  Invalid or expired EXERCISM_TOKEN.", file=sys.stderr)
            sys.exit(1)
        if not resp.ok:
            print(f"   ⚠️  HTTP {resp.status_code}")
            break
        data = resp.json()
        for sol in data.get("solutions", []):
            status = sol.get("status", "")
            slug   = sol.get("exercise", {}).get("slug", "?")
            if status in ("published", "completed", "iterated", "started"):
                solutions.append(sol)
                print(f"        ✔ {slug} ({status})")
        url = data.get("meta", {}).get("links", {}).get("next")

    # fallback
    if not solutions:
        print("   ⚠️  Trying sideload fallback …")
        r2 = requests.get(f"{EXERCISM_API}/tracks/{TRACK}/exercises?sideload[]=solutions", headers=headers, timeout=15)
        if r2.ok:
            for sol in r2.json().get("solutions", []):
                if sol.get("status") in ("published", "completed", "iterated", "started"):
                    solutions.append(sol)

    solutions.sort(key=lambda s: s.get("submitted_at") or s.get("created_at") or "")
    print(f"   ✅  {len(solutions)} solution(s) found.")
    return solutions

# ── Fetch solution source code ────────────────────────────────────────────────

def fetch_solution_code(solution: dict, headers: dict) -> str:
    uuid = solution.get("uuid", "")
    slug = solution.get("exercise", {}).get("slug", "?")

    if not uuid:
        return ""

    # Step 1 — get solution detail with iterations sideloaded
    detail_url = f"{EXERCISM_API}/solutions/{uuid}?sideload[]=iterations"
    resp = requests.get(detail_url, headers=headers, timeout=15)
    if not resp.ok:
        print(f"      ⚠️  detail fetch failed: HTTP {resp.status_code}")
        return ""

    data       = resp.json()
    iterations = data.get("iterations", [])

    if not iterations:
        print(f"      ⚠️  no iterations found")
        return ""

    # DEBUG: print the full latest iteration object so we can see all fields
    latest = iterations[-1]
    print(f"      🔑  iteration keys: {list(latest.keys())}")
    print(f"      🔑  iteration data: {json.dumps(latest, indent=8)[:600]}")

    # Step 2 — try every plausible field name for the files URL
    files_url = (
        latest.get("files_url")
        or latest.get("download_url")
        or latest.get("submission_url")
        or ""
    )

    # Step 3 — if no URL field, try building it from the solution's
    #           file_download_base_url (old v1 style still present in v2)
    if not files_url:
        base = data.get("solution", {}).get("file_download_base_url", "")
        print(f"      ℹ️  file_download_base_url = {base!r}")
        sol_files = data.get("solution", {}).get("files", [])
        print(f"      ℹ️  solution.files = {sol_files}")
        if base and sol_files:
            code_parts = []
            for f in sol_files:
                if f.endswith(".java") and "Test" not in f:
                    fc = requests.get(base + f, headers=headers, timeout=15)
                    print(f"      📄  {f} → HTTP {fc.status_code} | {len(fc.text)} chars")
                    if fc.ok and fc.text.strip():
                        code_parts.append(fc.text)
            if code_parts:
                return "\n\n".join(code_parts)

    if not files_url:
        print(f"      ⚠️  no files URL found anywhere")
        return ""

    # Step 4 — fetch file listing from files_url
    fr = requests.get(files_url, headers=headers, timeout=15)
    print(f"      🌐  files listing → HTTP {fr.status_code}")
    if not fr.ok:
        return ""

    files      = fr.json().get("files", [])
    code_parts = []
    for file_info in files:
        filename = file_info.get("filename", "")
        if filename.endswith(".java") and "Test" not in filename:
            file_url = file_info.get("url") or file_info.get("download_url", "")
            if file_url:
                fc = requests.get(file_url, headers=headers, timeout=15)
                if fc.ok and fc.text.strip():
                    code_parts.append(fc.text)

    return "\n\n".join(code_parts)

# ── Build table ───────────────────────────────────────────────────────────────

def humanize(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.split("-"))

def build_table(solutions: list, headers: dict) -> str:
    cache   = load_cache()
    changed = False

    header = (
        "| # | Exercise | Concepts Used |\n"
        "|---|----------|---------------|"
    )
    rows = []

    for i, sol in enumerate(solutions, start=1):
        ex    = sol.get("exercise", {})
        slug  = ex.get("slug", "")
        title = ex.get("title", humanize(slug))
        url   = f"https://exercism.org/tracks/java/exercises/{slug}"

        if slug in cache:
            concepts = cache[slug]
            print(f"   📦  {title} — cached: {concepts}")
        else:
            print(f"\n   🔍  {title} …")
            code     = fetch_solution_code(sol, headers)
            concepts = detect_concepts(code)
            print(f"        → {concepts}")
            cache[slug] = concepts
            changed = True
            time.sleep(0.5)

        rows.append(f"| {i} | [{title}]({url}) | {concepts} |")

    if changed:
        save_cache(cache)
        print("\n   💾  Cache saved.")

    return header + "\n" + "\n".join(rows)

# ── Update README ─────────────────────────────────────────────────────────────

def update_readme(table: str):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER_START not in content or MARKER_END not in content:
        print(f"❌  Markers not found in {README_PATH}.", file=sys.stderr)
        sys.exit(1)

    new_block   = f"{MARKER_START}\n{table}\n{MARKER_END}"
    new_content = re.sub(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}",
        new_block,
        content,
        flags=re.DOTALL,
    )

    if new_content == content:
        print("ℹ️   README already up to date.")
        return

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅  README.md updated.")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    headers   = exercism_headers()
    solutions = fetch_solutions(headers)

    if not solutions:
        print("⚠️   No solutions found — README not changed.")
        return

    print(f"\n🔎  Scanning {len(solutions)} exercise(s) …")
    table = build_table(solutions, headers)
    update_readme(table)

if __name__ == "__main__":
    main()
