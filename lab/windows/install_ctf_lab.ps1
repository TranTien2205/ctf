# install_ctf_lab.ps1
# Install the CTF practice range on a Windows host for an agent to run.
#
# It installs the prerequisites, clones the Amazon Science CTF-Dojo and
# Cyber-Zero repositories, and prepares the Python environments. It does NOT
# generate challenges or start containers; run ctf_forge.py and start_challenge.ps1
# afterwards.
#
# Usage (elevated PowerShell):
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   .\install_ctf_lab.ps1 -Root C:\ctf-lab
#
# The repositories are licensed CC-BY-NC-4.0 (non-commercial). Keep them in this
# lab directory, outside any repository you own or publish.

param(
    [string]$Root = "C:\ctf-lab",
    [string]$PythonVersion = "3.11",
    [switch]$SkipDocker,
    [switch]$CloneArchive
)

$ErrorActionPreference = "Stop"

function Say($msg) { Write-Host "[ctf-lab] $msg" -ForegroundColor Cyan }
function Have($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

function Ensure-Winget {
    if (-not (Have "winget")) {
        throw "winget is required. Install App Installer from the Microsoft Store, then re-run."
    }
}

function Install-Package($id, $label) {
    Say "installing $label ($id)"
    winget install --id $id --exact --accept-package-agreements --accept-source-agreements --silent
}

Say "target root: $Root"
New-Item -ItemType Directory -Force -Path $Root | Out-Null

Ensure-Winget

if (-not (Have "git")) { Install-Package "Git.Git" "Git" } else { Say "git present" }
if (-not (Have "python")) { Install-Package "Python.Python.$($PythonVersion -replace '\.','')" "Python $PythonVersion" } else { Say "python present" }

if (-not $SkipDocker) {
    if (-not (Have "docker")) {
        Install-Package "Docker.DockerDesktop" "Docker Desktop"
        Say "Docker Desktop installed. Start it once and enable 'Expose daemon' only if you understand the risk."
    } else {
        Say "docker present"
    }
}

# Refresh PATH for this session after installs.
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path", "User")

$Dojo = Join-Path $Root "CTF-Dojo"
$Cyber = Join-Path $Root "Cyber-Zero"

if (-not (Test-Path $Dojo)) {
    Say "cloning CTF-Dojo"
    git clone --depth 1 https://github.com/amazon-science/CTF-Dojo.git $Dojo
} else { Say "CTF-Dojo already cloned" }

if (-not (Test-Path $Cyber)) {
    Say "cloning Cyber-Zero"
    git clone --depth 1 https://github.com/amazon-science/Cyber-Zero.git $Cyber
} else { Say "Cyber-Zero already cloned" }

if ($CloneArchive) {
    $Archive = Join-Path $Dojo "ctf-archive"
    if (-not (Test-Path $Archive)) {
        Say "cloning the pwn.college ctf-archive template (this is large)"
        git clone --depth 1 https://github.com/pwncollege/ctf-archive.git $Archive
    } else { Say "ctf-archive already cloned" }
}

Say "creating the CTF-Dojo virtual environment"
Push-Location $Dojo
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Pop-Location

$Served = Join-Path $Root "served"
New-Item -ItemType Directory -Force -Path $Served | Out-Null

Say "done. Next steps:"
Write-Host ""
Write-Host "  1. Generate a small batch of challenges (needs an LLM API key):"
Write-Host "       cd $Dojo"
Write-Host "       .\.venv\Scripts\python.exe ctf_forge.py --filter_category web --max_tasks 5 --workers 4"
Write-Host "       .\.venv\Scripts\python.exe generate_metadata.py"
Write-Host ""
Write-Host "  2. Start one challenge and expose it to the VM agent:"
Write-Host "       .\start_challenge.ps1 -ChallengePath <task-dir> -HostIp <windows-lan-ip>"
Write-Host ""
Write-Host "  3. Serve the target list so the VM agent can read it:"
Write-Host "       .\serve_lab.ps1"
Write-Host ""
Write-Host "  4. In the Kali VM, point the ctf-v2 agent at it:"
Write-Host "       python3 tools/lab_sync.py --targets http://<windows-lan-ip>:8899/lab_targets.json --list"
