#!/usr/bin/env python3
"""Detect questions that repeat (near-verbatim) across many states' question banks.

Item 7 of issue #59. Marketing copy claims every question cites the state's manual.
A question copy-pasted into many states passes each state's individual gates but
signals over-generic content not actually grounded in state-specific material.

Sign questions (those with an ``image`` field) ARE supposed to repeat across states
because they all reference shared MUTCD signs in ``data/signs/``. They are filtered
out before clustering.

Usage:
    python3 tools/cross_state_dedupe.py [--threshold 0.85] [--min-states 5]
                                        [--out docs/quality/cross_state_clusters.md]

Output: a Markdown report at ``--out`` listing each cluster (states involved,
sample text, per-state question IDs). Reviewers eyeball the report once to
identify problematic clusters; the script itself is a one-shot diagnostic.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
from collections import defaultdict
from collections.abc import Iterable

import yaml
from _util import STATES_DIR
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT_DIR, "docs", "quality", "cross_state_clusters.md")

# Hand-curated header documenting which clusters are expected/legitimate so
# reviewers can quickly triage. Renders at the top of the report.
LEGITIMATE_CLUSTER_EXAMPLES = """\
## What this report is

Every cluster below is a group of questions whose stems are at least
**{threshold:.0%} similar** (TF-IDF cosine) and that appear in
**>= {min_states} distinct states**. Sign questions (those with an
``image`` field, referencing shared MUTCD signs in ``data/signs/``) are
excluded from analysis — they are *supposed* to repeat.

## How to triage clusters

**Legitimate clusters (no action needed)** — every state's manual covers these
topics, so similar phrasing is expected:

- Universal DUI / BAC limits (e.g., "What is the legal BAC limit for drivers 21+?")
- Basic right-of-way at uncontrolled intersections
- Stop-sign / red-light behavior
- Seat-belt requirements
- Speed limits in school / residential zones
- Following-distance rules (3-second / 2-second)

**Suspicious clusters (investigate)** — these suggest the question generator
leaned on LLM knowledge instead of the state's specific manual:

- A statute / law / fine amount that is state-specific but appears verbatim in
  many states (e.g., a California-specific demerit schedule appearing in NY)
- Phrasing that quotes a specific section number (e.g., "Section 4.2 says...")
  appearing across multiple states whose manuals have no such section
- Questions referencing a state-specific agency or program name (e.g., "the
  Illinois Rules of the Road booklet") appearing in states other than the one
  named

When in doubt: open the involved states' ``manual_text.txt`` and grep for the
distinctive phrase. If only one state's manual contains it, the others
contaminated their banks with that state's question.
"""


def load_state_questions(state_code: str) -> list[dict]:
    """Read a state's English questions, dropping sign (image-tagged) questions."""
    path = os.path.join(STATES_DIR, state_code, "questions_en.yaml")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    questions = data.get("questions") or []
    return [q for q in questions if not q.get("image")]


def iter_all_questions(states_dir: str = STATES_DIR) -> Iterable[tuple[str, dict]]:
    """Yield ``(state_code, question)`` pairs from every state's YAML."""
    if not os.path.isdir(states_dir):
        return
    for code in sorted(os.listdir(states_dir)):
        state_dir = os.path.join(states_dir, code)
        if not os.path.isdir(state_dir):
            continue
        path = os.path.join(state_dir, "questions_en.yaml")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        for q in data.get("questions") or []:
            if q.get("image"):
                continue
            yield code, q


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace. Keeps TF-IDF stable."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_clusters(
    records: list[tuple[str, dict]],
    threshold: float,
) -> list[set[int]]:
    """Cluster question indices whose pairwise cosine similarity >= threshold.

    Uses TF-IDF on character + word features. Union-find on the sparse similarity
    matrix (only entries >= threshold are followed) keeps memory reasonable for
    the ~16K-question corpus.
    """
    if not records:
        return []

    corpus = [normalize(q["question"]) for _, q in records]
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    matrix = vec.fit_transform(corpus)

    # Compute cosine in chunks to bound peak memory. Sparse matrix * sparse.T
    # produces a (chunk, N) dense float matrix per slice.
    n = len(corpus)
    chunk = 1024
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        sims = cosine_similarity(matrix[start:end], matrix)
        # Only consider the upper triangle (j > i) to avoid duplicate work.
        for local_i in range(end - start):
            i = start + local_i
            row = sims[local_i]
            # row[j] is similarity(i, j). Look only at j > i.
            for j in range(i + 1, n):
                if row[j] >= threshold:
                    union(i, j)

    groups: dict[int, set[int]] = defaultdict(set)
    for idx in range(n):
        groups[find(idx)].add(idx)
    # Drop singletons.
    return [g for g in groups.values() if len(g) > 1]


