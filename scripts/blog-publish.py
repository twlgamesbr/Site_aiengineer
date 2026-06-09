#!/usr/bin/env python3
"""
blog-publish.py — Auto-generate blog posts with charts from Unsloth_Core results.

Usage:
  python scripts/blog-publish.py --npc chef_assistant
  python scripts/blog-publish.py --npc chef_assistant,history_guide
  python scripts/blog-publish.py --all
  python scripts/blog-publish.py --npc chef_assistant --train-dir </absolute/path>
  python scripts/blog-publish.py --npc chef_assistant --rebuild
  python scripts/blog-publish.py --all --summary --rebuild
"""

import argparse
import json
import os
import re
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── paths ──────────────────────────────────────────────────────────────
UNSLOTH_CORE_DIR = Path(os.environ.get("UNSLOTH_CORE_DIR", "~/Projects/Unsloth_Core")).expanduser()
SITE_DIR = Path(os.environ.get("SITE_DIR", "~/Projects/Site_aiengineer")).expanduser()

CHARTS_DIR = SITE_DIR / "public" / "charts"
CONTENT_DIR = SITE_DIR / "content" / "blog"

# ensure dirs exist
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
CONTENT_DIR.mkdir(parents=True, exist_ok=True)

CHART_BASE_URL = "/charts"  # served from public/


# ── helpers ────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    text = text.lower().strip().replace(" ", "-")
    return re.sub(r"[^a-z0-9_-]", "", text)


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def short_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


# ── data loaders ───────────────────────────────────────────────────────
def load_feedback(npc: str) -> Optional[dict]:
    """Load the latest feedback JSON for an NPC."""
    path = UNSLOTH_CORE_DIR / "artifacts" / "eval" / "results" / "feedback" / f"{npc}.json"
    if not path.exists():
        print(f"  ⚠ No feedback JSON at {path}")
        return None
    with open(path) as f:
        return json.load(f)


def load_latest_eval_index(npc: str) -> Optional[dict]:
    """Find and load the latest eval report index for an NPC."""
    reports_dir = UNSLOTH_CORE_DIR / "artifacts" / "eval" / "reports" / npc
    if not reports_dir.exists():
        print(f"  ⚠ No eval reports dir at {reports_dir}")
        return None
    index_files = sorted(reports_dir.glob("*.index.json"))
    if not index_files:
        print(f"  ⚠ No .index.json files in {reports_dir}")
        return None
    latest = index_files[-1]
    with open(latest) as f:
        return json.load(f)


def load_training_log(npc: str, train_dir: Optional[str] = None) -> Optional[list]:
    """Load training loss data -- looks for trainer_state.json or logs."""
    if train_dir:
        base = Path(train_dir)
    else:
        runs_dir = UNSLOTH_CORE_DIR / "artifacts" / "models" / npc / "runs"
        if not runs_dir.exists():
            return None
        run_dirs = sorted(runs_dir.iterdir())
        if not run_dirs:
            return None
        base = run_dirs[-1]  # latest run

    # trainer_state.json
    ts_path = base / "trainer_state.json"
    if ts_path.exists():
        with open(ts_path) as f:
            data = json.load(f)
        # extract loss per step
        steps = []
        for log in data.get("log_history", []):
            if "loss" in log:
                steps.append({"step": log["step"], "loss": log["loss"]})
            elif "eval_loss" in log:
                steps.append({"step": log["step"], "eval_loss": log["eval_loss"]})
        return steps if steps else None

    # fallback: training_loss.jsonl
    loss_file = base / "training_loss.jsonl"
    if loss_file.exists():
        steps = []
        with open(loss_file) as f:
            for line in f:
                entry = json.loads(line)
                steps.append(entry)
        return steps if steps else None

    return None


