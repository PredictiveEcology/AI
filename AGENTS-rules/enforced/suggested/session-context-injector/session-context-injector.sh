#!/usr/bin/env bash
# Reference SessionStart hook (see AGENTS-rules/enforced/suggested/session-context-injector/).
# Prints one line per git repository directly under the project folder: branch, origin,
# upstream, and ahead/behind versus the tracked branch. Read-only; never fetches.
# Environment facts only; behavioural rules live in default/hooks/session-guardrails.sh.
# Limit: MAX_REPOS (default 40).

dir="${PA_PROJECT_DIR:-$PWD}"
max="${MAX_REPOS:-40}"
n=0
out=""

for g in "$dir"/*/.git; do
  [ -e "$g" ] || continue
  r="$(dirname "$g")"
  n=$((n + 1))
  [ "$n" -gt "$max" ] && break
  name="$(basename "$r")"
  branch="$(git -C "$r" symbolic-ref --short -q HEAD || echo 'detached')"
  origin="$(git -C "$r" remote get-url origin 2>/dev/null | sed -E 's#.*[:/]([^/:]+/[^/]+)$#\1#; s#\.git$##')"
  upstream="$(git -C "$r" remote get-url upstream 2>/dev/null | sed -E 's#.*[:/]([^/:]+/[^/]+)$#\1#; s#\.git$##')"
  counts="$(git -C "$r" rev-list --left-right --count 'HEAD...@{upstream}' 2>/dev/null)"
  if [ -n "$counts" ]; then
    set -- $counts
    track="ahead $1 / behind $2"
  else
    track="no tracking branch"
  fi
  out="${out}- ${name}: ${branch} (origin=${origin:-none}, upstream=${upstream:-none}; ${track})"$'\n'
done

if [ -n "$out" ]; then
  printf '# Repository state (at session start)\n%s' "$out"
fi
