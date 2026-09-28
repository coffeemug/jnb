#!/usr/bin/env bash
# Put `jnb` on your PATH by symlinking it into ~/.local/bin (or $JNB_BIN_DIR).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bin="${JNB_BIN_DIR:-$HOME/.local/bin}"

command -v uv >/dev/null || { echo "jnb needs uv: https://docs.astral.sh/uv/" >&2; exit 1; }

mkdir -p "$bin"
ln -sfn "$here/bin/jnb" "$bin/jnb"
echo "Installed $bin/jnb -> $here/bin/jnb"

case ":$PATH:" in
  *":$bin:"*) ;;
  *) echo "Note: $bin is not on your PATH. Add it in your shell rc to use jnb." ;;
esac
