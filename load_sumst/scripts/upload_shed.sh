#!/usr/bin/env bash
set -euo pipefail

tools_root="$1"
SHED="$2"

planemo \
    shed_upload . \
    --shed_target $SHED \
    --force_repository_creation