# ── chart generation ───────────────────────────────────────────────────
def make_win_rate_chart(npc: str, feedback: dict, slug: str) -> Optional[str]:
    """Bar chart: candidate win rate vs baseline."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  ⚠ matplotlib not installed; skipping charts")
        return None

    baseline_wins = feedback.get("baseline_wins", 0)
    candidate_wins = feedback.get("candidate_wins", 0)
    ties = feedback.get("ties", 0)
    total = feedback.get("total_examples", baseline_wins + candidate_wins + ties)

    if total == 0:
        return None

    fig, ax = plt.subplots(figsize=(6, 3.5))
    categories = ["Candidate", "Baseline", "Ties"]
    values = [
        candidate_wins / total * 100,
        baseline_wins / total * 100,
        ties / total * 100,
    ]
    colors = ["#7c5cfc", "#6b7280", "#374151"]

    bars = ax.bar(categories, values, color=colors, width=0.5, edgecolor="none")
    ax.set_ylabel("Win Rate (%)")
    ax.set_title(f"{npc.replace('_', ' ').title()} — Win Rate", fontsize=13, fontweight="bold")
    ax.set_ylim(0, 100)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{val:.0f}%",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#e8e8ed",
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#1f1f23")
    ax.spines["bottom"].set_color("#1f1f23")
    ax.tick_params(colors="#6b7280")
    ax.set_facecolor("#0a0a0b")
    fig.patch.set_facecolor("#0a0a0b")

    out_path = CHARTS_DIR / f"{slug}-winrate.png"
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0a0a0b")
    plt.close(fig)
    print(f"  ✓ Chart saved: {out_path}")
    return f"{CHART_BASE_URL}/{slug}-winrate.png"


def make_quality_chart(npc: str, feedback: dict, slug: str) -> Optional[str]:
    """Bar chart: candidate vs baseline quality per concept."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    per_concept = feedback.get("per_concept", {})
    if not per_concept:
        return None

    concepts = sorted(per_concept.keys(), key=lambda k: per_concept[k].get("win_rate", 0))
    # shorten concept labels
    short_labels = [c.split("/")[-1][:18] for c in concepts]
    cand_qual = [per_concept[c].get("avg_candidate_quality", 0) for c in concepts]
    base_qual = [per_concept[c].get("avg_baseline_quality", 0) for c in concepts]

    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(concepts))
    w = 0.35

    ax.bar(x - w / 2, base_qual, w, label="Baseline", color="#6b7280")
    ax.bar(x + w / 2, cand_qual, w, label="Candidate", color="#7c5cfc")

    ax.set_ylabel("Avg Quality Score")
    ax.set_title(f"{npc.replace('_', ' ').title()} — Quality by Concept", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=30, ha="right", fontsize=8)
    ax.legend(frameon=False, labelcolor="#e8e8ed")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#1f1f23")
    ax.spines["bottom"].set_color("#1f1f23")
    ax.tick_params(colors="#6b7280")
    ax.set_facecolor("#0a0a0b")
    fig.patch.set_facecolor("#0a0a0b")

    out_path = CHARTS_DIR / f"{slug}-quality.png"
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0a0a0b")
    plt.close(fig)
    print(f"  ✓ Chart saved: {out_path}")
    return f"{CHART_BASE_URL}/{slug}-quality.png"


def make_loss_chart(npc: str, steps: list, slug: str) -> Optional[str]:
    """Line chart: training loss over steps."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    if not steps:
        return None

    fig, ax = plt.subplots(figsize=(6, 3))
    step_nums = [s["step"] for s in steps]
    losses = [s.get("loss") or s.get("eval_loss") for s in steps]

    ax.plot(step_nums, losses, color="#7c5cfc", linewidth=1.5)
    ax.fill_between(step_nums, losses, alpha=0.1, color="#7c5cfc")

    ax.set_xlabel("Step", color="#6b7280")
    ax.set_ylabel("Loss", color="#6b7280")
    ax.set_title(f"Training Loss — {npc.replace('_', ' ').title()}", fontsize=12, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#1f1f23")
    ax.spines["bottom"].set_color("#1f1f23")
    ax.tick_params(colors="#6b7280")
    ax.set_facecolor("#0a0a0b")
    fig.patch.set_facecolor("#0a0a0b")

    out_path = CHARTS_DIR / f"{slug}-loss.png"
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0a0a0b")
    plt.close(fig)
    print(f"  ✓ Chart saved: {out_path}")
    return f"{CHART_BASE_URL}/{slug}-loss.png"


# ── blog post content builder ──────────────────────────────────────────
def build_post(
    npc: str,
    feedback: dict,
    eval_index: Optional[dict],
    train_steps: Optional[list],
    chart_urls: dict,
) -> str:
    """Build the full markdown blog post from data."""
    date = today_str()
    npc_title = npc.replace("_", " ").title()
    win_rate = feedback.get("win_rate", 0)
    total = feedback.get("total_examples", 0)
    cand_wins = feedback.get("candidate_wins", 0)
    base_wins = feedback.get("baseline_wins", 0)

    per_concept = feedback.get("per_concept", {})
    weak = sorted(
        [(k, v) for k, v in per_concept.items() if v.get("win_rate", 1) < 1.0 and v.get("total", 0) > 0],
        key=lambda x: x[1].get("win_rate", 1),
    )

    tags = ["llm-training", npc, "evaluation"]

    # build markdown
    md = f"""---
title: "{npc_title} — Training Update {date}"
date: {date}
excerpt: "Win rate: {win_rate*100:.0f}% ({cand_wins}/{total}). Per-concept breakdown, quality metrics, and density analysis."
tags: [{', '.join(tags)}]
---

