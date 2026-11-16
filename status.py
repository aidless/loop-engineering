#!/usr/bin/env python3
"""Loop Engineering 0.1.0-dev — registry dashboard.

Prints the papers listed in registry.yaml and both the stored TMLR aggregate
and the medians that can be recomputed from numeric fields. The stored
aggregate is hand-coded. This script does not read the papers.

Usage:
    python status.py --all
    python status.py PAPER-A
"""
import argparse
import statistics
from datetime import datetime
from pathlib import Path

import yaml

LOOP_DIR = Path(__file__).resolve().parent


def version_string():
    return (LOOP_DIR / 'VERSION').read_text(encoding='utf-8').strip()


def _numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def recompute_baselines(baselines):
    """Medians and rates computed from the per-paper fields.

    Dataset and model medians use numeric fields only. Strings such as
    "multiple graph benchmarks" are omitted, not parsed. CI and effect-size
    rates are the share of stored booleans that are true. A statistical-test
    string counts as reported only when it is not "none reported" or
    "not specified". None of these fields were checked against the PDFs.
    """
    rows = baselines['baselines']
    datasets = [row['datasets'] for row in rows if _numeric(row.get('datasets'))]
    models = [row['models'] for row in rows if _numeric(row.get('models'))]
    scores = [row['score_estimated'] for row in rows]
    n = len(rows)
    absent = {'none reported', 'not specified'}
    tests_reported = sum(
        1 for row in rows
        if str(row.get('statistical_tests', '')).strip().lower() not in absent
    )
    return {
        'n_papers': n,
        'n_numeric_datasets': len(datasets),
        'n_numeric_models': len(models),
        'median_datasets_numeric': statistics.median(datasets) if datasets else None,
        'median_models_numeric': statistics.median(models) if models else None,
        'ci_flag_pct': int(100 * sum(row.get('reports_ci') is True for row in rows) / n),
        'effect_size_flag_pct': int(100 * sum(row.get('reports_effect_size') is True for row in rows) / n),
        'median_score': statistics.median(scores),
        'statistical_tests_reported_pct': int(100 * tests_reported / n),
    }

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def phase_bar(phase, total=5):
    filled = int(30 * phase / total)
    return '█' * filled + '░' * (30 - filled)

def status_icon(status):
    icons = {'completed': '✅', 'in_progress': '🔄', 'pending': '⬜', 'blocked': '🚫'}
    return icons.get(status, '❓')

def main():
    parser = argparse.ArgumentParser(
        description='Loop Engineering 0.1.0-dev — registry dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python status.py              # Summary of all papers
  python status.py PAPER-A      # Detailed view of one paper
  python status.py --all        # Same as default (all papers)
        """
    )
    parser.add_argument('paper', nargs='?', help='Paper ID for detailed view (e.g., PAPER-A)')
    parser.add_argument('--all', '-a', action='store_true', help='Show all papers (default)')
    args = parser.parse_args()
    
    registry = load_yaml(LOOP_DIR / 'registry.yaml')
    baselines = load_yaml(LOOP_DIR / 'tmlr_baselines.yaml')
    
    paper_id = args.paper
    show_all = args.all or not paper_id
    
    papers = registry['papers']
    
    print("=" * 65)
    print(f"  Loop Engineering {version_string()} — registry dashboard")
    print("  Registry loop_version values below are stored strings, not this package version.")
    print(f"  🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  📊 {registry['summary']['total_papers']} papers tracked | {registry['summary']['papers_with_loop']} with Loop")
    print("=" * 65)
    
    if paper_id:
        # Single paper detail view
        p = papers.get(paper_id)
        if not p:
            print(f"  ❌ Paper '{paper_id}' not found. Use: PAPER-A, PAPER-B, etc.")
            return
        print(f"\n  📄 {p['title'][:55]}...")
        print(f"  📍 {p['path']}")
        print(f"  🏷️  {p['venue']} | Type: {p['type']}")
        print(f"  📈 Phase: {p['phase']}/5 — {p['phase_name']}")
        print(f"  {'✅' if p['has_loop'] else '⬜'} Loop {'v' + str(p['loop_version']) if p['loop_version'] else 'not initialized'}")
        if p['score_self']:
            print(f"  ⭐ Self-score: {p['score_self']}/10")
        if p['score_tmlr_calibrated']:
            print(f"  📐 TMLR-calibrated: {p['score_tmlr_calibrated']}/10")
        if p.get('notes'):
            print(f"  📝 {p['notes']}")
        return
    
    # All papers summary
    print(f"\n  {'ID':<12} {'Short Title':<25} {'Phase':<8} {'Score':<8} {'Loop':<6}")
    print("  " + "-" * 60)
    
    for key, p in papers.items():
        pid = p['id']
        title = p['short_title'][:23]
        phase_str = f"{status_icon(p.get('phase_name','pending').split()[0] if p['phase']==5 else 'completed' if p['phase']==5 else 'pending')} P{p['phase']}"
        score = f"{p.get('score_self','—')}/10" if p.get('score_self') else "—"
        loop = "v" + str(p['loop_version']) if p.get('loop_version') else "⬜"
        print(f"  {pid:<12} {title:<25} {phase_str:<8} {score:<8} {loop:<6}")
    
    # TMLR baseline reference. The aggregate block is hand-coded. The
    # recomputed line uses only fields that are actually numbers.
    agg = baselines['aggregate']
    rec = recompute_baselines(baselines)
    print(f"\n  TMLR baseline file ({rec['n_papers']} hand-coded rows):")
    print(f"     Recomputed numeric medians: datasets {rec['median_datasets_numeric']} "
          f"(n={rec['n_numeric_datasets']}/{rec['n_papers']}), "
          f"models {rec['median_models_numeric']} "
          f"(n={rec['n_numeric_models']}/{rec['n_papers']})")
    print(f"     Stored aggregate {agg['median_datasets']} datasets / {agg['median_models']} models "
          f"is hand-coded and is not that median.")
    print(f"     CI flag {rec['ci_flag_pct']}% | effect-size flag {rec['effect_size_flag_pct']}% "
          f"(hand-coded booleans, not verified against the papers)")
    print(f"     Median of stored score_estimated: {rec['median_score']}")
    
    # Cross-paper insights
    cross = load_yaml(LOOP_DIR / 'cross_ref.yaml')
    pending = [p for p in cross['propagation_log'] if p['status'] == 'pending_review']
    if pending:
        print(f"\n  🔗 {len(pending)} cross-paper patterns pending propagation")
    
    print("\n" + "=" * 65)
    print("  Commands: status.py --all | status.py PAPER-A | status.py PAPER-B")
    print("=" * 65)

if __name__ == '__main__':
    main()
