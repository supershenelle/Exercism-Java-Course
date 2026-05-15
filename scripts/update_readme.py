"""
update_readme.py
────────────────

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
    # OOP
    ("Classes",             [r"\bclass\b"]),
    ("Inheritance",         [r"\bextends\b"]),
    ("Interfaces",          [r"\bimplements\b", r"\binterface\b"]),
    ("Constructors",        [r"public\s+[A-Z]\w+\s*\("]),
    ("Access modifiers",    [r"\b(private|protected)\b"]),
    ("Static members",      [r"\bstatic\b"]),
    ("Enums",               [r"\benum\b"]),
    ("Abstract classes",    [r"\babstract\b"]),
    ("Generics",            [r"<[A-Z]\w*>"]),

    # Control flow
    ("If/else",             [r"\bif\s*\(", r"\belse\b"]),
    ("Switch statement",    [r"\bswitch\s*\("]),
    ("For loop",            [r"\bfor\s*\("]),
    ("While loop",          [r"\bwhile\s*\("]),
    ("Do-while loop",       [r"\bdo\s*\{"]),
    ("Ternary operator",    [r"\?[^:]+:"]),
    ("Break/continue",      [r"\b(break|continue)\b"]),

    # Data types
    ("Booleans",            [r"\bboolean\b"]),
    ("Integers",            [r"\b(int|long|short|byte)\b"]),
    ("Doubles/floats",      [r"\b(double|float)\b"]),
    ("Constants",           [r"\bfinal\b"]),
    ("Type casting",        [r"\([a-z]+\)\s*\w"]),
    ("Null checks",         [r"\bnull\b"]),

    # Strings
    ("String methods",      [r"\.(toUpperCase|toLowerCase|substring|indexOf|contains|replace|split|trim|startsWith|endsWith|charAt|length)\s*\("]),
    ("String concatenation",[r'"\s*\+']),
    ("String formatting",   [r"String\.format\s*\(", r"\.formatted\s*\("]),
    ("StringBuilder",       [r"\bStringBuilder\b"]),
    ("Char operations",     [r"\bchar\b"]),

    # Math
    ("Math class",          [r"\bMath\."]),

    # Arrays
    ("Arrays",              [r"\w+\s*\[\]", r"\bArrays\."]),

    # Collections
    ("ArrayList",           [r"\bArrayList\b"]),
    ("HashMap",             [r"\bHashMap\b"]),
    ("HashSet",             [r"\bHashSet\b"]),
    ("Collections API",     [r"\bCollections\."]),

    # Functional
    ("Lambda expressions",  [r"->"]),
    ("Streams API",         [r"\.stream\(\)"]),
    ("Optional",            [r"\bOptional\b"]),

    # Exceptions
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

    url = f"{EXERCISM_API}/tracks/{TRACK}/exercises?sideload[]=solutions"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 401:
        print("❌  Invalid or expired EXERCISM_TOKEN.", file=sys.stderr)
        sys.exit(1)

    if resp.ok:
        data = resp.json()
        for sol in data.get("solutions", []):
            status = sol.get("status", "")
            slug   = sol.get("exercise", {}).get("slug", "?")
            print(f"        {slug} → status={status} | uuid={sol.get('uuid', 'NO-UUID')}")
            if status in ("published", "completed", "iterated", "started"):
                solutions.append(sol)

    if not solutions:
        print("   ⚠️  Trying /solutions fallback …")
        url2  = f"{EXERCISM_API}/solutions?track_slug={TRACK}"
        resp2 = requests.get(url2, headers=headers, timeout=15)
        if resp2.ok:
            data2 = resp2.json()
            for sol in data2.get("solutions", []):
                status = sol.get("status", "")
                slug   = sol.get("exercise", {}).get("slug", "?")
                print(f"        {slug} → status={status} | uuid={sol.get('uuid', 'NO-UUID')}")
                if status in ("published", "completed", "iterated", "started"):
                    solutions.append(sol)

    solutions.sort(key=lambda s: s.get("submitted_at") or s.get("created_at") or "")
    print(f"   ✅  Found {len(solutions)} solution(s).")
    return solutions

# ── Fetch solution source code ────────────────────────────────────────────────

def fetch_solution_code(solution: dict, headers: dict) -> str:
    """
    Try multiple approaches to get the .java source for a solution.
    Prints debug info so we can see exactly what's happening.
    """
    # The UUID can live in different places depending on the endpoint used
    uuid = (
        solution.get("uuid")
        or solution.get("id")
        or solution.get("solution", {}).get("uuid")
        or ""
    )

    slug = solution.get("exercise", {}).get("slug", "?")
    print(f"      📄  {slug}: uuid={uuid!r}")

    if not uuid:
        print(f"      ⚠️  No UUID found for {slug}, skipping file fetch.")
        return ""

    # ── Approach A: /solutions/{uuid}/files listing ───────────────────────────
    files_url = f"{EXERCISM_API}/solutions/{uuid}/files"
    print(f"      🌐  GET {files_url}")
    resp = requests.get(files_url, headers=headers, timeout=15)
    print(f"           → HTTP {resp.status_code}")

    if resp.ok:
        payload = resp.json()
        print(f"           → keys: {list(payload.keys())}")
        files = payload.get("files", [])
        print(f"           → {len(files)} file(s): {[f.get('filename','?') for f in files]}")

        code_parts = []
        for file_info in files:
            filename = file_info.get("filename", "")
            if filename.endswith(".java") and "Test" not in filename:
                # try download_url first, then url, then filename-based download
                file_url = (
                    file_info.get("download_url")
                    or file_info.get("url")
                    or f"{EXERCISM_API}/solutions/{uuid}/files/{filename}"
                )
                print(f"           → downloading {filename} from {file_url}")
                fr = requests.get(file_url, headers=headers, timeout=15)
                print(f"              HTTP {fr.status_code} | {len(fr.text)} chars")
                if fr.ok and fr.text.strip():
                    code_parts.append(fr.text)

        if code_parts:
            return "\n\n".join(code_parts)

    # ── Approach B: direct file download by convention ────────────────────────
    # Exercism stores files at /solutions/{uuid}/files/src/main/java/{PascalSlug}.java
    pascal = "".join(w.capitalize() for w in slug.split("-"))
    direct_url = f"{EXERCISM_API}/solutions/{uuid}/files/src/main/java/{pascal}.java"
    print(f"      🌐  Trying direct: {direct_url}")
    dr = requests.get(direct_url, headers=headers, timeout=15)
    print(f"           → HTTP {dr.status_code} | {len(dr.text)} chars")
    if dr.ok and dr.text.strip():
        return dr.text

    print(f"      ⚠️  Could not retrieve code for {slug}")
    return ""

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
            print(f"        → detected: {concepts}")
            cache[slug] = concepts
            changed = True
            time.sleep(0.3)

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

    print(f"\n🔎  Scanning concepts for {len(solutions)} exercise(s) …")
    table = build_table(solutions, headers)
    update_readme(table)

if __name__ == "__main__":
    main()
