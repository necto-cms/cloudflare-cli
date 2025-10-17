#!/usr/bin/env bash
set -euo pipefail

# Script options
VENV_DIR="${VENV_DIR:-.venv}"
NON_INTERACTIVE="${NON_INTERACTIVE:-0}"
PYTHON="${PYTHON:-}"

echo "Cloudflare Manager CLI - installer"
echo "Venv directory: $VENV_DIR"
echo "Non-interactive mode: $NON_INTERACTIVE"

# Function to exit with error
die() {
  echo "ERROR: $*" >&2
  exit 1
}

# Choose python executable
if [ -z "$PYTHON" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
  elif command -v python >/dev/null 2>&1; then
    PYTHON=python
  else
    die "Python not found in PATH. Please install Python 3.8+ and retry."
  fi
fi

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  die "Python executable not found: $PYTHON"
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>/dev/null || echo "unknown")
echo "Using python: $PYTHON (version $PYTHON_VERSION)"

# Check for pip
if ! $PYTHON -m pip --version >/dev/null 2>&1; then
  die "pip module not found or not working. Please install pip or ensure it's available via 'python -m pip'."
fi

echo "pip is available"

# create virtual environment
if [ -d "$VENV_DIR" ]; then
  echo "Virtual environment already exists at $VENV_DIR. Skipping creation."
else
  echo "Creating virtual environment at $VENV_DIR..."
  $PYTHON -m venv "$VENV_DIR" || die "Failed to create virtual environment"
fi

# Activate venv for this script (POSIX)
if [ -f "$VENV_DIR/bin/activate" ]; then
  # shellcheck source=/dev/null
  . "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
  # Windows-style (in MSYS/WSL this may work)
  # shellcheck source=/dev/null
  . "$VENV_DIR/Scripts/activate"
fi


echo "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip || die "Failed to upgrade pip"

if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt || die "Failed to install requirements from requirements.txt"
  echo "Installing the CLI package..."
  python -m pip install . || die "Failed to install the CLI package"
else
  echo "WARNING: requirements.txt not found, skipping pip install -r requirements.txt"
fi

# Create .env from example if missing
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "✓ .env created from .env.example"
  echo "  Edit .env to add your CLOUDFLARE_API_TOKEN and other values."
elif [ -f .env ]; then
  echo "✓ .env already exists (not overwriting)"
else
  echo "WARNING: .env.example not found, skipping .env creation"
fi

echo ""
echo "=== Installation finished successfully! ==="
echo ""
echo "Quick start:"
if [ -f "$VENV_DIR/bin/activate" ]; then
  echo "  source $VENV_DIR/bin/activate"
else
  echo "  # On Windows PowerShell:"
  echo "  .\\$VENV_DIR\\Scripts\\Activate.ps1"
fi
echo "  cf"
echo ""
echo "Environment variables (optional):"
echo "  VENV_DIR=<path>       - Custom venv directory (default: .venv)"
echo "  PYTHON=<python-exe>   - Custom Python executable (auto-detected if not set)"
echo "  NON_INTERACTIVE=1     - Run without user prompts (for CI/CD)"
echo ""

echo "If you want to run this installer directly from GitHub via curl|bash, use (replace <user>/<repo> and branch):"
echo "  curl -fsSL https://raw.githubusercontent.com/<user>/<repo>/main/install.sh | bash -s --"
echo "The script itself sets 'set -e' so it will exit on errors."