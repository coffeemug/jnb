#!/usr/bin/env bash
# Remove the `jnb` symlink created by install.sh. Your notebooks are left alone.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
link="${JNB_BIN_DIR:-$HOME/.local/bin}/jnb"

if [[ -L "$link" && "$(readlink "$link")" == "$here/bin/jnb" ]]; then
  rm "$link"
  echo "Removed $link"
else
  echo "No jnb symlink from this repo at $link; nothing to do."
fi
