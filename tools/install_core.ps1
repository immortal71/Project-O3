<#
PowerShell helper to create a venv and install backend/requirements-core.txt
Usage:
  .\install_core.ps1            # create venv (if missing) and install
  .\install_core.ps1 -Recreate  # remove + recreate venv then install
#>
param(
    [switch]$Recreate
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root '..\backend' | Resolve-Path -Relative
$venvPath = Join-Path $backend 'venv'

if ($Recreate -and (Test-Path $venvPath)) {
    Write-Host "Removing existing venv at $venvPath"
    Remove-Item -Recurse -Force $venvPath
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at: $venvPath"
    python -m venv $venvPath
}

$activate = Join-Path $venvPath 'Scripts\Activate.ps1'
if (-not (Test-Path $activate)) {
    Write-Error "Activation script not found; ensure Python is on PATH and venv created successfully."
    exit 1
}

Write-Host "Activating venv..."
. $activate

$reqFile = Join-Path $backend 'requirements-core.txt'
if (-not (Test-Path $reqFile)) {
    Write-Error "requirements-core.txt not found in backend/. Ensure the file exists: $reqFile"
    exit 1
}

Write-Host "Upgrading pip and installing core requirements from $reqFile"
python -m pip install --upgrade pip
python -m pip install -r $reqFile

Write-Host "Done. To run the server:"
Write-Host "  cd $backend"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  $env:OPENAI_API_KEY = '<your key>'  # optional if using real OpenAI"
Write-Host "  uvicorn main:app --reload --host 127.0.0.1 --port 8000"

Write-Host "If you want to run summarization without an API key, set the mock flag:"
Write-Host "  $env:MOCK_LLM = 'true'"