## Overview

Latest evaluation results for **{npc_title}**.

- **Total examples evaluated:** {total}
- **Candidate wins:** {cand_wins} ({win_rate*100:.0f}%)
- **Baseline wins:** {base_wins} ({f"{base_wins/total*100:.0f}%" if total else "0%"})
- **Win rate:** {win_rate*100:.1f}%

"""

    # charts
    if chart_urls.get("winrate"):
        md += f'![Win Rate]({chart_urls["winrate"]})\n\n'
    if chart_urls.get("quality"):
        md += f'![Quality by Concept]({chart_urls["quality"]})\n\n'

    # per-concept breakdown
    if per_concept:
        md += "### Per-Concept Breakdown\n\n"
        md += "| Concept | Total | Candidate Wins | Win Rate | Cand. Quality | Base. Quality |\n"
        md += "|---------|-------|---------------|----------|--------------|--------------|\n"
        for concept, data in sorted(per_concept.items()):
            label = concept.split("/")[-1].replace("_", " ").title()
            cw = data.get("candidate_wins", 0)
            t = data.get("total", 0)
            wr = data.get("win_rate", 0)
            cq = data.get("avg_candidate_quality", 0)
            bq = data.get("avg_baseline_quality", 0)
            md += f"| {label} | {t} | {cw} | {wr*100:.0f}% | {cq:.1f} | {bq:.1f} |\n"
        md += "\n"

    # weak concepts
    if weak:
        md += "### Areas for Improvement\n\n"
        md += "The following concepts showed lower win rates:\n\n"
        for concept, data in weak[:5]:
            label = concept.split("/")[-1].replace("_", " ").title()
            md += f"- **{label}**: {data['win_rate']*100:.0f}% win rate "
            md += f"({data['candidate_wins']}/{data['total']} examples)\n"
        md += "\n"

    # density metrics
    avg_cand_words = feedback.get("avg_candidate_words")
    avg_base_words = feedback.get("avg_baseline_words")
    avg_cand_sent = feedback.get("avg_candidate_sentences")
    if avg_cand_words:
        avg_cand_sent_rounded = round(avg_cand_sent, 1) if avg_cand_sent else "?"
        md += "### Response Density\n\n"
        md += f"- **Candidate avg length:** {avg_cand_words:.0f} words / {avg_cand_sent_rounded} sentences\n"
        md += f"- **Baseline avg length:** {avg_base_words:.0f} words\n\n"

    # training loss chart
    if chart_urls.get("loss"):
        md += f"### Training Progress\n\n"
        md += f"![Loss Curve]({chart_urls['loss']})\n\n"

    # eval parameters
    if eval_index:
        params = eval_index.get("parameters", {})
        model = eval_index.get("model", {})
        md += "### Evaluation Configuration\n\n"
        md += "| Parameter | Value |\n"
        md += "|-----------|-------|\n"
        md += f"| Judge model | {model.get('judge_model', '-')} |\n"
        md += f"| Candidate format | {model.get('candidate_format', '-')} |\n"
        md += f"| Lora weight | {params.get('lora_weight', '-')} |\n"
        md += f"| Max tokens | {params.get('max_tokens', '-')} |\n"
        md += f"| Questions | {params.get('num_questions', '-')} |\n"
        md += "\n"

    md += "---\n"
    md += f"*Auto-generated from Unsloth_Core eval artifacts on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*\n"

    return md


def build_summary_post(npcs_data: list) -> tuple[str, str]:
    """Build a summary post covering multiple NPCs."""
    date = today_str()
    slug = f"training-roundup-{short_ts()}"

    md = f"""---
title: "Training Roundup — {date}"
date: {date}
excerpt: "Weekly summary of LLM training progress across all active NPCs."
tags: [llm-training, roundup, evaluation]
---

## Training Roundup — {date}

Quick summary of this week's training and evaluation results across all active NPCs.

