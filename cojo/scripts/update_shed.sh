#!/usr/bin/env bash
set -euo pipefail

tools_root="$1"
SHED="$2"
# KEY="$3"

planemo \
    shed_update \
    --check_diff \
    --shed_target $SHED \
# --force_repository_creation\
# --recursive\
# --shed_key $KEY \
# ${tools_root}