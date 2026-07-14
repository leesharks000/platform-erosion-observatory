#!/usr/bin/env python3
"""
generate_audit.py — Reproducibility script for EA-EROSION-EMPIRICAL-01 v0.1.

Executes the traversal specified in §1 of the governing deposit, producing
all numerical findings from the source containers:

  ZENODO-DELETION-EXPORT-20260607 (deleted-20260607.csv.gz)
  ZENODO-DELETION-EXPORT-20260710 (deleted-head-20260710.csv.gz)

plus HTTP access to zenodo.org/api/records and zenodo.org/api/records (Search).

Usage:
    python3 generate_audit.py --data-dir <path-to-zenodo-deletion-ledger>

Requires: python3 (stdlib only); network access to zenodo.org.

Governing citation discipline: EA-NEGSHAPE-01 v0.2 (AXN:0444, deposit #1075).
No citation rendered without confirmed membership (§2.4).
"""
import argparse
import csv
import gzip
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


AI_SIGNAL_TERMS = [
    'chatgpt', ' claude ', 'gpt-4', 'gpt4', 'gpt ', 'llm ', 'large language model',
    'artificial intelligence', ' ai ', 'ai system', 'ai review', 'ai evolution',
    'ai coauthor', 'gemini', 'grok', 'openai', 'anthropic',
    'ai governance', 'cognitive orchestration', 'triune superintelligence',
    'agentic ai', 'ai-assisted', 'ai assisted',
]

INSTITUTIONAL_TERMS = [
    'university', 'universit', 'universidad', 'institut', ' college ', 'laboratory',
    ' cern ', ' nasa', ' cnrs', 'max planck', 'lbnl', 'ornl', 'inria', 'polytech',
    'school of', 'department of',
]


def load_export(path):
    """Load a Zenodo bulk deletion export into {record_id: row}."""
    ids = {}
    with gzip.open(path, 'rt') as f:
        for row in csv.DictReader(f):
            ids[row['record_id']] = row
    return ids


def set_comparison(jun, jul):
    """Return (in_both, in_jun_only, in_jul_only)."""
    in_both = set(jun) & set(jul)
    in_jun_only = set(jun) - set(jul)
    in_jul_only = set(jul) - set(jun)
    return in_both, in_jun_only, in_jul_only


def contingency_2x2(export_jul):
    """Compute 2x2 contingency: AI-signal × institutional-signal within 2026 non-spam deletions."""
    c = Counter()
    for rid, row in export_jul.items():
        if not row['removal_date'].startswith('2026'):
            continue
        if not row['citation_text']:
            continue
        cite = row['citation_text'].lower()
        has_ai = any(t in cite for t in AI_SIGNAL_TERMS)
        has_inst = any(t in cite for t in INSTITUTIONAL_TERMS)
        key = f"{'ai' if has_ai else 'no_ai'}_{'inst' if has_inst else 'no_inst'}"
        c[key] += 1
    return c


def spam_strip_test(export_jul):
    """Categorize citation_text availability by removal_reason for 2026 deletions."""
    by_reason = defaultdict(lambda: {'total': 0, 'with_citation': 0})
    for rid, row in export_jul.items():
        if not row['removal_date'].startswith('2026'):
            continue
        r = row['removal_reason']
        by_reason[r]['total'] += 1
        if row['citation_text']:
            by_reason[r]['with_citation'] += 1
    return dict(by_reason)


