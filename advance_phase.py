#!/usr/bin/env python3
"""Loop Engineering v4.1 — Phase Advancement Tool
Validates preconditions before advancing paper to next phase.

Usage:
    python advance_phase.py PAPER_ID           # Advance with precondition checks
    python advance_phase.py PAPER_ID --force   # Skip precondition checks
    python advance_phase.py PAPER_ID --dry-run # Show what's missing without advancing
    python advance_phase.py --help             # Show this help
"""
import yaml
import sys
import argparse
from pathlib import Path
from datetime import datetime

LOOP_DIR = Path(__file__).resolve().parent
AETTL_DIR = LOOP_DIR.parent

# Phase advancement preconditions
PRECONDITIONS = {
    0: [],  # Phase 0 → 1: no preconditions (baseline assessment is self-contained)
    1: [    # Phase 1 → 2: format conversion complete
        ('Compilation', 'Verify tmlr_submit/main.log has 0 Errors', 
         lambda paper_dir: _check_log(paper_dir / 'tmlr_submit' / 'main.log')),
    ],
    2: [    # Phase 2 → 3: content review complete
        ('Critical Issues', 'All critical issues resolved or documented',
         lambda paper_dir: _check_critical_issues(paper_dir)),
    ],
    3: [    # Phase 3 → 4: polish complete
        ('Abstract Check', 'Abstract is standalone-readable',
         lambda paper_dir: True),  # Manual check — always passes auto
    ],
    4: [    # Phase 4 → 5: anonymization complete
        ('Anonymization', 'Zero identity leaks in grep verification',
         lambda paper_dir: _check_anonymization(paper_dir)),
    ],
    5: [    # Phase 5: final sign-off
        ('User Sign-off', 'User has manually confirmed readiness',
         lambda paper_dir: False),  # Always requires --force or manual confirmation
    ],
}

def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def _check_log(log_path):
    if not log_path.exists():
        return False, "main.log not found"
    content = log_path.read_text(encoding='utf-8', errors='ignore')
    errors = content.count('Error:')
    if errors > 0:
        return False, f"{errors} errors in log"
    return True, "0 errors"

def _check_critical_issues(paper_dir):
    issue_path = paper_dir / '.loop' / 'issue_tracker.yaml'
    if not issue_path.exists():
        return False, "issue_tracker.yaml not found"
    issues = load_yaml(issue_path)
    open_critical = [i for i in issues.get('issues', {}).values() 
                     if i.get('severity') == 'critical' and i.get('status') == 'open']
    if open_critical:
        ids = ', '.join(i['id'] for i in open_critical)
        return False, f"{len(open_critical)} open critical issues: {ids}"
    return True, "0 open critical issues"

def _check_anonymization(paper_dir):
    patterns = ['zewen', 'qilu', 'lzw7071', 'jinan']
    tex_dir = paper_dir / 'tmlr_submit'
    if not tex_dir.exists():
        tex_dir = paper_dir
    found = []
    for pattern in patterns:
        for ext in ['*.tex', '*.bib', '*.bbl']:
            import glob
            for f in glob.glob(str(tex_dir / '**' / ext), recursive=True):
                content = Path(f).read_text(encoding='utf-8', errors='ignore').lower()
                if pattern in content:
                    found.append(f"{pattern} in {Path(f).name}")
    if found:
        return False, f"Identity leaks: {', '.join(found[:3])}"
    return True, "0 identity leaks"

def find_paper(paper_id):
    registry = load_yaml(LOOP_DIR / 'registry.yaml')
    for key, p in registry['papers'].items():
        if p['id'] == paper_id:
            return p
    return None

