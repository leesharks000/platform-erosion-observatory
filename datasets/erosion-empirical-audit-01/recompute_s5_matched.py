#!/usr/bin/env python3
"""EROSION-EMPIRICAL-AUDIT-01 §5 — instrument-matched recomputation (v0.2).

WHY THIS EXISTS
---------------
v0.1 reported a "compression ratio" of 31.2x: an alive-side institutional
fraction of 0.311 against a deletion-side AI-signalled institutional fraction
of 0.00996. The two sides were measured with DIFFERENT INSTRUMENTS:

  alive side    -> Zenodo Search API, institution panel, matched against
                   full record metadata INCLUDING creators[].affiliation
  deletion side -> case-insensitive substring match on `citation_text`

`citation_text` is "Author. (Year). Title. Publisher. DOI". It has no
affiliation field. The deletion side therefore could not measure the construct
the alive side measured, and the ratio between them is dominated by the gap
between the instruments rather than by any difference between the populations.

Measured instrument gap (see verify_instrument_gap below): on the SAME alive
records, the affiliation field yields ~52% institutional and the citation
string yields ~1.2% — a ~41x gap, with the two instruments agreeing on 1
record in 400. Applying the deletion-side instrument to BOTH sides collapses
the reported effect to alive 1.3% vs deleted 1.0%.

WHAT REPLACES IT
----------------
The deletion side is made measurable on the same construct by reconstructing
affiliation from OpenAlex, which ingested the records before deletion and
retains authorships[].institutions and raw_affiliation_strings. Note that
DataCite is NOT a usable reconstruction source: its metadata records are
purged for ~99.8% of deleted records (a finding in its own right — Zenodo
deletion cascades into destruction of the DataCite descriptive record).
OpenAIRE returned 0% coverage. OpenAlex returns 66-77%.

Both sides are then held to the SAME AI classifier (the 23-term panel applied
to a citation string) and the SAME affiliation instrument (OpenAlex).

RESULT (2026-08-27): alive 107/231 = 46.3%; deleted 10/165 = 6.1%;
risk ratio 7.6x, odds ratio 13.4, Fisher exact p = 8.7e-16.
The direction and significance of the v0.1 finding survive. The magnitude
does not: 31.2x was an instrument artifact and is withdrawn.

LIMITATIONS CARRIED FORWARD (do not drop these when citing):
  - OpenAlex coverage differs by side (77% alive / 66% deleted); the
    reconstructable subset is the population, and non-coverage may not be
    random.
  - The alive sampling frame is search-enriched, not a random draw; only the
    CLASSIFIER is matched, not the frame.
  - Affiliation-data density ran 49% alive against 77% deleted in the AI
    subset. This is backwards from expectation and is not yet explained.
  - One depositor accounts for 60.3% of the v0.1 population (100,313 rows).
    That depositor is only ~6% of the AI-signalled deletion sample, so this
    comparison is not driven by the cascade — but any POPULATION-level claim
    from this export must disclose the concentration.
  - The Crimson Hexagonal Archive's own deleted records are inside the
    population (63 rows in the not_ai_and_institutional cell, 25 of them
    under "Sharks, L."). Self-inclusion is small but must be declared.
"""
import csv, gzip, json, random, subprocess, sys
import concurrent.futures as cf
from math import comb, sqrt

AI_SIGNAL_TERMS = [
    'chatgpt', ' claude ', 'gpt-4', 'gpt4', 'gpt ', 'llm ',
    'large language model', 'artificial intelligence', ' ai ', 'ai system',
    'ai review', 'ai evolution', 'ai coauthor', 'gemini', 'grok', 'openai',
    'anthropic', 'ai governance', 'cognitive orchestration',
    'triune superintelligence', 'agentic ai', 'ai-assisted', 'ai assisted',
]
INSTITUTIONAL_TERMS = [
    'university', 'universit', 'universidad', 'institut', ' college ',
    'laboratory', ' cern ', ' nasa', ' cnrs', 'max planck', 'lbnl', 'ornl',
    'inria', 'polytech', 'school of', 'department of',
]

def curl(url, timeout=25):
    return subprocess.run(['curl', '-s', '-m', str(timeout), url],
                          capture_output=True, text=True).stdout

def openalex_affiliation(doi):
    """Reconstructed affiliation text for a DOI, or None if not covered."""
    try:
        d = json.loads(curl(f'https://api.openalex.org/works/doi:{doi}'))
    except Exception:
        return None
    if 'id' not in d:
        return None
    aus = d.get('authorships') or []
    return ' '.join(
        [i.get('display_name', '') for au in aus for i in (au.get('institutions') or [])] +
        [s for au in aus for s in (au.get('raw_affiliation_strings') or [])])

def is_institutional(text):
    return bool(text) and any(t in text.lower() for t in INSTITUTIONAL_TERMS)

def is_ai_signalled(citation_text):
    return any(t in citation_text.lower() for t in AI_SIGNAL_TERMS)

