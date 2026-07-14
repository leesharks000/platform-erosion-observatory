# Rejected-candidate ledger — EA-EROSION-EMPIRICAL-01 v0.1

Per NEGSHAPE §2.4 membership discipline: no citation is rendered without confirmed membership. Rejected candidates are preserved so the dataset holds itself to the disambiguation standard it demands from the institution.

## Status: EMPTY

Zero rejected candidates in this audit's cohort. The criteria against which candidates would have been rejected are preserved below for future audits and for reader verification.

## Criteria for rejection

A candidate is rejected if any of the following holds:

1. **Registered-creator collision.** The candidate's creator name matches a heteronym-shaped string of the archive but the record's other metadata (ORCID, affiliation, cited works) is inconsistent with the archive's registered creator. The Jack Feist / Dr. Jack E. Feist ophthalmologist near-miss in NEGSHAPE §2.4 is the enforcement precedent.

2. **Cross-cohort attribution collision.** The candidate is a record whose citation_text names an author whose surname appears in more than one cascade cohort, and whose given-name or middle-initial is insufficient to disambiguate uniquely.

3. **Unresolved membership basis.** The candidate's citation_text does not permit disambiguation at any tier of the membership vocabulary (`sovereign_registry_exact_doi`, `exact_registered_creator_match`, `datacite_orcid_match`, `datacite_affiliation_match`, etc.).

4. **Recovered title from referencing document rather than from the work itself.** The candidate's title field is a title recovered from a citation-string context that describes a different, referencing work rather than the work at the cited DOI.

## Candidates evaluated and confirmed

All 15 terminated-cohort authors named in §6 of the governing deposit passed membership discipline at `sovereign_registry_exact_doi ∧ exact_registered_creator_match` — each author's records are enumerated in ZENODO-DELETION-EXPORT-20260710 at exact record_ids, and the creator string is consistent across all cited records within the cascade. No cross-author collisions between the 15 cohort members were detected. The 1,360 identifier entries across the 15 cohorts are membership-confirmed.

The Wu Shaoyuan cohort (67 records) passed membership discipline at `sovereign_registry_exact_doi ∧ exact_owner_id_match ∧ same_day_cascade_membership` — all 67 records share owner ID 1499202, share removal_date 2026-04-25, and share creator string "Wu, Shaoyuan" (66) or "Shaoyuan, Wu" (1), with the ORCID identity confirmed at 0009-0008-0660-8232 across the cohort.

## Note on future audits

If this ledger acquires entries in subsequent audit passes, each rejection should record: candidate identifier, cascade container, apparent match reason, disambiguation failure mode, and disposition (quarantined, forwarded to civil-authority correction channel, or retained-for-review).

## Governance

