#!/usr/bin/env bash
# Run the us-quality-gate skill headlessly on every eval case.
# Usage: ./run_skill.sh <out-dir> [runs-per-case]
# Each run happens in its own work dir: <out-dir>/<case>/run-<n>/
# Then score the results:  python3 run_eval.py <out-dir>
set -euo pipefail
OUT="${1:?usage: run_skill.sh <out-dir> [runs]}"
RUNS="${2:-3}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$HERE/../.." && pwd)"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"

for case_dir in "$HERE"/cases/*/; do
  name="$(basename "$case_dir")"
  for n in $(seq 1 "$RUNS"); do
    work="$OUT/$name/run-$n"
    mkdir -p "$work"
    cp "$case_dir/story.md" "$work/story.md"
    echo "== $name run $n"
    (cd "$work" && claude -p \
      "Use the us-quality-gate skill on the user story in ./story.md. Write the artifacts under ./qe-artifacts/. Do not post anything to external tools." \
      --plugin-dir "$PLUGIN" \
      --permission-mode acceptEdits \
      --allowedTools "Read,Write,Edit,Bash(python3:*)" \
      > "$work/transcript.txt" 2>&1) || echo "   (claude exited non-zero; see $work/transcript.txt)"
  done
done
