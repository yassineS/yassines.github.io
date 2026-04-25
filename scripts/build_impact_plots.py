#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas>=2.0",
#   "matplotlib>=3.7",
# ]
# ///
"""Aggregate Altmetric exports into summary CSVs and impact-page SVG plots.

Source CSVs (kept outside the repo by default):
    Altmetric - Mentions - Adelaide University - YYYY-MM-DD.csv     (full mentions)
    Altmetric - Mentions - Adelaide University - YYYY-MM-DD(1).csv  (policy + extras)
    Altmetric - News Demographics - Adelaide University - YYYY-MM-DD.csv

Outputs (committed to the repo):
    static/data/impact/mentions-by-country.csv
    static/data/impact/papers-engagement.csv
    static/data/impact/marquee-outlets.csv
    static/images/impact/mentions-by-country.svg
    static/images/impact/engagement-by-paper.svg

Run from the repo root, or pass --repo-root explicitly:
    ./scripts/build_impact_plots.py
    ./scripts/build_impact_plots.py --altmetric-dir ~/Projects/job_applications/papers
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Marquee outlet keywords mapped to a quality tier. Order matters: first match wins.
TIER_RULES: list[tuple[str, list[str]]] = [
    (
        "Tier-1 broadsheet",
        [
            "New York Times",
            "Washington Post",
            "The Guardian",
            "Financial Times",
            "Le Monde",
            "El Pais",
            "Der Spiegel",
            "SPIEGEL",
            "Süddeutsche",
            "Sueddeutsche",
            "Telegraph (UK)",
            "The Independent",
            "Daily Mail",
            "BBC",
            "Reuters",
            "CNN News",
            "CNN Philippines",
            "Bloomberg",
            "Newsweek",
            "Times of India",
            "Hindustan Times",
            "Irish Times",
        ],
    ),
    (
        "Tier-1 science press",
        [
            "Smithsonian",
            "Scientific American",
            "New Scientist",
            "National Geographic",
            "Science News",
            "Quanta",
            "Wired",
            "Forbes",
            "Discover Magazine",
            "Cosmos",
            "COSMOS",
            "Gizmodo",
            "Nature",
            "Conversation",
        ],
    ),
    (
        "Wire / aggregator",
        [
            "EurekAlert",
            "Phys.org",
            "MSN",
            "Yahoo!",
            "Mirage News",
            "Tech Times",
            "Verve times",
            "Sign of the Times",
        ],
    ),
    (
        "Regional Australian",
        [
            "Brisbane Times",
            "Canberra Times",
            "Sydney Morning Herald",
            "Mudgee Guardian",
            "Wellington Times",
            "Braidwood Times",
            "Katherine Times",
            "Manning River Times",
            "Wimmera Mail-Times",
            "Voxy",
        ],
    ),
]


# Short labels for the engagement plot — keyed by the start of the research-output title.
PAPER_LABELS: list[tuple[str, str, str]] = [
    # (title-prefix-match, short label, publication-date hint YYYY-MM)
    ("An ancient viral epidemic", "Souilmi 2021\nCurr. Biol.", "2021-06"),
    ("A global environmental crisis", "Cooper 2021\nScience", "2021-02"),
    ("Ancient genomes reveal over two thousand", "Souilmi 2024\nPNAS (dingo)", "2024-07"),
    ("A 1000-year-old case of Klinefelter", "Roca-Rada 2022\nLancet", "2022-08"),
    ("Admixture has obscured signals", "Souilmi 2022\nNat. Ecol. Evol.", "2022-10"),
    ("The role of genetic selection", "Tobler 2023\nPNAS (OOA)", "2023-05"),
    ("The impact of the cytoplasmic", "Rogers 2023\nKidney Int.", "2023-04"),
    ("The Dogma of Dingoes", "Cairns 2018\ndingo reply", "2018-03"),
    ("Response to Comment on", "Tobler 2021\nScience reply", "2021-11"),
]


def find_csv(altmetric_dir: Path, pattern: str) -> Path:
    matches = sorted(altmetric_dir.glob(pattern))
    if not matches:
        sys.exit(f"No file matched {pattern!r} in {altmetric_dir}")
    # Prefer the largest file when multiple are present (snapshot rotation).
    return max(matches, key=lambda p: p.stat().st_size)


def tier_for(outlet: str) -> str:
    for tier, keywords in TIER_RULES:
        for kw in keywords:
            if kw.lower() in outlet.lower():
                return tier
    return "Other / regional"


def short_label_for(title: str) -> tuple[str, str]:
    for prefix, label, pub_hint in PAPER_LABELS:
        if title.startswith(prefix):
            return label, pub_hint
    return title[:30], "2020-01"


def load_souilmi_mentions(big_csv: Path, extras_csv: Path) -> pd.DataFrame:
    """Load both Altmetric mention exports and filter to rows attributed to Souilmi."""
    frames = []
    for path in (big_csv, extras_csv):
        df = pd.read_csv(path, encoding="utf-8", encoding_errors="replace", dtype=str, on_bad_lines="warn")
        df = df.dropna(subset=["Authors at my Institution"])
        df = df[df["Authors at my Institution"].str.contains("Souilmi", na=False)].copy()
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["Altmetric Attention Score"] = pd.to_numeric(out["Altmetric Attention Score"], errors="coerce").fillna(0).astype(int)
    return out


def aggregate_papers(mentions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for title, group in mentions.groupby("Research Output Title"):
        score = int(group["Altmetric Attention Score"].max())
        total = len(group)
        marquee = sum(1 for outlet in group["Outlet or Author"].dropna() if tier_for(outlet) in {"Tier-1 broadsheet", "Tier-1 science press"})
        label, pub_hint = short_label_for(title)
        # Try to recover publication date from the rows themselves.
        pub_dates = pd.to_datetime(group["Publication Date"], errors="coerce").dropna()
        pub_date = pub_dates.iloc[0] if len(pub_dates) else pd.to_datetime(pub_hint + "-15")
        rows.append(
            {
                "title": title,
                "label": label,
                "publication_date": pub_date.date().isoformat(),
                "altmetric_score": score,
                "news_mentions": total,
                "marquee_mentions": marquee,
            }
        )
    return pd.DataFrame(rows).sort_values("publication_date").reset_index(drop=True)


def aggregate_outlets(mentions: pd.DataFrame) -> pd.DataFrame:
    counts = mentions["Outlet or Author"].fillna("(unknown)").value_counts()
    rows = [
        {"outlet": outlet, "tier": tier_for(outlet), "mentions": int(n)}
        for outlet, n in counts.items()
    ]
    return pd.DataFrame(rows).sort_values(["tier", "mentions"], ascending=[True, False]).reset_index(drop=True)


def plot_countries(country_csv: Path, out_path: Path, total_mentions: int, total_countries: int) -> None:
    df = pd.read_csv(country_csv).rename(columns={"Country name": "country", "Number of posts": "posts"})
    df = df.sort_values("posts", ascending=False).head(15).iloc[::-1]

    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    bars = ax.barh(df["country"], df["posts"], color="#3a5fa0", edgecolor="white")
    ax.set_xlabel("News mentions")
    ax.set_title("News mentions by country (top 15)", loc="left", fontsize=12, weight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#dddddd", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, df["posts"]):
        ax.text(value + max(df["posts"]) * 0.01, bar.get_y() + bar.get_height() / 2, str(int(value)),
                va="center", ha="left", fontsize=9, color="#333333")
    fig.text(
        0.0,
        -0.02,
        f"{total_mentions:,} total mentions across {total_countries} countries (Altmetric, snapshot 2026-04-01).",
        ha="left",
        fontsize=8,
        color="#555555",
        transform=ax.transAxes,
    )
    plt.rcParams["svg.fonttype"] = "none"
    fig.savefig(out_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_engagement(papers: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    df = papers.copy()
    df["publication_date"] = pd.to_datetime(df["publication_date"])
    sizes = df["news_mentions"].clip(lower=1) * 2.5

    sc = ax.scatter(
        df["publication_date"],
        df["altmetric_score"].clip(lower=1),
        s=sizes,
        alpha=0.55,
        color="#c1573b",
        edgecolor="white",
        linewidth=1.0,
    )
    ax.set_yscale("log")
    ax.set_ylabel("Altmetric Attention Score (log scale)")
    ax.set_xlabel("Publication date")
    ax.set_title("Research engagement by publication", loc="left", fontsize=12, weight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, color="#dddddd", linewidth=0.6, which="both", zorder=0)
    ax.set_axisbelow(True)

    for _, row in df.iterrows():
        ax.annotate(
            row["label"],
            xy=(row["publication_date"], row["altmetric_score"]),
            xytext=(8, 6),
            textcoords="offset points",
            fontsize=8,
            color="#333333",
        )

    fig.text(
        0.0,
        -0.06,
        "Bubble size proportional to total tracked news mentions per paper. Source: Altmetric, 2026-04-01.",
        ha="left",
        fontsize=8,
        color="#555555",
        transform=ax.transAxes,
    )
    plt.rcParams["svg.fonttype"] = "none"
    fig.savefig(out_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    here = Path(__file__).resolve()
    default_repo = here.parent.parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--altmetric-dir",
        type=Path,
        default=Path("~/Projects/job_applications/papers").expanduser(),
        help="Directory containing the three Altmetric CSV exports.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_repo,
        help="Repo root; outputs go under data/impact and static/images/impact.",
    )
    args = parser.parse_args()

    big = find_csv(args.altmetric_dir, "Altmetric - Mentions - * - *.csv")
    # The file with "(1).csv" should be the smaller extras file
    extras_candidates = list(args.altmetric_dir.glob("Altmetric - Mentions - *(1).csv"))
    extras = extras_candidates[0] if extras_candidates else big
    if extras == big:
        sys.stderr.write("Warning: no separate '(1).csv' extras file found; using primary mentions only.\n")
    countries = find_csv(args.altmetric_dir, "Altmetric - News Demographics - * - *.csv")

    data_dir = args.repo_root / "static" / "data" / "impact"
    img_dir = args.repo_root / "static" / "images" / "impact"
    data_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    mentions = load_souilmi_mentions(big, extras)
    papers = aggregate_papers(mentions)
    outlets = aggregate_outlets(mentions)
    country_df = pd.read_csv(countries)

    papers.to_csv(data_dir / "papers-engagement.csv", index=False)
    outlets.to_csv(data_dir / "marquee-outlets.csv", index=False)
    country_df.to_csv(data_dir / "mentions-by-country.csv", index=False)

    total_mentions = int(country_df["Number of posts"].sum())
    total_countries = int((country_df["Number of posts"] > 0).sum())

    plot_countries(countries, img_dir / "mentions-by-country.svg", total_mentions, total_countries)
    plot_engagement(papers, img_dir / "engagement-by-paper.svg")

    print("Built impact summaries and plots:")
    print(f"  Souilmi-attributed mentions: {len(mentions):>5}")
    print(f"  Distinct papers covered:     {len(papers):>5}")
    print(f"  Total news posts (geo):      {total_mentions:>5}")
    print(f"  Countries:                   {total_countries:>5}")
    print(f"  Peak Altmetric score:        {int(papers['altmetric_score'].max()):>5}")
    print()
    print("Wrote:")
    for p in sorted([data_dir / "papers-engagement.csv", data_dir / "marquee-outlets.csv",
                     data_dir / "mentions-by-country.csv",
                     img_dir / "mentions-by-country.svg",
                     img_dir / "engagement-by-paper.svg"]):
        print(f"  {p.relative_to(args.repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
