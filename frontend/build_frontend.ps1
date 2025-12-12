# Build helper for the frontend (Windows PowerShell)
# Does: optional venv creation, install requirements, generate app.ico, compile Qt resources (pyrcc5)
# Note: This script does NOT run PyInstaller by default; uncomment the pyinstaller step when you're ready.

param(
    [switch] $UseVenv
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if ($UseVenv) {
    Write-Host "Creating and activating virtual environment .venv (if missing)"
    if (-Not (Test-Path .venv)) {
        python -m venv .venv
    }
    Write-Host "To activate the venv run: .\\.venv\\Scripts\\Activate.ps1"
}

Write-Host "Installing requirements (frontend/requirements.txt)"
if (Test-Path requirements.txt) {
    pip install -r requirements.txt
} else {
    pip install PyQt5
}

# Generate app.ico from app.svg
$iconScript = Join-Path $root 'tools\make_app_icon.py'
if (Test-Path $iconScript) {
    Write-Host "Generating app.ico from app.svg"
    python $iconScript
} else {
    Write-Host "Icon generator script not found: $iconScript"
}

# Compile Qt resources if pyrcc5 is available
$qrc = Join-Path $root 'resources.qrc'
$out = Join-Path $root 'resources_rc.py'
if (Test-Path $qrc) {
    Write-Host "Compiling Qt resources (resources.qrc -> resources_rc.py)"
    # try using pyrcc5
    $pyrcc = Get-Command pyrcc5 -ErrorAction SilentlyContinue
    if ($pyrcc) {
        pyrcc5 -o $out $qrc
    } else {
        Write-Host "pyrcc5 not found; skipping resource compile. You can run: pyrcc5 -o frontend/resources_rc.py frontend/resources.qrc"
    }
} else {
    Write-Host "No resources.qrc found at $qrc"
}

Write-Host "Build script finished. To create a single exe with PyInstaller, run (example):"
Write-Host "pyinstaller --onefile --windowed --icon=resources\\icons\\app.ico --add-data \"resources;resources\" main.py"

# Uncomment and edit the following block to run PyInstaller automatically
<#
Write-Host "Running PyInstaller..."
pyinstaller --onefile --windowed --icon=resources\icons\app.ico --add-data "resources;resources" main.py
#>
