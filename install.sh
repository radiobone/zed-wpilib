#!/bin/sh
# zed-wpilib installer for macOS and Linux. Teammates run:
#   curl -fsSL https://raw.githubusercontent.com/radiobone/zed-wpilib/main/install.sh | sh
# Running it again updates. From a clone you can also just run ./install.sh
set -eu

REPO="${ZED_WPILIB_REPO:-https://github.com/radiobone/zed-wpilib}"
BRANCH="${ZED_WPILIB_BRANCH:-main}"
DEST="${ZED_WPILIB_DIR:-$HOME/.local/share/zed-wpilib}"

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
    PY="$c"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "zed-wpilib needs Python 3.9 or newer."
  echo "  macOS: run  xcode-select --install  (or: brew install python), then run this again."
  echo "  Linux: install python3 with your package manager, then run this again."
  exit 1
fi

# Running from a checkout? Install from it directly.
HERE=$(CDPATH='' cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || true)
if [ -n "$HERE" ] && [ -f "$HERE/install.py" ] && [ -f "$HERE/bin/wpilib" ]; then
  exec "$PY" "$HERE/install.py" "$@"
fi

if [ -d "$DEST/.git" ]; then
  echo "Updating $DEST"
  git -C "$DEST" pull --ff-only
elif command -v git >/dev/null 2>&1 && [ ! -e "$DEST" ]; then
  echo "Downloading zed-wpilib to $DEST"
  git clone --depth 1 --branch "$BRANCH" "$REPO" "$DEST"
else
  echo "Downloading zed-wpilib to $DEST"
  mkdir -p "$DEST"
  curl -fsSL "$REPO/archive/refs/heads/$BRANCH.tar.gz" | tar -xz -C "$DEST" --strip-components 1
fi

exec "$PY" "$DEST/install.py" "$@"
