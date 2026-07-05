#!/usr/bin/env python3
"""Loop Engineering v4.1 — Automated Pre-Review Scanner
Applies Tier 1 rules from rulebook.yaml to a paper's main.tex

Usage:
    python pre_review.py PAPER_ID              # Run pre-review on a paper
    python pre_review.py PAPER_ID --tier 2     # Run Tier 1+2 checks
    python pre_review.py --help                # Show this help
"""
import yaml
import sys
import re
import argparse
from pathlib import Path

LOOP_DIR = Path(__file__).resolve().parent
AETTL_DIR = LOOP_DIR.parent

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def find_paper(paper_id):
    registry = load_yaml(LOOP_DIR / 'registry.yaml')
    for key, p in registry['papers'].items():
        if p['id'] == paper_id:
            return p
    return None

def read_tex(paper):
    tex_path = AETTL_DIR / paper['path'] / 'main.tex'
    if not tex_path.exists():
        return None
    with open(tex_path, 'r', encoding='utf-8') as f:
        return f.read()

def run_tier1_checks(text, paper_name):
    """Run all Tier 1 (blocking) checks"""
    issues = []
    
    # C1: "First"/"Novel" claims
    first_claims = re.findall(r'(?:first|novel|we are the first to)[^.]*\.', text, re.IGNORECASE)
    if first_claims:
        for claim in first_claims[:3]:
            issues.append({
                'rule': 'C1',
                'severity': 'critical',
                'description': f'"First/Novel" claim detected: "{claim.strip()[:80]}..."',
                'fix': 'Verify no prior work did the same thing. Search literature for each claim.'
            })
    
    # C9: Null effect misinterpretation
    null_phrases = re.findall(r'no statistically significant[^.]*\.|no detectable[^.]*\.|no effect[^.]*\.', text, re.IGNORECASE)
    for phrase in null_phrases[:3]:
        if 'p' in phrase.lower() and '=' in phrase:
            issues.append({
                'rule': 'C9',
                'severity': 'critical',
                'description': f'Null effect phrasing: "{phrase.strip()[:80]}..."',
                'fix': 'Use "insufficient evidence to reject the null" not "no effect exists".'
            })
    
    # C7: Count mismatch
    count_patterns = re.findall(r'(?:^|\s)([Tt]wo|[Tt]hree|[Ff]our|[Ff]ive|[Ss]ix)\s+\w+(?:\s+\w+)?\s*(?:recommendations|guidelines|findings|items|steps)', text)
    if count_patterns:
        issues.append({
            'rule': 'C7',
            'severity': 'minor',
            'description': f'Count claims detected: {count_patterns[:3]}. Verify enumerated items match count.',
            'fix': 'Count the actual items and match the number.'
        })
    
    # C4: Monotonic claims
    monotonic_claims = re.findall(r'monotonically[^.]*\.', text, re.IGNORECASE)
    if monotonic_claims:
        issues.append({
            'rule': 'C4',
            'severity': 'critical',
            'description': f'Monotonic claims: {len(monotonic_claims)} found. Verify per-condition data.',
            'fix': 'Check per-condition data for non-monotonic violations. Use "broadly" or "descriptively" qualifiers.'
        })
    
    # W4: Chinglish scan
    chinglish_patterns = [
        (r'different with', '"different with" → "different from"'),
        (r'\bcompare with\b(?!ed)', '"compare with" → "compared with/to"'),
        (r'\bprove\b(?!n|d|r|s)', '"prove" → "demonstrate/show" (unless mathematical proof)'),
        (r'in the following', '"in the following" → "below" or "in the next section"'),
        (r'most of\s(?!the)', '"most of" → "most" (unless followed by "the")'),
    ]
    for pattern, suggestion in chinglish_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            issues.append({
                'rule': 'W4',
                'severity': 'minor',
                'description': f'Chinglish: "{matches[0]}" → {suggestion}',
                'fix': suggestion
            })
    
    # Abstract density check
    abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1)
        numbers = re.findall(r'\d+\.?\d*', abstract)
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', abstract) if s.strip()]
        max_nums_in_sentence = max(len(re.findall(r'\d+\.?\d*', s)) for s in sentences) if sentences else 0
        if max_nums_in_sentence > 5:
            issues.append({
                'rule': 'ABSTRACT',
                'severity': 'important',
                'description': f'Abstract density: up to {max_nums_in_sentence} numbers in a single sentence ({len(numbers)} total numbers in abstract).',
                'fix': 'Break dense sentences. Narrative over data dump. Maximum ~4 numbers per sentence.'
            })
    
    return issues

def main():
    parser = argparse.ArgumentParser(
        description='Loop Engineering v4.1 — Automated Pre-Review Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pre_review.py PAPER-A           # Run Tier 1 checks
  python pre_review.py PAPER-A --tier 2  # Run Tier 1+2 checks
  python pre_review.py PAPER-B --json    # Output as JSON
        """
    )
    parser.add_argument('paper_id', help='Paper ID (e.g., PAPER-A, PAPER-B)')
    parser.add_argument('--tier', '-t', type=int, default=1, choices=[1, 2, 3], help='Max tier to check (1-3)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    paper_id = args.paper_id
    paper = find_paper(paper_id)
    if not paper:
        print(f"Paper '{paper_id}' not found in registry.")
        return
    
    text = read_tex(paper)
    if not text:
        print(f"main.tex not found at {AETTL_DIR / paper['path'] / 'main.tex'}")
        return
    
    print(f"\n🔍 Pre-Review: {paper['title'][:60]}...")
    print(f"   Paper: {paper_id} | Phase: {paper['phase']}")
    print("=" * 60)
    
    issues = run_tier1_checks(text, paper['short_title'])
    
    if not issues:
        print("\n✅ No Tier 1 issues detected!")
        return
    
    critical = [i for i in issues if i['severity'] == 'critical']
    important = [i for i in issues if i['severity'] == 'important']
    minor = [i for i in issues if i['severity'] == 'minor']
    
    print(f"\n🔴 Critical ({len(critical)}):")
    for i in critical:
        print(f"  [{i['rule']}] {i['description']}")
        print(f"  → Fix: {i['fix']}\n")
    
    print(f"🟡 Important ({len(important)}):")
    for i in important:
        print(f"  [{i['rule']}] {i['description']}")
        print(f"  → Fix: {i['fix']}\n")
    
    print(f"🟢 Minor ({len(minor)}):")
    for i in minor:
        print(f"  [{i['rule']}] {i['description']}")
    
    print(f"\n{'='*60}")
    print(f"Summary: {len(critical)} critical, {len(important)} important, {len(minor)} minor")
    print(f"Estimated review time saved: ~{len(issues) * 5} minutes")

if __name__ == '__main__':
    main()
