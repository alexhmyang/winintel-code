#!/usr/bin/env bash
set -euo pipefail
# User-level Ubuntu installation; no npm, Docker or root required.
VERSION="0.1.0"
ENGINE_VERSION="1.19.6"
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(uname -s)" != Linux ]]; then
  echo "此安装器用于 Linux / Ubuntu。" >&2
  exit 1
fi
for tool in python3 curl tar install; do
  command -v "$tool" >/dev/null || { echo "缺少 $tool，请安装后重试。" >&2; exit 1; }
done
case "$(uname -m)" in
  x86_64) asset="opencode-linux-x64-baseline.tar.gz" ;;
  aarch64|arm64) asset="opencode-linux-arm64.tar.gz" ;;
  *) echo "支持 x86_64 和 ARM64。" >&2; exit 1 ;;
esac
target="$HOME/.local/share/winintel-code"
stage="$(mktemp -d)"
trap 'rm -rf -- "$stage"' EXIT
if [[ -n "${WININTEL_ENGINE_ARCHIVE:-}" ]]; then
  cp -- "$WININTEL_ENGINE_ARCHIVE" "$stage/engine.tar.gz"
else
  curl --fail --location --retry 2 --connect-timeout 15 --max-time 300 \
    "https://github.com/anomalyco/opencode/releases/download/v${ENGINE_VERSION}/${asset}" \
    -o "$stage/engine.tar.gz"
fi
tar -xzf "$stage/engine.tar.gz" -C "$stage"
[[ -f "$stage/opencode" ]] || { echo "引擎安装包格式不正确。" >&2; exit 1; }
chmod +x "$stage/opencode"
actual="$("$stage/opencode" --version)"
[[ "$actual" == "$ENGINE_VERSION" ]] || { echo "引擎版本不匹配：$actual" >&2; exit 1; }
mkdir -p "$target/engine" "$HOME/.local/bin" "$HOME/.local/share/applications"
install -m 755 "$stage/opencode" "$target/engine/opencode"
install -m 644 "$SOURCE/winintel_code.py" "$target/winintel_code.py"
install -m 644 "$SOURCE/LICENSE" "$target/LICENSE"
install -m 644 "$SOURCE/THIRD_PARTY_NOTICES.md" "$target/THIRD_PARTY_NOTICES.md"
python3 - "$target" "$HOME/.local/bin/winintel-code" "$HOME/.local/share/applications/winintel-code.desktop" <<'PY'
from pathlib import Path
import shlex
import sys
target, launcher, desktop = map(Path, sys.argv[1:])
launcher.write_text('#!/bin/sh\nexec python3 ' + shlex.quote(str(target / "winintel_code.py")) + ' "$@"\n')
launcher.chmod(0o755)
exec_path = str(launcher).replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$").replace("%", "%%")
desktop.write_text(
    '[Desktop Entry]\nType=Application\nName=winintel AI Code Agent\n'
    'Comment=Ubuntu 中文 AI 编程助手\nExec="' + exec_path + '" gui\n'
    'Icon=utilities-terminal\nTerminal=false\nCategories=Development;\n')
PY
if ! python3 -c 'import tkinter' 2>/dev/null; then
  echo "桌面入口需要：sudo apt install python3-tk"
fi
echo "winintel-code $VERSION 已安装。"
echo "启动：$HOME/.local/bin/winintel-code web --project /你的项目目录"
echo "桌面：应用菜单 → winintel AI Code Agent"
echo '命令不在 PATH 时：export PATH="$HOME/.local/bin:$PATH"'
