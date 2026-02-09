#!/usr/bin/env bash
# set -euo pipefail

# tools_root="$1"
# SHED="$2"

# planemo \
#     shed_create \
#     --shed_target $SHED


#!/usr/bin/env bash
set -euo pipefail

tools_root="$1"
SHED="$2"

if ! planemo shed_create --shed_target "$SHED"; then
    echo "Repository may already exist. Ignoring."
fi
