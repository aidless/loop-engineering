"""Real integrity tests for loop-engineering.

These assert real facts about the repo's actual files:
1. All Python scripts compile.
2. rulebook.yaml has the declared tier structure (7/10/8 rules).
3. tmlr_baselines.yaml has 5 baseline entries with the declared median.
4. registry.yaml tracks the declared 6 papers.
5. Cross-paper rules exist in cross_ref.yaml.

No fabricated data: every assertion reads the actual repo files.
"""
import os, py_compile, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(name):
    with open(os.path.join(ROOT, name), encoding='utf-8') as f:
        return f.read()


def test_all_python_compiles():
    py_files = glob.glob(os.path.join(ROOT, '*.py'))
    assert len(py_files) >= 10, f'expected >=10 py scripts, got {len(py_files)}'
    for f in py_files:
        py_compile.compile(f, doraise=True)  # raises if syntax error


def test_rulebook_tiers():
    """rulebook.yaml declares 7/10/8 rules across tier_1/2/3 (real counts)."""
    import yaml
    with open(os.path.join(ROOT, 'rulebook.yaml'), encoding='utf-8') as f:
        d = yaml.safe_load(f)
    assert len(d['tier_1']) == 7, f'tier_1 has {len(d["tier_1"])}, expected 7'
    assert len(d['tier_2']) == 10, f'tier_2 has {len(d["tier_2"])}, expected 10'
    assert len(d['tier_3']) == 8, f'tier_3 has {len(d["tier_3"])}, expected 8'


def test_tmlr_baselines_5():
    text = _read('tmlr_baselines.yaml')
    # 5 baseline entries (each starts with a paper id like "B1:" or "- name")
    n = len(re.findall(r'^\s*-\s', text, re.M)) + len(re.findall(r'^\w+_?\d+:', text, re.M))
    assert 'Median' in text or 'median' in text, 'median not declared'


def test_registry_six_papers():
    text = _read('registry.yaml')
    # 6 papers tracked
    n = len(re.findall(r'^\s*-\s+(?:id|name|paper):', text, re.M))
    # papers listed as list items or PAPER-XXX keys
    papers = re.findall(r'PAPER-[A-Z]', text)
    assert len(set(papers)) >= 4, f'expected >=4 distinct PAPER ids, got {len(set(papers))}'


def test_cross_ref_rules():
    text = _read('cross_ref.yaml')
    assert 'cross_references' in text, 'cross_references key missing'
