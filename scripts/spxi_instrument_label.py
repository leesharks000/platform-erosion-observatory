#!/usr/bin/env python3
"""spxi_instrument_label.py — label a page as the SPXI instrument it is (2026-10-14).

Reads spxi-instruments.json (a copy of spxi.dev/instruments.json, itself built from spxi.dev/methods.json) and writes
into a page, between markers, three things: a visible line under the page's first heading, a <meta name="spxi:instrument">
and a JSON-LD block naming the method as a DefinedTerm in the SPXI method inventory. Idempotent: an existing block is
replaced, never doubled. The same file is copied into each surface's repository; a builder may import label().

    python3 scripts/spxi_instrument_label.py <page.html> <page-url> [--inventory spxi-instruments.json]
"""
import html, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
BEGIN, END = "<!-- SPXI-INSTRUMENT:BEGIN -->", "<!-- SPXI-INSTRUMENT:END -->"
VBEGIN, VEND = "<!-- SPXI-INSTRUMENT-LINE:BEGIN -->", "<!-- SPXI-INSTRUMENT-LINE:END -->"
_INV = {}


def inventory(path=None):
    p = pathlib.Path(path) if path else next(x for x in (HERE.parent / "spxi-instruments.json", HERE.parent / "data/spxi-instruments.json",
                                                         HERE.parent / "instruments.json") if x.exists())
    if str(p) not in _INV:
        _INV[str(p)] = json.loads(p.read_text(encoding="utf-8"))
    return _INV[str(p)]


def find(page_url, inv):
    best = None
    for ins in inv["instruments"]:
        for s in ins["surfaces"]:
            if page_url.startswith(s["surface"]) and (best is None or len(s["surface"]) > len(best[1]["surface"])):
                best = (ins, s)
    return best


def blocks(page_url, inv):
    hit = find(page_url, inv)
    if not hit:
        return None
    ins, s = hit
    e = html.escape
    also = "".join(f'; also method <a href="{e(a["url"])}">{e(a["method"])}</a>, {e(a["name"])}' for a in s.get("also", []))
    note = f' {e(s["note"])}' if s.get("note") else ""
    line = (f'{VBEGIN}<p class="spxi-instrument" data-spxi-method="{e(ins["method"])}" style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace;'
            f'font-size:.78em;letter-spacing:.02em;margin:.4em 0 1em;padding:.45em .7em;border-left:3px solid #8a5a00;background:rgba(138,90,0,.07)">'
            f'<strong>SPXI instrument</strong> · method <a href="{e(ins["url"])}">{e(ins["method"])}</a> of {inv["itemCount"]}, '
            f'level {ins["level"]} ({e(ins["level_name"])}): {e(ins["name"])}{also}. An instrument of '
            f'<a href="https://www.spxi.dev/">SPXI</a>, the Semantic Packet for eXchange &amp; Indexing; '
            f'the whole practice is itemized at <a href="{e(inv["inventory"])}">spxi.dev/methods</a>.{note}</p>{VEND}')
    ld = {"@context": "https://schema.org", "@type": "DefinedTerm", "@id": ins["url"], "name": ins["name"], "termCode": ins["method"],
          "description": ins["what"],
          "inDefinedTermSet": {"@type": "DefinedTermSet", "@id": inv["inventory"], "name": f'SPXI methods ({inv["itemCount"]}, {inv["levelCount"]} levels)',
                               "url": inv["inventory"]},
          "subjectOf": {"@type": "WebPage", "@id": page_url, "url": page_url},
          "additionalType": "SPXI instrument", "isPartOf": {"@type": "DefinedTerm", "name": f'level {ins["level"]}: {ins["level_name"]}'}}
    head = (f'{BEGIN}\n<meta name="spxi:instrument" content="{e(ins["method"])} {e(ins["name"])} — SPXI method inventory, {e(ins["url"])}">\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n{END}\n')
    return head, line, ins


def label(page, page_url, inv=None):
    inv = inv or inventory()
    b = blocks(page_url, inv)
    page = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", page, flags=re.S)
    page = re.sub(re.escape(VBEGIN) + r".*?" + re.escape(VEND), "", page, flags=re.S)
    if not b:
        return page
    head, line, _ = b
    page = page.replace("</head>", head + "</head>", 1)
    for pat in (r"</h1>", r"<!-- NAV-END -->", r"</nav>", r"<body[^>]*>"):
        m = re.search(pat, page, re.I)
        if m:
            return page[:m.end()] + line + page[m.end():]
    return page
    m = None
    return page[:m.end()] + line + page[m.end():] if m else page


def record(page_url, inv=None):
    """The label as data, for a record's JSON."""
    inv = inv or inventory()
    hit = find(page_url, inv)
    if not hit:
        return None
    ins, s = hit
    return {"method": ins["method"], "name": ins["name"], "level": ins["level"], "level_name": ins["level_name"], "url": ins["url"],
            "inventory": inv["inventory"], "statement": f'SPXI instrument: method {ins["method"]} of {inv["itemCount"]}, level {ins["level"]} ({ins["level_name"]}), {ins["name"]}.',
            "also": s.get("also", [])}


if __name__ == "__main__":
    a = sys.argv[1:]
    inv = inventory(a[a.index("--inventory") + 1]) if "--inventory" in a else inventory()
    p = pathlib.Path(a[0]); url = a[1]
    old = p.read_text(encoding="utf-8")
    new = label(old, url, inv)
    if new != old:
        p.write_text(new, encoding="utf-8")
    print(p, "labelled" if find(url, inv) else "no instrument for this URL", "(unchanged)" if new == old else "")
