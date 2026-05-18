"""
update_readme.py
────────────────

Requirements: pip install requests
Env vars (auto-set in GitHub Actions): GITHUB_TOKEN, GITHUB_REPOSITORY
"""

import os
import re
import sys
import json
import time
import requests

# ── Config ────────────────────────────────────────────────────────────────────

TRACK         = "java"
README_PATH   = "README.md"
MARKER_START  = "<!-- EXERCISM-START -->"
MARKER_END    = "<!-- EXERCISM-END -->"
CACHE_PATH    = "scripts/.concepts_cache.json"
BRANCH_PREFIX = "exercism-sync/"

# ── Concept detection ─────────────────────────────────────────────────────────
# Ordered from most specific to least specific.
# Each rule: (label, [regex patterns]) — first match wins for that label.
# Rules higher up take priority in the MAX_CONCEPTS cap.

CONCEPT_RULES = [
    # -- Functional / advanced (check early, they're distinctive) --
    ("Streams API",         [r"\.stream\(\)", r"\bStream\."]),
    ("Lambda expressions",  [r"\w+\s*->\s*\w"]),          # x -> expr (not just ->)
    ("Optional",            [r"\bOptional\b"]),
    ("Generics",            [r"<[A-Z]\w*>"]),

    # -- Collections --
    ("ArrayList",           [r"\bnew\s+ArrayList\b"]),
    ("HashMap",             [r"\bnew\s+HashMap\b"]),
    ("HashSet",             [r"\bnew\s+HashSet\b"]),
    ("Collections API",     [r"\bCollections\.\w"]),
    ("Arrays utility",      [r"\bArrays\.\w"]),

    # -- OOP (beyond basic class boilerplate) --
    ("Inheritance",         [r"\bextends\s+[A-Z]"]),
    ("Interfaces",          [r"\bimplements\s+[A-Z]", r"\binterface\s+\w"]),
    ("Abstract classes",    [r"\babstract\s+class\b"]),
    ("Enums",               [r"\benum\s+\w"]),
    ("Constructors",        [r"public\s+[A-Z]\w+\s*\([^)]*\)\s*\{"]),  # non-empty constructor
    ("Access modifiers",    [r"\bprivate\s+\w", r"\bprotected\s+\w"]),

    # -- Exception handling --
    ("Try/catch",           [r"\btry\s*\{", r"\bcatch\s*\(\w"]),
    ("Throws",              [r"\bthrows\s+[A-Z]"]),

    # -- Control flow --
    ("Switch statement",    [r"\bswitch\s*\("]),
    ("Ternary operator",    [r"\w\s*\?\s*\w[^:]*:[^?]"]),  # avoid matching generics
    ("For loop",            [r"\bfor\s*\(\s*(int|var|\w+\s+\w+)\s"]),
    ("While loop",          [r"\bwhile\s*\("]),
    ("Do-while loop",       [r"\bdo\s*\{"]),
    ("If/else",             [r"\bif\s*\(", r"\belse\s*\{"]),

    # -- String specific --
    ("StringBuilder",       [r"\bnew\s+StringBuilder\b"]),
    ("String formatting",   [r"String\.format\s*\(", r"\.formatted\s*\("]),
    ("String methods",      [r"\.(toUpperCase|toLowerCase|substring|indexOf|contains|replace|split|trim|startsWith|endsWith|charAt)\s*\("]),
    ("Char operations",     [r"\bchar\b(?!\s*\[)"]),       # char but not char[]

    # -- Math --
    ("Math class",          [r"\bMath\.(abs|pow|sqrt|round|floor|ceil|min|max|PI)\b"]),

    # -- Types --
    ("Arrays",              [r"\w+\s*\[\]\s*\w", r"new\s+\w+\s*\["]),  # actual array usage
    ("Null checks",         [r"==\s*null\b", r"!=\s*null\b", r"\bnull\b.*\bthrow\b"]),
    ("Type casting",        [r"\(\s*(int|double|long|float|char)\s*\)\s*\w"]),
    ("Constants",           [r"\bstatic\s+final\b"]),      # only static final, not just final
    ("Booleans",            [r"\breturn\s+(true|false)\b", r"\bboolean\s+\w+\s*="]),
    ("Doubles/floats",      [r"\b(double|float)\s+\w+\s*="]),
    ("Integers",            [r"\b(int|long)\s+\w+\s*="]),
]

MAX_CONCEPTS = 5

