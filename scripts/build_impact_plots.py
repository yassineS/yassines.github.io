#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas>=2.0",
#   "matplotlib>=3.7",
#   "adjustText>=1.0",
# ]
# ///
"""Aggregate Altmetric exports into summary CSVs and impact-page SVG plots.

Source CSVs (kept outside the repo by default):
    Altmetric - Mentions - Adelaide University - YYYY-MM-DD.csv     (full mentions)
    Altmetric - Mentions - Adelaide University - YYYY-MM-DD(1).csv  (policy + extras)
    Altmetric - News Demographics - Adelaide University - YYYY-MM-DD.csv

Outputs (committed to the repo):
    static/data/impact/mentions-by-country.csv
    static/data/impact/mentions-by-language.csv
    static/data/impact/papers-engagement.csv
    static/data/impact/marquee-outlets.csv
    static/images/impact/geographic-linguistic-breadth.svg
    static/images/impact/engagement-by-paper.svg

Run from the repo root, or pass --repo-root explicitly:
    ./scripts/build_impact_plots.py
    ./scripts/build_impact_plots.py --altmetric-dir ~/Projects/job_applications/papers
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text

# Marquee outlet keywords mapped to a quality tier. Order matters: first match wins.
TIER_RULES: list[tuple[str, list[str]]] = [
    (
        "Tier-1 broadsheet",
        [
            "New York Times", "Washington Post", "The Guardian", "Financial Times",
            "Le Monde", "El Pais", "Der Spiegel", "SPIEGEL", "Süddeutsche", "Sueddeutsche",
            "Telegraph (UK)", "The Independent", "Daily Mail", "BBC", "Reuters",
            "CNN News", "CNN Philippines", "Bloomberg", "Newsweek",
            "Times of India", "Hindustan Times", "Irish Times",
        ],
    ),
    (
        "Tier-1 science press",
        [
            "Smithsonian", "Scientific American", "New Scientist", "National Geographic",
            "Science News", "Quanta", "Wired", "Forbes", "Discover Magazine",
            "Cosmos", "COSMOS", "Gizmodo", "Nature", "Conversation",
        ],
    ),
    (
        "Wire / aggregator",
        [
            "EurekAlert", "Phys.org", "MSN", "Yahoo!", "Mirage News",
            "Tech Times", "Verve times", "Sign of the Times",
        ],
    ),
    (
        "Regional Australian",
        [
            "Brisbane Times", "Canberra Times", "Sydney Morning Herald",
            "Mudgee Guardian", "Wellington Times", "Braidwood Times",
            "Katherine Times", "Manning River Times", "Wimmera Mail-Times", "Voxy",
        ],
    ),
]


# Per-paper config for the engagement plot:
# (title-prefix-match, short single-line label, publication-date hint, label x-offset pts, label y-offset pts)
PAPER_LABELS: list[tuple[str, str, str, int, int]] = [
    ("An ancient viral epidemic",            "Souilmi 2021, Curr. Biol.",   "2021-06",  10,  18),
    ("A global environmental crisis",        "Cooper 2021, Science",        "2021-02", -15, -22),
    ("Ancient genomes reveal over two thousand", "Souilmi 2024, PNAS (dingo)",  "2024-07", -10,  20),
    ("A 1000-year-old case of Klinefelter",  "Roca-Rada 2022, Lancet",      "2022-08",   8, -22),
    ("Admixture has obscured signals",       "Souilmi 2022, Nat. Ecol. Evol.", "2022-10",  8,  16),
    ("The role of genetic selection",        "Tobler 2023, PNAS (OOA)",     "2023-05",   8,  16),
    ("The impact of the cytoplasmic",        "Rogers 2023, Kidney Int.",    "2023-04", -75, -20),
    ("The Dogma of Dingoes",                 "Cairns 2018, dingo reply",    "2018-03",  10,   6),
    ("Response to Comment on",               "Tobler 2021, Science reply",  "2021-11",  10,   6),
]


# Country → dominant news-press language. Used to convert Altmetric per-mention country
# values into a language attribution for the linguistic-breadth plot. Outlets in
# multilingual countries are bucketed to the dominant press language; outlet-name
# overrides handle the obvious exceptions (e.g. NatGeo en Español).
COUNTRY_TO_LANGUAGE: dict[str, str] = {
    "United States": "English", "United Kingdom": "English", "Australia": "English",
    "India": "English", "New Zealand": "English", "Canada": "English",
    "Ireland": "English", "Singapore": "English", "Malaysia": "English",
    "Pakistan": "English", "Bangladesh": "English", "Philippines": "English",
    "South Africa": "English", "Hong Kong": "English",
    "Germany": "German", "Austria": "German", "Switzerland": "German",
    "Spain": "Spanish", "Argentina": "Spanish", "Mexico": "Spanish",
    "Chile": "Spanish", "Colombia": "Spanish", "Peru": "Spanish",
    "Brazil": "Portuguese", "Portugal": "Portuguese",
    "France": "French", "Belgium": "French", "Luxembourg": "French",
    "Italy": "Italian",
    "Russia": "Russian",
    "Greece": "Greek",
    "Poland": "Polish",
    "Czechia": "Czech", "Czech Republic": "Czech",
    "Hungary": "Hungarian",
    "Netherlands": "Dutch",
    "Sweden": "Swedish",
    "Norway": "Norwegian",
    "Denmark": "Danish",
    "Finland": "Finnish",
    "Lithuania": "Lithuanian", "Latvia": "Latvian", "Estonia": "Estonian",
    "Turkey": "Turkish",
    "Israel": "Hebrew",
    "United Arab Emirates": "Arabic", "Qatar": "Arabic", "Saudi Arabia": "Arabic",
    "Lebanon": "Arabic", "Egypt": "Arabic",
    "China": "Chinese", "Taiwan": "Chinese",
    "Japan": "Japanese", "Korea, Republic of": "Korean", "South Korea": "Korean",
    "Indonesia": "Indonesian", "Vietnam": "Vietnamese", "Thailand": "Thai",
    "Georgia": "Georgian", "Azerbaijan": "Azerbaijani",
    "Kyrgyzstan": "Russian",  # Russian-language press dominant
    "Iran": "Persian",
}

# Outlet-name keywords that flag a non-default language regardless of country.
OUTLET_LANGUAGE_OVERRIDES: list[tuple[str, str]] = [
    ("en Español", "Spanish"),
    ("en Espa", "Spanish"),  # match mojibake variant
    ("en Italiano", "Italian"),
    ("Deutsch", "German"),
    ("Süddeutsche", "German"),
    ("Sputnik", "Russian"),
    ("Taipei Times", "English"),  # English-language Taiwan paper
    ("China Daily", "English"),
    ("Japan Times", "English"),
    ("Korea Herald", "English"),
    ("Le Figaro", "French"),
    ("Le Monde", "French"),
    ("La Vanguardia", "Spanish"),
    ("La Nación", "Spanish"),
]


def find_csv(altmetric_dir: Path, pattern: str) -> Path:
    matches = sorted(altmetric_dir.glob(pattern))
    if not matches:
        sys.exit(f"No file matched {pattern!r} in {altmetric_dir}")
    return max(matches, key=lambda p: p.stat().st_size)


def tier_for(outlet: str) -> str:
    for tier, keywords in TIER_RULES:
        for kw in keywords:
            if kw.lower() in outlet.lower():
                return tier
    return "Other / regional"


def short_label_for(title: str) -> tuple[str, str, int, int]:
    for prefix, label, pub_hint, dx, dy in PAPER_LABELS:
        if title.startswith(prefix):
            return label, pub_hint, dx, dy
    return title[:30], "2020-01", 8, 6


def language_for(country: str | None, outlet: str | None) -> str:
    outlet = outlet or ""
    for kw, lang in OUTLET_LANGUAGE_OVERRIDES:
        if kw.lower() in outlet.lower():
            return lang
    if country and country in COUNTRY_TO_LANGUAGE:
        return COUNTRY_TO_LANGUAGE[country]
    return "Other / unattributed"


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
        marquee = sum(
            1 for outlet in group["Outlet or Author"].dropna()
            if tier_for(outlet) in {"Tier-1 broadsheet", "Tier-1 science press"}
        )
        label, pub_hint, dx, dy = short_label_for(title)
        pub_dates = pd.to_datetime(group["Publication Date"], errors="coerce").dropna()
        pub_date = pub_dates.iloc[0] if len(pub_dates) else pd.to_datetime(pub_hint + "-15")
        rows.append({
            "title": title, "label": label,
            "publication_date": pub_date.date().isoformat(),
            "altmetric_score": score, "news_mentions": total, "marquee_mentions": marquee,
            "label_dx": dx, "label_dy": dy,
        })
    return pd.DataFrame(rows).sort_values("publication_date").reset_index(drop=True)


def aggregate_outlets(mentions: pd.DataFrame) -> pd.DataFrame:
    counts = mentions["Outlet or Author"].fillna("(unknown)").value_counts()
    rows = [
        {"outlet": outlet, "tier": tier_for(outlet), "mentions": int(n)}
        for outlet, n in counts.items()
    ]
    return pd.DataFrame(rows).sort_values(["tier", "mentions"], ascending=[True, False]).reset_index(drop=True)


def aggregate_languages(mentions: pd.DataFrame) -> pd.DataFrame:
    """Attribute each mention to a language via country + outlet-name overrides."""
    languages = mentions.apply(
        lambda r: language_for(r.get("Country"), r.get("Outlet or Author")), axis=1
    )
    counts = languages.value_counts()
    return (
        pd.DataFrame({"language": counts.index, "mentions": counts.values})
        .sort_values("mentions", ascending=False)
        .reset_index(drop=True)
    )


# ---------- plotting ----------------------------------------------------------------

FOOTNOTE_KW = dict(fontsize=8, color="#555555")


def _add_panel_footer(fig, ax, text: str) -> None:
    """Place a caption below the x-axis label, right-aligned to that axis."""
    # Use axes coordinates so the caption stays anchored to the panel even with subplots.
    ax.annotate(
        text,
        xy=(1.0, -0.18),
        xycoords="axes fraction",
        ha="right",
        va="top",
        **FOOTNOTE_KW,
    )


def plot_geo_linguistic(
    country_csv: Path,
    languages: pd.DataFrame,
    out_path: Path,
    total_mentions: int,
    total_countries: int,
    total_languages: int,
) -> None:
    countries_df = (
        pd.read_csv(country_csv)
        .rename(columns={"Country name": "country", "Number of posts": "posts"})
        .sort_values("posts", ascending=False)
        .head(15)
        .iloc[::-1]
    )

    fig, axes = plt.subplots(1, 2, figsize=(14.0, 5.5))
    plt.subplots_adjust(wspace=0.35, bottom=0.18)

    # --- Left: countries ---
    ax_l = axes[0]
    bars_l = ax_l.barh(countries_df["country"], countries_df["posts"], color="#3a5fa0", edgecolor="white")
    ax_l.set_xlabel("News mentions")
    ax_l.set_title("News mentions by country (top 15)", loc="left", fontsize=12, weight="bold", pad=12)
    ax_l.spines[["top", "right"]].set_visible(False)
    ax_l.grid(axis="x", color="#dddddd", linewidth=0.8, zorder=0)
    ax_l.set_axisbelow(True)
    pad = max(countries_df["posts"]) * 0.01
    for bar, value in zip(bars_l, countries_df["posts"]):
        ax_l.text(value + pad, bar.get_y() + bar.get_height() / 2, str(int(value)),
                  va="center", ha="left", fontsize=9, color="#333333")
    _add_panel_footer(
        fig, ax_l,
        f"{total_mentions:,} mentions across {total_countries} countries (Altmetric, snapshot 2026-04-01).",
    )

    # --- Right: languages ---
    lang_top = languages.head(12).iloc[::-1]
    ax_r = axes[1]
    bars_r = ax_r.barh(lang_top["language"], lang_top["mentions"], color="#c1573b", edgecolor="white")
    ax_r.set_xlabel("News mentions")
    ax_r.set_title("News mentions by language of the press outlet", loc="left", fontsize=12, weight="bold", pad=12)
    ax_r.spines[["top", "right"]].set_visible(False)
    ax_r.grid(axis="x", color="#dddddd", linewidth=0.8, zorder=0)
    ax_r.set_axisbelow(True)
    pad_r = max(lang_top["mentions"]) * 0.01
    for bar, value in zip(bars_r, lang_top["mentions"]):
        ax_r.text(value + pad_r, bar.get_y() + bar.get_height() / 2, str(int(value)),
                  va="center", ha="left", fontsize=9, color="#333333")
    _add_panel_footer(
        fig, ax_r,
        f"Coverage in {total_languages} languages (inferred from outlet country, with outlet-name overrides).",
    )

    plt.rcParams["svg.fonttype"] = "none"
    fig.savefig(out_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def plot_engagement(papers: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 6.0))
    plt.subplots_adjust(bottom=0.20)
    df = papers.copy()
    df["publication_date"] = pd.to_datetime(df["publication_date"])
    sizes = df["news_mentions"].clip(lower=1) * 2.5

    ax.scatter(
        df["publication_date"], df["altmetric_score"].clip(lower=1),
        s=sizes, alpha=0.55, color="#c1573b", edgecolor="white", linewidth=1.0,
    )
    ax.set_yscale("log")
    ax.set_ylabel("Altmetric Attention Score (log scale)")
    ax.set_xlabel("Publication date")
    ax.set_title("Research Impact for Selected Publications", loc="left", fontsize=12, weight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, color="#dddddd", linewidth=0.6, which="both", zorder=0)
    ax.set_axisbelow(True)

    texts = [
        ax.text(
            row["publication_date"],
            row["altmetric_score"],
            row["label"],
            fontsize=8,
            color="#333333",
        )
        for _, row in df.iterrows()
    ]
    adjust_text(
        texts,
        ax=ax,
        arrowprops=dict(arrowstyle="-", color="#888888", lw=0.6, shrinkA=2, shrinkB=4),
        expand_text=(1.15, 1.4),
        expand_points=(1.4, 1.6),
        force_text=(0.4, 0.6),
        force_points=(0.3, 0.5),
        only_move={"text": "xy"},
    )

    _add_panel_footer(
        fig, ax,
        "Bubble size proportional to total tracked news mentions per paper. Source: Altmetric, 2026-04-01.",
    )
    plt.rcParams["svg.fonttype"] = "none"
    fig.savefig(out_path, format="svg", bbox_inches="tight")
    plt.close(fig)


# ---------- main --------------------------------------------------------------------


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
        help="Repo root; outputs go under static/data/impact and static/images/impact.",
    )
    args = parser.parse_args()

    big = find_csv(args.altmetric_dir, "Altmetric - Mentions - * - *.csv")
    extras_candidates = list(args.altmetric_dir.glob("Altmetric - Mentions - *(1).csv"))
    extras = extras_candidates[0] if extras_candidates else big
    if extras == big:
        sys.stderr.write("Warning: no separate '(1).csv' extras file found; using primary mentions only.\n")
    countries_csv = find_csv(args.altmetric_dir, "Altmetric - News Demographics - * - *.csv")

    data_dir = args.repo_root / "static" / "data" / "impact"
    img_dir = args.repo_root / "static" / "images" / "impact"
    data_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    mentions = load_souilmi_mentions(big, extras)
    papers = aggregate_papers(mentions)
    outlets = aggregate_outlets(mentions)
    languages = aggregate_languages(mentions)
    country_df = pd.read_csv(countries_csv)

    papers.to_csv(data_dir / "papers-engagement.csv", index=False)
    outlets.to_csv(data_dir / "marquee-outlets.csv", index=False)
    languages.to_csv(data_dir / "mentions-by-language.csv", index=False)
    country_df.to_csv(data_dir / "mentions-by-country.csv", index=False)

    total_mentions = int(country_df["Number of posts"].sum())
    total_countries = int((country_df["Number of posts"] > 0).sum())
    total_languages = int((languages["mentions"] > 0).sum())

    plot_geo_linguistic(
        countries_csv,
        languages,
        img_dir / "geographic-linguistic-breadth.svg",
        total_mentions,
        total_countries,
        total_languages,
    )
    plot_engagement(papers, img_dir / "engagement-by-paper.svg")

    print("Built impact summaries and plots:")
    print(f"  Souilmi-attributed mentions: {len(mentions):>5}")
    print(f"  Distinct papers covered:     {len(papers):>5}")
    print(f"  Total news posts (geo):      {total_mentions:>5}")
    print(f"  Countries:                   {total_countries:>5}")
    print(f"  Languages:                   {total_languages:>5}")
    print(f"  Peak Altmetric score:        {int(papers['altmetric_score'].max()):>5}")
    print()
    print("Wrote:")
    for p in sorted([
        data_dir / "papers-engagement.csv", data_dir / "marquee-outlets.csv",
        data_dir / "mentions-by-country.csv", data_dir / "mentions-by-language.csv",
        img_dir / "geographic-linguistic-breadth.svg",
        img_dir / "engagement-by-paper.svg",
    ]):
        print(f"  {p.relative_to(args.repo_root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
