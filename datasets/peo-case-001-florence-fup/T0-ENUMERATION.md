## T0 enumeration (2026-07-22)

The 14,283-figure lost between the 2026-07-13 and 2026-07-20 census epochs is now
resolved to identifiers. The DataCite Public Data File 2025 (landing DOI
`10.14454/t5qb-d995`), frozen at `2026-01-06T20:11:59Z` — approximately six months
prior to the deletion event — was streamed and filtered on `client_id=crui.unifi`.
The extraction yields **14,284 unique DOIs**, all under prefix `10.13128`:

- 14,282 in `findable` state (one below the tier-1 census's 14,283 figure, consistent with a single state-transition between the T0 snapshot and the 2026-07-13 tier-1 census)
- 2 in `registered` state (a state class DataCite's client-count APIs generally do not surface, hence the +2 versus tier-1)

Update-time distribution places 12,308 DOIs — 86.2% of the corpus — in a four-month window
of mid-2020 (June through September), consistent with a single sustained
metadata refresh event. Secondary refresh points at 2021-03 (528) and
2023-03 (352). Long tail through August 2024. Top source months:
2020-06 (4,939), 2020-08 (3,242), 2020-07 (2,392), 2020-09 (1,735), 2021-03 (528).

The enumeration is deposited at `data/peo-case-001-florence-fup-enumeration.tsv`
alongside this case file, and structured facts at
`data/peo-case-001-florence-fup-t0-summary.json`. The enumeration is
redistributed from the DataCite Public Data File under its CC-BY license and
constitutes a recovery map for the 10.13128 corpus that currently resolves to
`https://journals.fupress.net/inactive-doi/`.

### Sample identifiers

For scale reference, three DOIs spanning the alphabetical range:

- `10.13128/1970-9501-2450`
- `10.13128/ijae-16987`
- `10.13128/techne-9971`

### Data-quality note

Two DOIs in the corpus (`10.13128/10.13128/ahs-23289`,
`10.13128/10.13128/rea-25108`) embed the `10.13128` prefix a second time inside
the suffix. They resolve as valid DataCite identifiers in the T0 snapshot and
are preserved unaltered in the enumeration; any re-registration pass should
inspect them individually.

### Extraction method note

The 2025 Public Data File is a 34.4 GB tar containing per-month
`dois/updated_YYYY-MM/YYYY-MM.csv.gz` members, each a compact projection of
`(doi, state, client_id, updated)` for DOIs whose last update fell in that
month. Streaming the tar via chunked HTTP Range requests to
`datafiles.datacite.org` — each chunk triggering a fresh S3 presigned URL
through the DataCite 302 (5-minute presigned TTL, ~180 chunks at 128 MB) —
avoids both bulk download (615 GB decompressed, 32 GB compressed) and the
single-connection expiration failure mode. Global filter yields per-client
enumerations without materializing the full 108,468,906-record file.