def deletion_side(export_path, n=250, seed=2026):
    """AI-signalled deleted records, affiliation reconstructed via OpenAlex."""
    pool = []
    with gzip.open(export_path, 'rt') as f:
        for r in csv.DictReader(f):
            if not r['removal_date'].startswith('2026') or not r['citation_text']:
                continue
            if is_ai_signalled(r['citation_text']):
                pool.append(r['doi'])
    random.seed(seed)
    sample = random.sample(pool, min(n, len(pool)))
    with cf.ThreadPoolExecutor(10) as ex:
        affs = [a for a in ex.map(openalex_affiliation, sample) if a is not None]
    return sum(1 for a in affs if is_institutional(a)), len(affs), len(pool)

def alive_side(n_pages=4, seed=2026):
    """Alive records that the DELETION-SIDE classifier would call AI-signalled,
    affiliation reconstructed through the SAME OpenAlex instrument."""
    import time, urllib.parse
    queries = ['"assisted by ChatGPT"', '"assisted by Claude"',
               '"generated by ChatGPT"', '"AI-assisted"',
               '"with the assistance of ChatGPT"', '"large language model"',
               '"artificial intelligence"', '"LLM"', '"GPT-4"', '"AI-generated"']
    pool = {}
    for q in queries:
        for p in range(1, n_pages + 1):
            u = (f"https://zenodo.org/api/records?size=25&page={p}"
                 f"&q={urllib.parse.quote(q)}")
            try:
                for h in json.loads(curl(u, 30))['hits']['hits']:
                    md = h.get('metadata', {})
                    if md.get('doi'):
                        pool[md['doi']] = md
            except Exception:
                pass
            time.sleep(0.15)
    matched = []
    for doi, md in pool.items():
        names = '; '.join((c.get('name') or '') for c in (md.get('creators') or []))
        cite = (f"{names}. ({(md.get('publication_date') or '')[:4]}). "
                f"{md.get('title', '')}. Zenodo. https://doi.org/{doi}")
        if is_ai_signalled(cite):
            matched.append(doi)
    with cf.ThreadPoolExecutor(10) as ex:
        affs = [a for a in ex.map(openalex_affiliation, matched) if a is not None]
    return sum(1 for a in affs if is_institutional(a)), len(affs), len(matched)

def verify_instrument_gap(n_pages=16):
    """The defect itself, measured: same alive records, two instruments."""
    import time
    recs = []
    for p in range(1, n_pages + 1):
        try:
            recs += json.loads(curl(
                f'https://zenodo.org/api/records?size=25&page={p}&sort=newest',
                30))['hits']['hits']
        except Exception:
            pass
        time.sleep(0.25)
    by_aff = by_cite = agree = 0
    for r in recs:
        md = r.get('metadata', {}); crs = md.get('creators') or []
        affs = ' '.join((c.get('affiliation') or '') for c in crs)
        names = ' '.join((c.get('name') or '') for c in crs)
        cite = (f"{names}. ({(md.get('publication_date') or '')[:4]}). "
                f"{md.get('title','')}. Zenodo. https://doi.org/{md.get('doi','')}")
        a, c = is_institutional(affs), is_institutional(cite)
        by_aff += a; by_cite += c; agree += (a and c)
    return by_aff, by_cite, agree, len(recs)

def wilson(k, n):
    if not n: return (float('nan'), float('nan'))
    z = 1.96; p = k / n; den = 1 + z*z/n
    ctr = (p + z*z/(2*n)) / den
    hw = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / den
    return 100*(ctr-hw), 100*(ctr+hw)

def fisher(a, b, c, d):
    n = a+b+c+d
    obs = comb(a+b, a) * comb(c+d, c) / comb(n, a+c)
    return sum(comb(a+b, i) * comb(c+d, a+c-i) / comb(n, a+c)
               for i in range(0, min(a+b, a+c)+1)
               if comb(a+b, i) * comb(c+d, a+c-i) / comb(n, a+c) <= obs + 1e-15)

if __name__ == '__main__':
    export = sys.argv[1] if len(sys.argv) > 1 else 'deleted-head-20260710.csv.gz'
    print('== instrument gap (the defect, measured) ==')
    aff, cite, agree, n = verify_instrument_gap()
    print(f'  same {n} alive records: affiliation {aff} ({100*aff/n:.1f}%) '
          f'vs citation-string {cite} ({100*cite/n:.1f}%); both fire on {agree}')
    print('\n== instrument-matched comparison ==')
    di, dn, dpool = deletion_side(export)
    ai, an, apool = alive_side()
    print(f'  DELETED AI-signalled: {di}/{dn} = {100*di/dn:.1f}%  '
          f'CI [{wilson(di,dn)[0]:.1f},{wilson(di,dn)[1]:.1f}]  (pool {dpool})')
    print(f'  ALIVE   AI-signalled: {ai}/{an} = {100*ai/an:.1f}%  '
          f'CI [{wilson(ai,an)[0]:.1f},{wilson(ai,an)[1]:.1f}]  (matched {apool})')
    rr = (ai/an) / (di/dn)
    print(f'\n  risk ratio {rr:.2f}x | Fisher p = {fisher(ai, an-ai, di, dn-di):.3g}')
    print(f'  v0.1 published 31.2x — withdrawn as instrument artifact.')
