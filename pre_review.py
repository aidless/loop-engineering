#!/usr/bin/env python3
"""Loop Engineering 0.1.0-dev — hard-coded pre-review scan.

Runs six regular expressions on a LaTeX file (C1, C4, C9, C7, W4, abstract
number density). Does not load rulebook.yaml. Does not implement Tier-1 rules
L1, C6, M1, or M3. Tier 2 and Tier 3 are not implemented.

Usage:
    python pre_review.py --tex path/to/main.tex --json
    python pre_review.py PAPER_ID
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

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
        description='Loop Engineering 0.1.0-dev — hard-coded pre-review scan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pre_review.py --tex fixtures/pre_review/trigger.tex --json
  python pre_review.py PAPER-A
        """
    )
    parser.add_argument('paper_id', nargs='?', help='Paper ID (e.g., PAPER-A). Not used with --tex.')
    parser.add_argument('--tex', help='Scan this .tex file instead of a registry paper')
    parser.add_argument('--tier', '-t', type=int, default=1, choices=[1, 2, 3],
                        help='Only 1 is implemented. 2 and 3 exit 2.')
    parser.add_argument('--json', '-j', action='store_true', help='Print the issue list as JSON')
    args = parser.parse_args()

    if args.tier != 1:
        print(
            "Tier 2 and Tier 3 are not implemented. This command only runs the hard-coded checks.",
            file=sys.stderr,
        )
        return 2

    if args.tex:
        tex_path = Path(args.tex)
        if not tex_path.is_file():
            print(f"tex file not found: {tex_path}", file=sys.stderr)
            return 1
        text = tex_path.read_text(encoding='utf-8')
        paper_id = tex_path.stem
        paper = {'title': paper_id, 'phase': 'fixture', 'short_title': paper_id}
    else:
        if not args.paper_id:
            print("Provide a paper id or --tex PATH.", file=sys.stderr)
            return 2
        paper_id = args.paper_id
        paper = find_paper(paper_id)
        if not paper:
            print(f"Paper '{paper_id}' not found in registry.")
            return 1
        text = read_tex(paper)
        if not text:
            print(f"main.tex not found at {AETTL_DIR / paper['path'] / 'main.tex'}")
            return 1

    issues = run_tier1_checks(text, paper.get('short_title', paper_id))
    if args.json:
        json.dump(issues, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        return 0

    print(f"\n🔍 Pre-Review: {paper['title'][:60]}...")
    print(f"   Paper: {paper_id} | Phase: {paper['phase']}")
    print("=" * 60)
    
    if not issues:
        print("\nNo hard-coded pattern hits.")
        return 0
    
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
    return 0

if __name__ == '__main__':
    sys.exit(main())