def verify_wu_restoration(candidate_ids, delay=0.15):
    """Fetch live Zenodo records to verify restoration status."""
    results = []
    for rid in candidate_ids:
        try:
            req = urllib.request.Request(
                f"https://zenodo.org/api/records/{rid}",
                headers={'User-Agent': 'PEO/audit'},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            md = data.get('metadata', {}) or {}
            creators = md.get('creators') or []
            first = (creators[0] if creators else {}) or {}
            files = data.get('files') or []
            results.append({
                'rec_id': rid,
                'http': 200,
                'status': data.get('status'),
                'revision': data.get('revision'),
                'updated': data.get('updated', '')[:19],
                'creator': first.get('name'),
                'affiliation': first.get('affiliation'),
                'orcid': first.get('orcid'),
                'file_count': len(files),
                'file_size_bytes': sum(f.get('size', 0) for f in files),
                'owner_id': (data.get('owners') or [{}])[0].get('id') if data.get('owners') else None,
            })
        except Exception as e:
            results.append({'rec_id': rid, 'error': str(e)})
        time.sleep(delay)
    return results


def search_alive_side_disclosure(queries, size=25, delay=0.4):
    """Query Zenodo Search API for AI-composition disclosure phrases."""
    results = []
    for q in queries:
        try:
            url = f"https://zenodo.org/api/records?q={urllib.parse.quote(q)}&size={size}"
            req = urllib.request.Request(url, headers={'User-Agent': 'PEO/audit'})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            for h in data.get('hits', {}).get('hits', []):
                md = h.get('metadata', {}) or {}
                creators = md.get('creators') or []
                first = (creators[0] if creators else {}) or {}
                results.append({
                    'query': q,
                    'rec_id': str(h.get('id', '')),
                    'title': (md.get('title') or '')[:200],
                    'creator': first.get('name'),
                    'affiliation': first.get('affiliation'),
                })
            time.sleep(delay)
        except Exception:
            pass
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--data-dir', required=True,
                    help='Directory containing deleted-20260607.csv.gz and deleted-head-20260710.csv.gz')
    ap.add_argument('--skip-live-checks', action='store_true',
                    help='Skip HTTP calls to zenodo.org (offline mode; contingency + spam-strip only)')
    args = ap.parse_args()

    dd = Path(args.data_dir)
    jun_path = dd / 'deleted-20260607.csv.gz'
    jul_path = dd / 'deleted-head-20260710.csv.gz'

    print(f'Loading {jun_path.name}...', file=sys.stderr)
    jun = load_export(jun_path)
    print(f'  {len(jun):,} rows', file=sys.stderr)
    print(f'Loading {jul_path.name}...', file=sys.stderr)
    jul = load_export(jul_path)
    print(f'  {len(jul):,} rows', file=sys.stderr)

    in_both, jun_only, jul_only = set_comparison(jun, jul)
    print(f'\nSet comparison:', file=sys.stderr)
    print(f'  In both: {len(in_both):,}', file=sys.stderr)
    print(f'  Withdrawn (in June only): {len(jun_only):,}', file=sys.stderr)
    print(f'  New deletions (in July only): {len(jul_only):,}', file=sys.stderr)

    contingency = contingency_2x2(jul)
    print(f'\n2x2 contingency:', file=sys.stderr)
    for k, v in contingency.most_common():
        print(f'  {k}: {v:,}', file=sys.stderr)

    spam_strip = spam_strip_test(jul)
    print(f'\nSpam-strip test (2026 deletions):', file=sys.stderr)
    for reason, stats in sorted(spam_strip.items(), key=lambda x: -x[1]['total']):
        total = stats['total']; wc = stats['with_citation']
        pct = 100 * wc / total if total else 0
        print(f'  {reason!r:>25}: {total:>8,} total  ·  {wc:>8,} with citation  ·  {pct:5.1f}%', file=sys.stderr)

    output = {
        'audit_date': '2026-07-14',
        'set_comparison': {
            'in_both': len(in_both),
            'withdrawn_candidates': len(jun_only),
            'new_deletions': len(jul_only),
        },
        'contingency_2x2_2026_nonspam': dict(contingency),
        'spam_strip_test_2026': spam_strip,
    }

    if not args.skip_live_checks:
        print(f'\nVerifying {len(jun_only)} withdrawal candidates via live Zenodo API...', file=sys.stderr)
        candidates = sorted(jun_only, key=int)
        wu_verification = verify_wu_restoration(candidates)
        output['withdrawal_verification'] = wu_verification
        published = sum(1 for r in wu_verification if r.get('status') == 'published')
        print(f'  {published}/{len(wu_verification)} confirmed published', file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
