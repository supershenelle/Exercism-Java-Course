"""
update_readme.py
────────────────
Fetches your completed Exercism Java solutions via the Exercism API,
enriches each exercise with concept tags pulled from the official
exercism/java config.json on GitHub, then rewrites the
<!-- EXERCISM-START --> … <!-- EXERCISM-END --> block in README.md.

Requirements
  pip install requests

Environment variables (set as GitHub Actions secrets or locally)
  EXERCISM_TOKEN   – your personal Exercism API token
                     (get it at https://exercism.org/settings/api_cli)
"""

import os
import re
import sys
import json
import requests

# ── Config ────────────────────────────────────────────────────────────────────

EXERCISM_API   = "https://exercism.org/api/v2"
TRACK          = "java"
README_PATH    = "README.md"
MARKER_START   = "<!-- EXERCISM-START -->"
MARKER_END     = "<!-- EXERCISM-END -->"

# Raw URL for the official Java track config (contains concepts per exercise)
JAVA_CONFIG_URL = (
    "https://raw.githubusercontent.com/exercism/java/main/config.json"
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_headers():
    token = os.environ.get("EXERCISM_TOKEN", "").strip()
    if not token:
        print("❌  EXERCISM_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}


def fetch_java_concepts():
    """
    Download exercism/java config.json and build a lookup dict:
      { slug -> [concept, concept, …] }
    Both concept exercises (teaches) and practice exercises (practices) are included.
    """
    print("📥  Fetching Java track config from GitHub …")
    resp = requests.get(JAVA_CONFIG_URL, timeout=15)
    resp.raise_for_status()
    config = resp.json()

    concept_map = {}

    # Concept exercises: the "concepts" key lists what the exercise *teaches*
    for ex in config.get("exercises", {}).get("concept", []):
        slug = ex["slug"]
        concepts = ex.get("concepts", [])
        concept_map[slug] = concepts

    # Practice exercises: the "practices" key lists what the exercise *practices*
    for ex in config.get("exercises", {}).get("practice", []):
        slug = ex["slug"]
        concepts = ex.get("practices", [])
        if concepts:
            concept_map[slug] = concepts

    print(f"   ✅  Loaded concepts for {len(concept_map)} exercises.")
    return concept_map


def fetch_solutions(headers):
    """
    Return a list of completed/published solutions for the Java track,
    ordered by completion date (oldest first).

    Uses /tracks/{track}/exercises?sideload[]=solutions which is the
    correct Exercism v2 endpoint for fetching a user's own solutions.
    Falls back to /solutions endpoint if the first returns nothing.
    """
    print("📥  Fetching your Exercism solutions …")
    solutions = []

    # ── Strategy 1: sideload solutions from the exercises endpoint ────────────
    url = f"{EXERCISM_API}/tracks/{TRACK}/exercises?sideload[]=solutions"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 401:
        print("❌  Invalid or expired EXERCISM_TOKEN.", file=sys.stderr)
        sys.exit(1)

    if resp.ok:
        data = resp.json()
        # Print raw keys to help debug if still 0
        print(f"   ℹ️   API response keys: {list(data.keys())}")
        for sol in data.get("solutions", []):
            status = sol.get("status", "")
            print(f"   ℹ️   Exercise: {sol.get('exercise', {}).get('slug')} | status: {status}")
            if status in ("published", "completed", "iterated", "started"):
                solutions.append(sol)

    # ── Strategy 2: fallback to /solutions endpoint ───────────────────────────
    if not solutions:
        print("   ⚠️  Strategy 1 returned 0 — trying /solutions fallback …")
        url2 = f"{EXERCISM_API}/solutions?track_slug={TRACK}"
        resp2 = requests.get(url2, headers=headers, timeout=15)
        if resp2.ok:
            data2 = resp2.json()
            print(f"   ℹ️   Fallback API response keys: {list(data2.keys())}")
            for sol in data2.get("solutions", []):
                status = sol.get("status", "")
                print(f"   ℹ️   Exercise: {sol.get('exercise', {}).get('slug')} | status: {status}")
                if status in ("published", "completed", "iterated", "started"):
                    solutions.append(sol)

    # Sort oldest first by submitted_at date
    solutions.sort(key=lambda s: s.get("submitted_at") or s.get("created_at") or "")

    print(f"   ✅  Found {len(solutions)} completed solution(s).")
    return solutions


def humanize(slug: str) -> str:
    """Convert a kebab-case slug into Title Case words."""
    return " ".join(word.capitalize() for word in slug.split("-"))


def format_concepts(concepts: list) -> str:
    """Turn a list of concept slugs into a readable string."""
    if not concepts:
        return "—"
    return ", ".join(humanize(c) for c in concepts)


def build_table(solutions: list, concept_map: dict) -> str:
    """Build the Markdown table string."""
    header = (
        "| # | Exercise | Concepts Practiced |\n"
        "|---|----------|--------------------|"
    )
    rows = []
    for i, sol in enumerate(solutions, start=1):
        ex       = sol.get("exercise", {})
        title    = ex.get("title", humanize(ex.get("slug", "unknown")))
        slug     = ex.get("slug", "")
        url      = f"https://exercism.org/tracks/java/exercises/{slug}"
        concepts = concept_map.get(slug, [])
        rows.append(f"| {i} | [{title}]({url}) | {format_concepts(concepts)} |")

    return header + "\n" + "\n".join(rows)


def update_readme(table: str):
    """Replace the content between the markers in README.md."""
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER_START not in content or MARKER_END not in content:
        print(
            f"❌  Could not find markers in {README_PATH}.\n"
            f"    Add {MARKER_START} and {MARKER_END} around your table.",
            file=sys.stderr,
        )
        sys.exit(1)

    new_block = f"{MARKER_START}\n{table}\n{MARKER_END}"
    new_content = re.sub(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}",
        new_block,
        content,
        flags=re.DOTALL,
    )

    if new_content == content:
        print("ℹ️   README is already up to date — nothing to write.")
        return

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅  {README_PATH} updated successfully.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    headers     = get_headers()
    concept_map = fetch_java_concepts()
    solutions   = fetch_solutions(headers)

    if not solutions:
        print("⚠️   No completed solutions found — README not changed.")
        return

    table = build_table(solutions, concept_map)
    update_readme(table)


if __name__ == "__main__":
    main()
