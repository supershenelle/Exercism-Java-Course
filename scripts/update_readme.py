"""
update_readme.py
────────────────
Reads your Exercism Java solution files from exercism-sync/{uuid} branches,
identifies the exercise from the folder structure inside each branch,
detects Java concepts via pattern matching, then rewrites the
<!-- EXERCISM-START --> … <!-- EXERCISM-END --> block in README.md.

Requirements
  pip install requests

Environment variables (automatically available in GitHub Actions — no setup needed)
  GITHUB_TOKEN      – auto-injected by GitHub Actions
  GITHUB_REPOSITORY – auto-set to "owner/repo"
"""

import os
import re
import sys
import json
import time
import requests

# ── Config ────────────────────────────────────────────────────────────────────

TRACK        = "java"
README_PATH  = "README.md"
MARKER_START = "<!-- EXERCISM-START -->"
MARKER_END   = "<!-- EXERCISM-END -->"
CACHE_PATH   = "scripts/.concepts_cache.json"
BRANCH_PREFIX = "exercism-sync/"

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

# ── List exercism-sync branches ───────────────────────────────────────────────

def list_sync_branches(repo: str, headers: dict) -> list:
    print("📋  Listing exercism-sync branches …")
    branches = []
    url = f"https://api.github.com/repos/{repo}/branches?per_page=100"
    while url:
        resp = requests.get(url, headers=headers, timeout=15)
        if not resp.ok:
            print(f"   ⚠️  GitHub API HTTP {resp.status_code}: {resp.text[:200]}")
            break
        for b in resp.json():
            name = b.get("name", "")
            if name.startswith(BRANCH_PREFIX):
                branches.append(name)
        link = resp.headers.get("Link", "")
        url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
    print(f"   ✅  Found {len(branches)} sync branch(es).")
    return branches

# ── Read branch contents ──────────────────────────────────────────────────────

def read_branch(repo: str, branch: str, headers: dict) -> tuple:
    """
    Returns (slug, title, code) by inspecting the branch's file tree.
    The Exercism syncer stores files under: java/{exercise-slug}/src/main/java/
    We find the slug from the folder structure, then read the .java files.
    """
    tree_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    resp = requests.get(tree_url, headers=headers, timeout=15)
    if not resp.ok:
        print(f"      ⚠️  tree HTTP {resp.status_code} for {branch}")
        return None, None, ""

    tree  = resp.json().get("tree", [])
    paths = [item["path"] for item in tree if item.get("type") == "blob"]

    # Debug: print all paths in first branch to understand structure
    if len(paths) < 20:  # only print for small trees to avoid log spam
        print(f"      📁  files: {paths}")

    # Find the exercise slug — look for .java solution files
    # Exercism syncer path pattern: java/{slug}/src/main/java/{ClassName}.java
    # or sometimes just: {slug}/src/main/java/{ClassName}.java
    slug  = None
    title = None

    for path in paths:
        parts = path.split("/")
        # Look for src/main/java in the path to identify exercise root
        if "src" in parts and "main" in parts and path.endswith(".java"):
            src_idx = parts.index("src")
            if src_idx >= 1:
                # The slug is the folder just before src/
                slug = parts[src_idx - 1]
                break

    # Fallback: try reading .exercism/metadata.json which stores exercise info
    if not slug:
        for path in paths:
            if path.endswith("metadata.json") and ".exercism" in path:
                raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
                mr = requests.get(raw_url, timeout=15)
                if mr.ok:
                    try:
                        meta = mr.json()
                        slug = meta.get("exercise", {}).get("slug") or meta.get("exercise_id", "")
                        title = meta.get("exercise", {}).get("title", "")
                        print(f"      📋  metadata slug: {slug!r}")
                    except Exception:
                        pass
                break

    if not slug:
        print(f"      ⚠️  could not determine slug for {branch}")
        return None, None, ""

    if not title:
        title = " ".join(w.capitalize() for w in slug.split("-"))

    # Download .java solution files (skip test files)
    code_parts = []
    for path in paths:
        if path.endswith(".java") and "Test" not in path:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
            fc = requests.get(raw_url, timeout=15)
            if fc.ok and fc.text.strip():
                print(f"      📄  {path} ({len(fc.text)} chars)")
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
    cache   = load_cache()
    changed = False

    # slug -> (title, concepts)
    exercises = {}

    for branch in branches:
        print(f"\n   🔍  {branch} …")
        slug, title, code = read_branch(repo, branch, gh_headers)
        if not slug:
            continue

        if slug in cache:
            exercises[slug] = (title, cache[slug])
            print(f"        📦  {title} — cached: {cache[slug]}")
        else:
            concepts = detect_concepts(code)
            cache[slug] = concepts
            exercises[slug] = (title, concepts)
            changed = True
            print(f"        → {concepts}")

        time.sleep(0.3)

    if changed:
        save_cache(cache)
        print("\n   💾  Cache saved.")

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
    for i, (slug, (title, concepts)) in enumerate(sorted(exercises.items()), start=1):
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

    print(f"\n🔎  Reading {len(branches)} branch(es) …")
    table = build_table(branches, repo, gh_hdrs)
    update_readme(table)

if __name__ == "__main__":
    main()
