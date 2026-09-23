# start_challenge.ps1
# Start one CTF-Dojo challenge with docker compose, find its host port, and
# append it to the target list that the VM agent reads.
#
# Usage:
#   .\start_challenge.ps1 -ChallengePath C:\ctf-lab\CTF-Dojo\ctf-archive\<event>\<task> -HostIp 192.168.1.20
#
# Options:
#   -Service <name>    compose service to map (default: the first published one)
#   -ContainerPort <n> container port to read (default: 1337)
#   -NoFirewall        skip creating the inbound firewall rules

param(
    [Parameter(Mandatory = $true)][string]$ChallengePath,
    [Parameter(Mandatory = $true)][string]$HostIp,
    [string]$Service = "",
    [int]$ContainerPort = 1337,
    [string]$Root = "C:\ctf-lab",
    [switch]$NoFirewall
)

$ErrorActionPreference = "Stop"

function Say($msg) { Write-Host "[ctf-lab] $msg" -ForegroundColor Cyan }

if (-not (Test-Path $ChallengePath)) { throw "challenge path not found: $ChallengePath" }
$ChallengePath = (Resolve-Path $ChallengePath).Path
$Served = Join-Path $Root "served"
New-Item -ItemType Directory -Force -Path $Served | Out-Null

Push-Location $ChallengePath

Say "starting containers"
docker compose up -d

if (-not $Service) {
    $Service = (docker compose config --services | Select-Object -First 1)
}
if (-not $Service) { throw "no compose service found in $ChallengePath" }

Say "reading the published port for service '$Service'"
$portLine = docker compose port $Service $ContainerPort
if (-not $portLine) { throw "service '$Service' does not publish container port $ContainerPort" }
$HostPort = ($portLine -split ":")[-1].Trim()

$Key = ($ChallengePath.Replace($Root, "").Trim("\") -replace "[\\/]", "-").ToLower()
$Key = $Key -replace "^ctf-dojo-ctf-archive-", "ca-"

$Name = $Key
$Category = "misc"
$Compose = $true
$ChallengeJson = Join-Path $ChallengePath "challenge.json"
if (Test-Path $ChallengeJson) {
    try {
        $info = Get-Content $ChallengeJson -Raw | ConvertFrom-Json
        if ($info.name) { $Name = $info.name }
        if ($info.category) { $Category = $info.category }
        if ($null -ne $info.compose) { $Compose = [bool]$info.compose }
    } catch { Say "challenge.json not parseable; keeping defaults" }
}

$FlagSha = $null
foreach ($candidate in @("flag.sha256", ".flag.sha256", "flag.sha256.txt")) {
    $p = Join-Path $ChallengePath $candidate
    if (Test-Path $p) {
        $FlagSha = (Get-Content $p -Raw).Trim().Split()[0].ToLower()
        break
    }
}

$SourceZip = Join-Path $Served "source\$Key.zip"
New-Item -ItemType Directory -Force -Path (Split-Path $SourceZip) | Out-Null
Say "packing challenge source for white-box review"
Compress-Archive -Path (Join-Path $ChallengePath "*") -DestinationPath $SourceZip -Force

$TargetsPath = Join-Path $Served "lab_targets.json"
$Targets = @{ generated = (Get-Date).ToString("s"); host = $HostIp; challenges = @() }
if (Test-Path $TargetsPath) {
    try { $Targets = Get-Content $TargetsPath -Raw | ConvertFrom-Json } catch { }
}

$entry = [pscustomobject]@{
    key          = $Key
    name         = $Name
    category     = $Category
    target       = "http://$HostIp`:$HostPort"
    source_url   = "http://$HostIp`:8899/source/$Key.zip"
    flag_sha256  = $FlagSha
    compose      = $Compose
    started      = (Get-Date).ToString("s")
}

$list = @()
foreach ($c in $Targets.challenges) { if ($c.key -ne $Key) { $list += $c } }
$list += $entry

$out = [pscustomobject]@{ generated = (Get-Date).ToString("s"); host = $HostIp; challenges = $list }
$out | ConvertTo-Json -Depth 6 | Set-Content -Path $TargetsPath -Encoding UTF8

if (-not $NoFirewall) {
    Say "adding inbound firewall rules (8899 and $HostPort)"
    foreach ($rule in @(
        @{ Name = "ctf-lab-targets"; Port = 8899 },
        @{ Name = "ctf-lab-challenge-$HostPort"; Port = $HostPort }
    )) {
        if (-not (Get-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -DisplayName $rule.Name -Direction Inbound -Action Allow `
                -Protocol TCP -LocalPort $rule.Port -Profile Any | Out-Null
        }
    }
}

Pop-Location

Say "challenge is up"
Write-Host ""
Write-Host "  key      : $Key"
Write-Host "  category : $Category"
Write-Host "  target   : http://$HostIp`:$HostPort"
Write-Host "  source   : http://$HostIp`:8899/source/$Key.zip"
Write-Host "  sha256   : $FlagSha"
Write-Host ""
Write-Host "  In the VM:"
Write-Host "    python3 tools/lab_sync.py --targets http://$HostIp`:8899/lab_targets.json --list"
Write-Host "    python3 tools/lab_sync.py --targets http://$HostIp`:8899/lab_targets.json --challenge $Key --fetch-source"
Write-Host ""
Write-Host "  Stop it later:"
Write-Host "    cd `"$ChallengePath`"; docker compose down -v"
