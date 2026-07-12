# Zenodo Deletion Ledger — CHA Cohort Extraction (v2, corrected)
Retrieved 2026-07-11 from https://zenodo.org/api/exporter (records-deleted.csv.gz).

**Source snapshots (Zenodo's monthly dumps; only latest 3 retained by Zenodo):**
- HEAD: created 2026-07-10T03:32:35Z, version_id c7571d4c-28ef-46ff-b0f0-235abaac58bf, md5 33877aba1fb5684f86758cb86ddc1ad4 → `deleted-head-20260710.csv.gz` (1,322,017 rows)
- PRIOR: created 2026-06-07T04:02:07Z, version_id ab4e273f-40a2-49e6-84f6-87dc66af87c7, md5 104e2f5c2603dc56217ece0d5519bff8 → `deleted-20260607.csv.gz` (1,309,361 rows)

**Schema:** record_id, doi, parent_id, parent_doi, removal_note, removal_reason, removal_date, citation_text.

## CHA cohort (`cha-kill-ledger-20260619.csv`)
1,136 record rows (strict author/entity pattern; one ornithology false positive excluded); 1,126 dated 2026-06-19; 10 earlier. DOIs touched: 1,136 record + 891 concept ≈ 2,027 union. Margin caveat: initials-style surname collisions possible among June-19 rows; site-wide June-19 blocked+out-of-scope total ≈ 1,198 including at least one other terminated account.

## Pre-2026-06-19 deletions: ALL uploader-initiated (MANUS classification, 2026-07-11)
Zero staff deletions against the archive precede 2026-06-19. An earlier draft of this file characterized these rows as a pre-termination drip; that was an attribution error — the ledger records deletions, not deleters. The ten rows:
- 2026-05-16 (personal-data, rec 20241326): uploader removal of a machine reconstruction that failed its brief (impoverished compression); reason category imprecise for the actual judgment.
- 2026-06-02 (retracted, rec 20453143): uploader removal from Zenodo only; the text remains published at its origin blog. Relocation under caution, not retraction of claims.
- 2026-06-10 (duplicate ×6, canon provenance nodes): session-lag near-duplicates; the stronger witness retained in each pair.
- 2026-06-14 (duplicate, rec 20675216, GW.TACHYON.zenodo v9): stray tether deposit created outside the version chain; incorporated, then removed.
- 2026-06-15 (duplicate, rec 20628554, Mrozony anchor): correction of misattributed heteronymic provenance (a heteronym belonging to another living author had been treated as the archive's own); superseded by a corrected deposit. Deletion-as-correction, with replacement.

## 2026-06-19 sequence (tombstone JSON `updated` timestamps; sampled)
- 11:43:15Z — record 19013315 (Space Ark) tombstoned, note "User was blocked" (cascade).
- 11:43:23Z — the crimsonhexagonal community (a7cc91cc-e640-49ec-913d-0db2fc3aee6f) tombstoned.
- 11:44:26Z — record 20070462 (DePIN analysis), bare "out-of-scope", individually actioned.
- 11:44:35Z — record 20722680 (Josephus MPAI), bare "out-of-scope", individually actioned.
The two individually-judged deletions did not precede the mass action; in execution order they followed the cascade's onset by ~70 seconds (mop-up, not trigger; execution order does not establish deliberation order). All sampled tombstones, including the community, carry `removed_by: user 1060945` (rendered "Admin" in the UI).

## Tombstone behavior
Tombstone JSON continues to serve full record metadata — file entries with checksums and content links, descriptions, related identifiers, usage stats — and the access_status field still reads "The record and files are publicly accessible," while the file content endpoints return HTTP 410 Gone.

## Reconciliation vs sovereign DOI Resolution Index (2026-07-11)
Index tracks 1,940 DOIs; ledger∖index = 212 (`cha-untracked-dead-dois.json` — remediation lane); index∖ledger = 125 (to classify).

## v3 — Tombstone mirror harvest (2026-07-12)

**tombstones/tombstone-api.jsonl** — full API-tombstone census: all 1,136 deleted records + 891 concept parents (2,027 objects), each returning HTTP 410 with tombstone block (removal timestamp to microsecond precision, removed_by, removal_reason, citation_text). Complete sweep chronology: first staff removal 2026-06-19T11:34:17.929620Z, last 11:48:50.039372Z — 872 seconds; 1,915 of 2,005 staff removals in the first five minutes at ~6.6 objects/second sustained. removed_by total enumeration: 2,005 by staff user 1060945; 19 (10 records + 9 parents, 2026-05-16 through 2026-06-15) by uploader user 1505735; 3 objects (18135984, 19359656, 19500795) return 410 with an empty tombstone block. Zero staff deletions before 2026-06-19.

**tombstones/tombstone-mirror.jsonl** — 57 rich HTML-tombstone captures containing the complete embedded record JSON: full metadata, all creators with affiliations, abstracts, related-identifier mesh (152 edges), file inventories with names/sizes/md5 checksums (1,279,828 bytes described), terminal usage statistics (157 downloads, 2,134 unique views at death across the 57).

**Surface-shrink event, documented live:** rich embedded record JSON was served on HTML tombstone pages through 2026-07-12T01:50:52Z (57th capture) and absent from 02:03:55Z onward — under every user-agent tested and via /export/ endpoints, including on records verified rich hours earlier (19013315, 20070462, 20722680; those three full captures preserved in session transcript). Cause indeterminate from a single vantage: platform-side change vs. per-client stripped rendering. **tombstones/raw-tombstone-pages-20260712.tar.gz** preserves all 1,079 post-shrink stripped pages as evidence of the reduced surface state.

Reception finding carried from harvest: the platform continues to serve, for every deleted record, the full citation text naming every heteronym — while the works themselves are gone. The tombstone is the last surface on which the Dodecad still publishes.
