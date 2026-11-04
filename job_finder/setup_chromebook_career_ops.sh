#!/usr/bin/env bash
# One-command installer for Career Ops + Codex in the ChromeOS Linux container.
# Run as your normal Linux user, not with sudo. Personal CV/application data
# remains on the Chromebook. No LinkedIn messages or applications are sent.
set -Eeuo pipefail
trap 'printf "\nSetup stopped near line %s. Copy the error message into ChatGPT for help.\n" "$LINENO" >&2' ERR

if [[ "$(id -u)" -eq 0 ]]; then
  printf 'Please run this as your regular Chromebook Linux user, not root.\n' >&2
  exit 1
fi
if ! command -v sudo >/dev/null 2>&1; then
  printf 'This requires the ChromeOS Linux development environment with sudo enabled.\n' >&2
  exit 1
fi

printf '\n[1/5] Installing basic Linux packages...\n'
sudo apt-get update
sudo apt-get install -y git curl ca-certificates build-essential

printf '\n[2/5] Preparing Node.js 22 using the nvm version manager...\n'
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
  temp_install="$(mktemp)"
  trap 'rm -f "${temp_install:-}"' EXIT
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh -o "$temp_install"
  bash "$temp_install"
fi
# nvm's setup script updates the shell profile, but this running script needs
# to load it into the current process explicitly.
if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
  printf 'Could not find nvm at %s\n' "$NVM_DIR" >&2
  exit 1
fi
# shellcheck disable=SC1091
source "$NVM_DIR/nvm.sh"
nvm install 22
nvm alias default 22
nvm use 22
printf 'Node: %s | npm: %s\n' "$(node -v)" "$(npm -v)"

printf '\n[3/5] Installing the Codex coding assistant...\n'
if ! command -v codex >/dev/null 2>&1; then
  npm install -g @openai/codex
else
  printf 'Codex is already installed; leaving it as-is.\n'
fi

printf '\n[4/5] Installing Career Ops privately in your home directory...\n'
cd "$HOME"
if [[ -e "$HOME/career-ops" ]]; then
  if [[ -f "$HOME/career-ops/package.json" ]]; then
    printf 'Career Ops folder already exists; leaving your data untouched.\n'
  else
    printf '%s exists but does not look like a Career Ops installation.\n' "$HOME/career-ops" >&2
    printf 'For safety, no files were deleted or overwritten.\n' >&2
    exit 1
  fi
else
  npx --yes @santifer/career-ops init
fi

printf '\n[5/5] Checking installed programs...\n'
command -v git >/dev/null
command -v node >/dev/null
command -v codex >/dev/null
if [[ ! -f "$HOME/career-ops/package.json" ]]; then
  printf 'Career Ops did not create the expected folder. Please share the output.\n' >&2
  exit 1
fi
printf '\nSetup completed! Your Career Ops project is: %s\n' "$HOME/career-ops"
printf 'Your GitHub Job Finder remains unchanged.\n'
printf 'Next: Follow the Codex sign-in prompt to connect your ChatGPT account.\n'
printf 'Never paste passwords, one-time codes, or other account secrets here.\n\n'

cd "$HOME/career-ops"
exec codex
