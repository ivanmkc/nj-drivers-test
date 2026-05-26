#!/usr/bin/env bash
# Bulk re-verification of every state at 100% coverage, with the upgraded
# gates from #62. Runs states in parallel batches to bound wall time.
#
# Usage: bash tools/_bulk_verify.sh [PARALLELISM]
# Default parallelism = 8. Each state's stdout/stderr is captured to
# /tmp/bulk_verify/<code>.log; a one-line summary appears here.

set -uo pipefail

PARALLELISM="${1:-8}"
STATES_FILE="${STATES_FILE:-/tmp/states_to_verify.txt}"
LOG_DIR="/tmp/bulk_verify"
mkdir -p "$LOG_DIR"

if [[ ! -f "$STATES_FILE" ]]; then
    echo "states file not found: $STATES_FILE" >&2
    exit 1
fi

start_epoch=$(date +%s)
echo "Bulk re-verification starting at $(date -u +%FT%TZ)"
echo "  parallelism: $PARALLELISM"
echo "  log dir:     $LOG_DIR"
echo "  states:      $(wc -l < "$STATES_FILE")"
echo

verify_one() {
    local code="$1"
    local log="$LOG_DIR/${code}.log"
    local started=$(date +%s)
    if python3 tools/quiz_gates.py "$code" --write-report > "$log" 2>&1; then
        local elapsed=$(( $(date +%s) - started ))
        local verdict grade
        verdict=$(grep -oE 'Overall: [A-Z_]+' "$log" | tail -1 | awk '{print $2}')
        grade=$(grep -oE 'grade [A-F]' "$log" | tail -1 | awk '{print $2}')
        printf '  %s  %3ds  %s  grade=%s\n' "$code" "$elapsed" "${verdict:-?}" "${grade:-?}"
    else
        local exit_code=$?
        local elapsed=$(( $(date +%s) - started ))
        printf '  %s  %3ds  FAILED (exit %d, see %s)\n' "$code" "$elapsed" "$exit_code" "$log"
    fi
}

export -f verify_one
export LOG_DIR

xargs -a "$STATES_FILE" -n 1 -P "$PARALLELISM" -I {} bash -c 'verify_one "$@"' _ {}

elapsed=$(( $(date +%s) - start_epoch ))
echo
echo "Done in ${elapsed}s ($((elapsed / 60))m $((elapsed % 60))s)"
echo
echo "Verdict tally:"
grep -hoE 'Overall: [A-Z_]+' "$LOG_DIR"/*.log | sort | uniq -c | sort -rn