def main():
    parser = argparse.ArgumentParser(
        description='Loop Engineering v4.1 — Phase Advancement Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advance_phase.py PAPER-A              # Advance with precondition checks
  python advance_phase.py PAPER-A --force      # Skip precondition checks
  python advance_phase.py PAPER-A --dry-run    # Show what's missing
        """
    )
    parser.add_argument('paper_id', help='Paper ID (e.g., PAPER-A, PAPER-B)')
    parser.add_argument('--force', '-f', action='store_true', help='Skip precondition checks')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Check preconditions without advancing')
    args = parser.parse_args()
    
    paper_id = args.paper_id
    force = args.force
    dry_run = args.dry_run
    
    paper = find_paper(paper_id)
    if not paper:
        print(f"❌ Paper '{paper_id}' not found.")
        sys.exit(1)
    
    paper_dir = AETTL_DIR / paper['path']
    state_path = paper_dir / '.loop' / 'state.yaml'
    
    if not state_path.exists():
        print(f"❌ No .loop/state.yaml found. Initialize paper first: python init_paper.py")
        sys.exit(1)
    
    state = load_yaml(state_path)
    current = state['current_phase']
    
    if current >= 5:
        print(f"✅ Paper is already at Phase 5 (submission ready). No further phases.")
        return
    
    next_phase = current + 1
    preconditions = PRECONDITIONS.get(current, [])
    
    print(f"\n📈 Advancing {paper_id}: Phase {current} → Phase {next_phase}")
    print(f"   Paper: {paper['short_title']}")
    
    if current == 5:
        print(f"\n🔴 Phase 5 → Complete requires USER SIGN-OFF.")
        if not force:
            print("   Use --force only after manually reviewing the final PDF.")
            sys.exit(1)
    
    # Check preconditions
    all_pass = True
    if preconditions:
        print(f"\n   Checking preconditions:")
        for name, desc, check_fn in preconditions:
            passed, detail = check_fn(paper_dir)
            icon = '✅' if passed else '❌'
            print(f"   {icon} {name}: {detail}")
            if not passed:
                all_pass = False
    
    if not all_pass and not force and not dry_run:
        print(f"\n❌ Preconditions not met. Fix issues, use --force, or use --dry-run to inspect.")
        sys.exit(1)
    
    if dry_run:
        if all_pass:
            print(f"\n✅ All preconditions met — ready to advance to Phase {next_phase}!")
            print(f"   Run without --dry-run to advance.")
        else:
            print(f"\n📋 Preconditions NOT met. Missing items:")
            for name, desc, check_fn in preconditions:
                passed, detail = check_fn(paper_dir)
                if not passed:
                    print(f"   ❌ {name}: {detail}")
            print(f"\n   Fix these before advancing, or use --force.")
        return
    
    if force and not all_pass:
        print(f"\n⚠️  Forcing advancement despite failed preconditions.")
    
    # Backup old state
    backup_path = state_path.with_suffix('.yaml.bak')
    save_yaml(backup_path, state)
    
    # Advance phase
    state['current_phase'] = next_phase
    state['updated'] = datetime.now().strftime('%Y-%m-%d')
    state['phases'][f'phase_{current}']['status'] = 'completed'
    state['phases'][f'phase_{current}']['completed'] = datetime.now().strftime('%Y-%m-%d')
    state['phases'][f'phase_{next_phase}']['status'] = 'in_progress'
    state['phases'][f'phase_{next_phase}']['started'] = datetime.now().strftime('%Y-%m-%d')
    
    state['session_history'].append({
        'date': datetime.now().strftime('%Y-%m-%d'),
        'action': f'phase_{current}_completed',
        'note': f'Advanced from Phase {current} to Phase {next_phase}. {"Forced." if force and not all_pass else "All preconditions met."}'
    })
    
    save_yaml(state_path, state)
    
    # Update registry
    registry = load_yaml(LOOP_DIR / 'registry.yaml')
    for key, p in registry['papers'].items():
        if p['id'] == paper_id:
            p['phase'] = next_phase
            phase_names = ['基线评估', '格式转换', '内容审阅', '润色', '匿名化', '提交就绪']
            p['phase_name'] = phase_names[next_phase] if next_phase < len(phase_names) else '完成'
    save_yaml(LOOP_DIR / 'registry.yaml', registry)
    
    print(f"\n{'='*50}")
    print(f"✅ Advanced to Phase {next_phase}!")
    print(f"   Backup saved: {backup_path.name}")
    print(f"   Next: python ../.loop/pre_review.py {paper_id}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
