#!/usr/bin/env bash
# Reference SessionStart hook (see AGENTS-rules/enforced/suggested/agents-md-size-check/).
# Install at ~/.posit/assistant/hooks/ (user-wide) or <project>/.posit/assistant/hooks/,
# and reference it from settings.json's hooks.SessionStart.
#
# AGENTS.md is read in full every conversation, so its size is a recurring token cost.
# Prints a short note (injected as context) only when it exceeds a line threshold;
# silent otherwise. It never edits anything. Threshold: AGENTS_MD_MAX_LINES (default 200).

max="${AGENTS_MD_MAX_LINES:-200}"
dir="${PA_PROJECT_DIR:-$PWD}"
f="$dir/AGENTS.md"

[ -f "$f" ] || exit 0

lines=$(wc -l < "$f")
bytes=$(wc -c < "$f")
tokens=$((bytes / 4)) # rough estimate: ~4 characters per token

if [ "$lines" -gt "$max" ]; then
  cat <<EOF
# AGENTS.md size notice
AGENTS.md is ${lines} lines (~${tokens} tokens), above the ${max}-line guide. It is loaded
in full every conversation. Do not trim it unprompted. When it is next edited, or if the
user asks about token use, suggest moving rarely-needed detail (long status logs,
catalogues, how-tos) into an on-demand skill or reference file, and let the user decide.
EOF
fi