def filter_clusters(
    clusters: list[set[int]],
    records: list[tuple[str, dict]],
    min_states: int,
) -> list[dict]:
    """Keep clusters spanning >= min_states distinct states; sort by breadth."""
    keep: list[dict] = []
    for cluster in clusters:
        by_state: dict[str, list[int]] = defaultdict(list)
        for idx in cluster:
            code, q = records[idx]
            qid = q.get("id", f"index-{idx}")
            by_state[code].append(qid)
        if len(by_state) < min_states:
            continue
        # Pick the shortest text as the representative sample (most likely the
        # generic / canonical phrasing).
        rep_idx = min(cluster, key=lambda i: len(records[i][1]["question"]))
        keep.append(
            {
                "size": len(cluster),
                "states": dict(sorted(by_state.items())),
                "sample": records[rep_idx][1]["question"].strip(),
            }
        )
    keep.sort(key=lambda c: (-len(c["states"]), -c["size"]))
    return keep


def render_report(
    clusters: list[dict],
    *,
    threshold: float,
    min_states: int,
    total_questions: int,
    total_states: int,
) -> str:
    """Produce the Markdown report body."""
    today = _dt.date.today().isoformat()
    lines: list[str] = []
    lines.append("# Cross-State Question Contamination Report")
    lines.append("")
    lines.append(f"**Date**: {today}  ")
    lines.append(f"**Threshold**: cosine similarity >= {threshold:.2f}  ")
    lines.append(f"**Min states per cluster**: {min_states}  ")
    lines.append(
        f"**Corpus**: {total_questions:,} non-sign questions across {total_states} states  "
    )
    lines.append(f"**Clusters found**: {len(clusters)}")
    lines.append("")
    lines.append(LEGITIMATE_CLUSTER_EXAMPLES.format(threshold=threshold, min_states=min_states))
    lines.append("")
    lines.append("## Clusters")
    lines.append("")

    if not clusters:
        lines.append(
            "No clusters found at the configured threshold. Either every state's"
            " questions are sufficiently distinct, or the threshold is too strict."
            " Try lowering ``--threshold`` (e.g., 0.75) for a softer scan."
        )
        lines.append("")
        return "\n".join(lines)

    for i, cluster in enumerate(clusters, start=1):
        states = cluster["states"]
        lines.append(f"### Cluster {i} - {len(states)} states, {cluster['size']} questions")
        lines.append("")
        lines.append(f"**Sample**: {cluster['sample']}")
        lines.append("")
        lines.append("| State | Question IDs |")
        lines.append("|-------|--------------|")
        for code, ids in states.items():
            id_str = ", ".join(str(x) for x in ids)
            lines.append(f"| {code} | {id_str} |")
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Minimum cosine similarity to cluster two questions (default 0.85).",
    )
    parser.add_argument(
        "--min-states",
        type=int,
        default=5,
        help="Minimum distinct states in a cluster to report it (default 5).",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help=f"Output Markdown path (default {DEFAULT_OUT}).",
    )
    parser.add_argument(
        "--states-dir",
        default=STATES_DIR,
        help="Override states directory (mainly for tests).",
    )
    args = parser.parse_args(argv)

    records = list(iter_all_questions(args.states_dir))
    total_states = len({code for code, _ in records})
    print(
        f"loaded {len(records):,} non-sign questions from {total_states} states",
        flush=True,
    )

    clusters_raw = build_clusters(records, args.threshold)
    print(f"raw clusters (size >= 2): {len(clusters_raw)}", flush=True)

    clusters = filter_clusters(clusters_raw, records, args.min_states)
    print(f"clusters spanning >= {args.min_states} states: {len(clusters)}", flush=True)

    report = render_report(
        clusters,
        threshold=args.threshold,
        min_states=args.min_states,
        total_questions=len(records),
        total_states=total_states,
    )

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write(report)
        if not report.endswith("\n"):
            f.write("\n")
    print(f"wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
