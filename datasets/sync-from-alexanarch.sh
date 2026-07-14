#!/bin/bash
# sync-from-alexanarch.sh
# Pull latest versions of PEO instrument datasets from alexanarch.org canonical.
# Idempotent; sha256-verifies against MANIFEST.json where present.
#
# Usage:  ./datasets/sync-from-alexanarch.sh [--dry-run]
#
# Canonical authority: alexanarch.org
# Mirror location: this directory tree
set -euo pipefail

DRY_RUN=${1:-}
ROOT="$(cd "$(dirname "$0")" && pwd)"
CANONICAL_BASE="https://www.alexanarch.org"

echo "PEO datasets sync"
echo "Canonical: $CANONICAL_BASE"
echo "Mirror root: $ROOT"
echo

sync_dataset() {
    local dataset_name="$1"
    local canonical_path="$2"
    local files=("${@:3}")
    local local_dir="$ROOT/$dataset_name"
    mkdir -p "$local_dir"
    echo "[$dataset_name]"
    for f in "${files[@]}"; do
        local url="$CANONICAL_BASE/$canonical_path/$f"
        local dest="$local_dir/$f"
        if [ "$DRY_RUN" = "--dry-run" ]; then
            echo "  would fetch $url → $dest"
        else
            echo "  fetching $f..."
            curl -sfSL "$url" -o "$dest" || echo "    (skipped: $url not yet available)"
        fi
    done
    if [ -f "$local_dir/MANIFEST.json" ] && command -v python3 >/dev/null 2>&1; then
        echo "  verifying sha256..."
        python3 -c "
import json, hashlib, os, sys
m = json.load(open('$local_dir/MANIFEST.json'))
ok = True
for fn, meta in m.get('files', {}).items():
    p = '$local_dir/' + fn
    if not os.path.exists(p):
        print(f'    MISSING {fn}')
        ok = False; continue
    h = hashlib.sha256(open(p,'rb').read()).hexdigest()
    if h != meta.get('sha256'):
        print(f'    HASH MISMATCH {fn}: expected {meta.get(\"sha256\")[:16]}... got {h[:16]}...')
        ok = False
sys.exit(0 if ok else 1)
"
    fi
    echo
}

# — Erosion Empirical Audit 01 —
sync_dataset "erosion-empirical-audit-01" \
    "datasets/erosion-empirical-audit-01" \
    "MANIFEST.json" "contingency-matrix.json" "wu-restoration-verification.json" \
    "terminated-cohort-citations.json" "alive-side-control.json" \
    "REJECTED-LEDGER-EMPTY.md" "generate_audit.py"

# — Additional datasets can be added below as they land in alexanarch canonical —
# sync_dataset "negshape-deletion-bibliography" "data/datasets/negshape-deletion-bibliography" ...

echo "Sync complete."
