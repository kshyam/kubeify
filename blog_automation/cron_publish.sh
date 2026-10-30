#!/bin/bash
set -euo pipefail
export PATH="$HOME/.opencode/bin:/usr/local/bin:/usr/bin:/bin"
export TZ=Asia/Kolkata
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${KUBEIFY_BLOG_ENV_FILE:-$HOME/.config/kubeify/blog.env}"
if [ -f "$ENV_FILE" ]; then
    set -a
    . "$ENV_FILE"
    set +a
fi
exec /usr/bin/flock -n /tmp/kubeify-blog-publish.lock /usr/bin/python3 "$SCRIPT_DIR/publish.py"
