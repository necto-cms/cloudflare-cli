#Requires -Version 5.1
<#
.SYNOPSIS
  Cloudflare Manager CLI installer for Windows PowerShell

.DESCRIPTION
  Installs the Cloudflare Manager CLI by setting up a Python virtual environment,
  installing dependencies, and creating a .env file from the example.

.PARAMETER VenvDir
  Path to the virtual environment directory (default: .venv)

.PARAMETER PythonExe
  Path to the Python executable (auto-detected if not provided)

.PARAMETER NonInteractive
  If true, skip user prompts (useful for CI/CD)

.EXAMPLE
  .\install.ps1
  .\install.ps1 -VenvDir "myenv" -PythonExe "python3.11"
#>

param(
  [string]$VenvDir = ".venv",
  [string]$PythonExe = "",
  [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"

Write-Host "Cloudflare Manager CLI - installer (Windows PowerShell)" -ForegroundColor Cyan
Write-Host "Venv directory: $VenvDir" -ForegroundColor Gray
Write-Host "Non-interactive mode: $NonInteractive" -ForegroundColor Gray
Write-Host ""

# Function to exit with error
function Die {
  param([string]$Message)
  Write-Host "ERROR: $Message" -ForegroundColor Red
  exit 1
}

# Find Python executable
if ([string]::IsNullOrEmpty($PythonExe)) {
  $pythonCandidates = @("python3", "python")
  $PythonExe = $null
  
  foreach ($candidate in $pythonCandidates) {
    try {
      if ((& $candidate --version) -match "Python") {
        $PythonExe = $candidate
        break
      }
    } catch {
      # Continue to next candidate
    }
  }
  
  if ([string]::IsNullOrEmpty($PythonExe)) {
    Die "Python not found in PATH. Please install Python 3.8+ and retry."
  }
}

# Verify Python is available
try {
  $pythonVersion = & $PythonExe -c 'import sys; print(".".join(map(str, sys.version_info[:2])))' 2>$null
} catch {
  Die "Failed to run Python executable: $PythonExe"
}

Write-Host "Using python: $PythonExe (version $pythonVersion)" -ForegroundColor Green

# Check for pip
try {
  & $PythonExe -m pip --version | Out-Null
} catch {
  Die "pip module not found or not working. Please install pip or ensure it's available via 'python -m pip'."
}

Write-Host "pip is available" -ForegroundColor Green
Write-Host ""

# Create virtual environment
if (Test-Path $VenvDir) {
  Write-Host "Virtual environment already exists at $VenvDir. Skipping creation." -ForegroundColor Yellow
} else {
  Write-Host "Creating virtual environment at $VenvDir..."
  try {
    & $PythonExe -m venv $VenvDir
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
  } catch {
    Die "Failed to create virtual environment: $_"
  }
}

# Activate virtual environment
$ActivateScript = Join-Path $VenvDir "Scripts" "Activate.ps1"
if (Test-Path $ActivateScript) {
  Write-Host "Activating virtual environment..."
  & $ActivateScript
} else {
  Die "Could not find Activate.ps1 in $VenvDir\Scripts"
}

# Upgrade pip
Write-Host "Upgrading pip..."
try {
  & python -m pip install --upgrade pip --quiet
  Write-Host "✓ pip upgraded" -ForegroundColor Green
} catch {
  Die "Failed to upgrade pip: $_"
}

# Install requirements
if (Test-Path "requirements.txt") {
  Write-Host "Installing requirements from requirements.txt..."
  try {
    & python -m pip install -r requirements.txt --quiet
    Write-Host "Installing the CLI package..."
    & python -m pip install . --quiet
    Write-Host "✓ Requirements and package installed" -ForegroundColor Green
  } catch {
    Die "Failed to install requirements or package: $_"
  }
} else {
  Write-Host "WARNING: requirements.txt not found" -ForegroundColor Yellow
}

# Create .env from example if missing
if ((Test-Path ".env") -eq $false -and (Test-Path ".env.example")) {
  Write-Host "Creating .env from .env.example..."
  Copy-Item ".env.example" ".env"
  Write-Host "✓ .env created from .env.example" -ForegroundColor Green
  Write-Host "  Edit .env to add your CLOUDFLARE_API_TOKEN and other values." -ForegroundColor Gray
} elseif (Test-Path ".env") {
  Write-Host "✓ .env already exists (not overwriting)" -ForegroundColor Green
} else {
  Write-Host "WARNING: .env.example not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Installation finished successfully! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Quick start:" -ForegroundColor Cyan
Write-Host "  cf" -ForegroundColor White
Write-Host ""
Write-Host "To deactivate the virtual environment later:" -ForegroundColor Gray
Write-Host "  deactivate" -ForegroundColor White
Write-Host ""

Write-Host "Done!" -ForegroundColor Green
