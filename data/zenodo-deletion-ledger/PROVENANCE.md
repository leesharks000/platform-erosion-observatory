# Zenodo Deletion Ledger — CHA Cohort Extraction
Retrieved 2026-07-11 from https://zenodo.org/api/exporter (records-deleted.csv.gz).

**Source snapshots (Zenodo's own monthly dumps; only latest 3 retained by Zenodo):**
- HEAD: created 2026-07-10T03:32:35Z, version_id c7571d4c-28ef-46ff-b0f0-235abaac58bf, md5 33877aba1fb5684f86758cb86ddc1ad4, 24,367,356 bytes → `deleted-head-20260710.csv.gz` (1,322,017 rows)
- PRIOR: created 2026-06-07T04:02:07Z, version_id ab4e273f-40a2-49e6-84f6-87dc66af87c7, md5 104e2f5c2603dc56217ece0d5519bff8, 23,501,144 bytes → `deleted-20260607.csv.gz` (1,309,361 rows)

**Schema:** record_id, doi, parent_id, parent_doi, removal_note, removal_reason, removal_date, citation_text.

**CHA cohort (`cha-kill-ledger-20260619.csv`, strict author/entity pattern):** 1,137 record rows; 1,126 dated 2026-06-19 (overwhelmingly note="User was blocked", reason="out-of-scope" — account-level, no per-record judgment); 11-row pre-termination drip (2026-05-16 personal-data; 2026-06-02 retracted; 2026-06-10 ×6 duplicate; 2026-06-14 duplicate = GW.TACHYON.zenodo v9; 2026-06-15 duplicate). DOIs touched: 1,137 record + 892 concept = 2,029 union. Pattern-matching caveat: initials-style surname collisions possible at the margin; June-19 site-wide blocked+out-of-scope total was ~1,198 rows including at least one other terminated account.

**Reconciliation vs sovereign DOI Resolution Index (2026-07-11):** index tracks 1,940 DOIs; ledger∖index = 214 (see `cha-untracked-dead-dois.json` — remediation lane); index∖ledger = 125 (to classify).

**Context:** June-19 site-wide deletions: 1,422. Adjacent blocked accounts in ledger: 2026-05-07 (AKTAŞ), 2026-06-26 (Rosehill — AI-collaborative author, one week post-CHA). citation_text preserves full author citations including heteronyms and Assembly witnesses.
