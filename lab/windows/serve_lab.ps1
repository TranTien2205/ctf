# serve_lab.ps1
# Serve C:\ctf-lab\served over HTTP so the VM agent can read lab_targets.json
# and download challenge source archives.
#
# Usage:
#   .\serve_lab.ps1 -HostIp 192.168.1.20 -Port 8899
#
# The server binds 0.0.0.0 so the VM can reach it. Keep it on a private network.
# Press Ctrl+C to stop.

param(
    [string]$HostIp = "",
    [int]$Port = 8899,
    [string]$Root = "C:\ctf-lab"
)

$ErrorActionPreference = "Stop"
function Say($msg) { Write-Host "[ctf-lab] $msg" -ForegroundColor Cyan }

$Served = Join-Path $Root "served"
New-Item -ItemType Directory -Force -Path $Served | Out-Null

if (-not $HostIp) {
    $HostIp = (Get-NetIPAddress -AddressFamily IPv4 |
               Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
               Select-Object -First 1 -ExpandProperty IPAddress)
    if (-not $HostIp) { $HostIp = "127.0.0.1" }
}

if (-not (Get-NetFirewallRule -DisplayName "ctf-lab-targets" -ErrorAction SilentlyContinue)) {
    Say "adding inbound firewall rule for port $Port"
    New-NetFirewallRule -DisplayName "ctf-lab-targets" -Direction Inbound -Action Allow `
        -Protocol TCP -LocalPort $Port -Profile Any | Out-Null
}

Say "serving $Served on 0.0.0.0:$Port"
Say "target list: http://$HostIp`:$Port/lab_targets.json"
Write-Host "  VM command: python3 tools/lab_sync.py --targets http://$HostIp`:$Port/lab_targets.json --list"
Write-Host ""

Push-Location $Served
python -m http.server $Port --bind 0.0.0.0
Pop-Location