"""

    for entry in npcs_data:
        npc = entry["npc"]
        feedback = entry["feedback"]
        win_rate = feedback.get("win_rate", 0)
        cand_wins = feedback.get("candidate_wins", 0)
        total = feedback.get("total_examples", 0)
        npc_title = npc.replace("_", " ").title()

        md += f"### {npc_title}\n\n"
        md += f"- **Win rate:** {win_rate*100:.1f}% ({cand_wins}/{total})\n"
        md += f"- **Avg response length:** {feedback.get('avg_candidate_words', 'N/A'):.0f} words\n"

        if entry.get("chart_urls", {}).get("winrate"):
            md += f"  ![Win Rate]({entry['chart_urls']['winrate']})\n"

        per_concept = feedback.get("per_concept", {})
        if per_concept:
            low = sorted(
                [(k, v) for k, v in per_concept.items() if v.get("win_rate", 1) < 0.7],
                key=lambda x: x[1].get("win_rate", 1),
            )
            if low:
                md += "- **Needs work:** "
                md += ", ".join([c.split("/")[-1].replace("_", " ").title() for c, _ in low[:3]])
                md += "\n"

        md += "\n"

    md += "---\n"
    md += f"*Auto-generated roundup — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*\n"

    return slug, md


# ── write post ─────────────────────────────────────────────────────────
def write_post(slug: str, content: str) -> Path:
    path = CONTENT_DIR / f"{slug}.md"
    with open(path, "w") as f:
        f.write(content)
    print(f"\n  ✓ Post written: {path}")
    return path


def rebuild_site():
    """Run npm run build in the site directory."""
    print("\n  Rebuilding site...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(SITE_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 0:
        print("  ✓ Site build successful")
    else:
        print(f"  ✗ Build failed:\n{result.stderr[:500]}")

    # optionally deploy
    deploy = input("  Deploy to Vercel? (y/N): ").strip().lower()
    if deploy == "y":
        result = subprocess.run(
            ["npx", "vercel", "deploy", "--prod"],
            cwd=str(SITE_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"  ✓ Deployed:\n{result.stdout}")
        else:
            print(f"  ✗ Deploy failed:\n{result.stderr[:500]}")


# ── main ───────────────────────────────────────────────────────────────
def process_npc(npc: str, train_dir: Optional[str] = None) -> Optional[dict]:
    """Process a single NPC: load data, generate charts, write post."""
    print(f"\n{'='*50}")
    print(f"  Processing: {npc}")
    print(f"{'='*50}")

    feedback = load_feedback(npc)
    if not feedback:
        return None

    eval_index = load_latest_eval_index(npc)
    train_steps = load_training_log(npc, train_dir)

    # create a slug
    slug = f"{npc}-update-{short_ts()}"
    chart_urls = {}

    # generate charts
    wr_chart = make_win_rate_chart(npc, feedback, slug)
    if wr_chart:
        chart_urls["winrate"] = wr_chart

    q_chart = make_quality_chart(npc, feedback, slug)
    if q_chart:
        chart_urls["quality"] = q_chart

    l_chart = None
    if train_steps:
        l_chart = make_loss_chart(npc, train_steps, slug)
        if l_chart:
            chart_urls["loss"] = l_chart

    # build and write post
    content = build_post(npc, feedback, eval_index, train_steps, chart_urls)
    write_post(slug, content)

    return {
        "npc": npc,
        "slug": slug,
        "feedback": feedback,
        "chart_urls": chart_urls,
    }


def main():
    parser = argparse.ArgumentParser(description="Publish blog post from Unsloth_Core results")
    parser.add_argument("--npc", help="NPC key(s) comma-separated, e.g. chef_assistant,history_guide")
    parser.add_argument("--all", action="store_true", help="Process all NPCs with feedback data")
    parser.add_argument("--summary", action="store_true", help="Generate a roundup post covering all NPCs")
    parser.add_argument("--train-dir", help="Path to training run directory (for loss curves)")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild the site after writing posts")
    parser.add_argument("--deploy", action="store_true", help="Deploy to Vercel after rebuild")
    args = parser.parse_args()

    if not args.npc and not args.all:
        parser.print_help()
        print("\nProvide --npc <key> or --all")
        sys.exit(1)

    # discover NPCs
    if args.all:
        feedback_dir = UNSLOTH_CORE_DIR / "artifacts" / "eval" / "results" / "feedback"
        npcs = sorted(set(f.stem.split("_density")[0].split("_large")[0] for f in feedback_dir.glob("*.json")))
    else:
        npcs = [n.strip() for n in args.npc.split(",")]

    processed = []
    for npc in npcs:
        result = process_npc(npc, args.train_dir)
        if result:
            processed.append(result)

    if not processed:
        print("\n  ✗ No NPCs processed successfully.")
        sys.exit(1)

    # summary post
    if args.summary and len(processed) > 1:
        print(f"\n{'='*50}")
        print("  Generating summary post...")
        slug, content = build_summary_post(processed)
        write_post(slug, content)

    # rebuild
    if args.rebuild:
        print(f"\n{'='*50}")
        rebuild_site()
        if args.deploy:
            result = subprocess.run(
                ["npx", "vercel", "deploy", "--prod"],
                cwd=str(SITE_DIR),
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "vercel.app" in line:
                        print(f"  ✓ Deployed: {line.strip()}")
            else:
                print(f"  ✗ Deploy failed:\n{result.stderr[:500]}")

    print(f"\n  ✅ Done. {len(processed)} post(s) published.")


if __name__ == "__main__":
    main()