def detect_concepts(code: str) -> str:
    if not code.strip():
        return "—"

    # Strip comments so they don't trigger false matches
    code = re.sub(r"//.*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

    found = []
    for label, patterns in CONCEPT_RULES:
        for pattern in patterns:
            if re.search(pattern, code):
                found.append(label)
                break
        if len(found) >= MAX_CONCEPTS:
            break

    return ", ".join(found) if found else "Basic output"

# ── GitHub helpers ────────────────────────────────────────────────────────────

def github_headers():
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def get_repo():
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if not repo:
        print("❌  GITHUB_REPOSITORY not set.", file=sys.stderr)
        sys.exit(1)
    return repo

# ── List branches ─────────────────────────────────────────────────────────────

def list_sync_branches(repo: str, headers: dict) -> list:
    print("📋  Listing exercism-sync branches …")
    branches = []
    url = f"https://api.github.com/repos/{repo}/branches?per_page=100"
    while url:
        resp = requests.get(url, headers=headers, timeout=15)
        if not resp.ok:
            print(f"   ⚠️  GitHub API HTTP {resp.status_code}")
            break
        for b in resp.json():
            name = b.get("name", "")
            if name.startswith(BRANCH_PREFIX):
                branches.append(name)
        link = resp.headers.get("Link", "")
        url  = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
    print(f"   ✅  {len(branches)} branch(es) found.")
    return branches

# ── Read branch ───────────────────────────────────────────────────────────────

# Path pattern inside each branch:
#   solutions/java/{slug}/{iteration}/src/main/java/{Class}.java
SLUG_RE = re.compile(r"^solutions/java/([^/]+)/\d+/src/main/java/.+\.java$")

def read_branch(repo: str, branch: str, headers: dict) -> tuple:
    """Returns (slug, title, code) or (None, None, '') on failure."""
    tree_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    resp = requests.get(tree_url, headers=headers, timeout=15)
    if not resp.ok:
        return None, None, ""

    tree  = resp.json().get("tree", [])
    paths = [item["path"] for item in tree if item.get("type") == "blob"]

    slug = None
    for path in paths:
        m = SLUG_RE.match(path)
        if m:
            slug = m.group(1)
            break

    if not slug:
        # Fallback: .exercism/metadata.json
        for path in paths:
            if path.endswith("metadata.json"):
                raw = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
                mr  = requests.get(raw, timeout=15)
                if mr.ok:
                    try:
                        meta = mr.json()
                        slug = (
                            meta.get("exercise", {}).get("slug")
                            or meta.get("exercise_id", "")
                        )
                    except Exception:
                        pass
                break

    if not slug:
        return None, None, ""

    title = " ".join(w.capitalize() for w in slug.split("-"))

    # Download solution .java files (skip Test files)
    code_parts = []
    for path in paths:
        if SLUG_RE.match(path) and "Test" not in path:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
            fc = requests.get(raw_url, timeout=15)
            if fc.ok and fc.text.strip():
                code_parts.append(fc.text)

    return slug, title, "\n\n".join(code_parts)

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

# ── Build table ───────────────────────────────────────────────────────────────

def build_table(branches: list, repo: str, gh_headers: dict) -> str:
    cache     = load_cache()
    changed   = False
    exercises = {}   # slug -> (title, concepts)

    for branch in branches:
        slug, title, code = read_branch(repo, branch, gh_headers)
        if not slug:
            print(f"   ⚠️  Could not identify exercise in {branch}")
            continue

        if slug in exercises:
            continue  # deduplicate (multiple branches for same exercise)

        if slug in cache:
            exercises[slug] = (title, cache[slug])
            print(f"   📦  {title} — {cache[slug]}")
        else:
            concepts = detect_concepts(code)
            cache[slug]      = concepts
            exercises[slug]  = (title, concepts)
            changed = True
            print(f"   ✅  {title} — {concepts}")

        time.sleep(0.2)

    if changed:
        save_cache(cache)
        print("   💾  Cache saved.")

    if not exercises:
        return (
            "| # | Exercise | Concepts Used |\n"
            "|---|----------|---------------|\n"
            "| — | No exercises found | — |"
        )

    header = (
        "| # | Exercise | Concepts Used |\n"
        "|---|----------|---------------|"
    )
    rows = []
    for i, slug in enumerate(sorted(exercises), start=1):
        title, concepts = exercises[slug]
        url = f"https://exercism.org/tracks/{TRACK}/exercises/{slug}"
        rows.append(f"| {i} | [{title}]({url}) | {concepts} |")

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
    repo     = get_repo()
    gh_hdrs  = github_headers()
    branches = list_sync_branches(repo, gh_hdrs)

    if not branches:
        print("⚠️   No exercism-sync/* branches found.")
        return

    print(f"\n🔎  Reading {len(branches)} branch(es) …\n")
    table = build_table(branches, repo, gh_hdrs)
    update_readme(table)

if __name__ == "__main__":
    main()
