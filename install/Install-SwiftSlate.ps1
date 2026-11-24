<#
  SwiftSlate Desktop: manuelle Installation ohne "irm | iex"
  SHA256-gepruefter Download vom Release-Tag.
  Ohne Adminrechte ausfuehren. Idempotent: mehrfach ausfuehren ist sicher.

  Beispiele:
    .\Install-SwiftSlate.ps1 -Endpoint https://chat-ai.academiccloud.de/v1 -Model deepseek-v4.1-flash-1017 -SetKey
    .\Install-SwiftSlate.ps1 -Endpoint http://localhost:11434/v1 -Model gemma3:12b
    .\Install-SwiftSlate.ps1 -SetKey                   # nur den Key neu setzen
    .\Install-SwiftSlate.ps1 -ResetConfig              # config.json neu schreiben
    .\Install-SwiftSlate.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [ValidateSet('custom','gemini','groq')] [string]$Provider = 'custom',
    [string]$Endpoint,
    [string]$Model,
    [switch]$SetKey,
    [switch]$ResetConfig,
    [switch]$ResetCommands,
    [switch]$NoAutostart,
    [switch]$NoStart,
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

# --- Feste Werte ---
$Repo    = 'codingismynewgaming/SwiftSlate-Desktop'
$Release = 'v1.0.0'
$RawBase = "https://raw.githubusercontent.com/$Repo/$Release"
$Hashes  = @{
    "SwiftSlate.pyw"  = "129D27AEBF0D207F984A1FD955B2FD8CAA18EF90CE300B3E8A3D4C213645C894"
    "commands.json"   = "CE38B3C4B48B56BA40B8BD23C58AE873C3B29D78BD8319FA96CEBB923A478E9A"
    "assets/icon.ico" = "31DC7128E226247F97605E8EB88D08ECDB549A516F4EED8EF17AA252BE20200A"
}

$Base      = Join-Path $env:LOCALAPPDATA 'SwiftSlate'
$AppDir    = Join-Path $Base 'app'
$AssetsDir = Join-Path $AppDir 'assets'
$VenvDir   = Join-Path $Base 'venv'
$Pyw       = Join-Path $AppDir 'SwiftSlate.pyw'
$CfgPath   = Join-Path $AppDir 'config.json'
$CmdPath   = Join-Path $AppDir 'commands.json'
$Lnk       = Join-Path ([Environment]::GetFolderPath('Startup')) 'SwiftSlate.lnk'
$Utf8      = New-Object System.Text.UTF8Encoding($false)

function Stop-SwiftSlate {
    Get-CimInstance Win32_Process -EA SilentlyContinue |
        Where-Object { $_.CommandLine -like "*$AppDir\SwiftSlate.pyw*" } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue; Wait-Process -Id $_.ProcessId -Timeout 10 -EA SilentlyContinue }
}

function Protect-File([string]$Path) {
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    & icacls.exe $Path /inheritance:r /grant:r "*${sid}:(F)" "*S-1-5-18:(F)" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "icacls fehlgeschlagen fuer $Path" }
}

function Protect-Directory([string]$Path) {
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    & icacls.exe $Path /inheritance:r /grant:r "*${sid}:(OI)(CI)(F)" "*S-1-5-18:(OI)(CI)(F)" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "icacls fehlgeschlagen fuer $Path" }
}

function Get-Python {
    $cands = @()
    if (Get-Command py -EA SilentlyContinue) { $cands += ,@('py','-3') }
    if (Get-Command python -EA SilentlyContinue) { $cands += ,@('python') }
    $cands += ,@("$env:LOCALAPPDATA\Programs\Python\Python313\python.exe")
    foreach ($c in $cands) {
        try {
            $exe = $c[0]; $args0 = @($c | Select-Object -Skip 1)
            if (-not (Get-Command $exe -EA SilentlyContinue) -and -not (Test-Path $exe)) { continue }
            $v = & $exe @args0 -c "import sys;print('%d.%d'%sys.version_info[:2]);print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $v) {
                $mm = [version]$v[0]
                if ($mm -ge [version]'3.10' -and $v[1] -notlike '*WindowsApps*') { return $v[1] }
            }
        } catch { }
    }
    Write-Host 'Kein Python >= 3.10 gefunden. Installiere Python 3.13 per winget (Benutzerkontext)...'
    & winget install -e --id Python.Python.3.13 --scope user --silent --accept-package-agreements --accept-source-agreements
    $p = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    if (-not (Test-Path $p)) { throw 'Python Installation fehlgeschlagen. Bitte Python 3.13 von python.org (Benutzerinstallation) installieren und erneut starten.' }
    return $p
}

function Install-VerifiedFile([string]$RelPath, [string]$DestPath) {
    $expected = $Hashes[$RelPath]
    $needDl = $true
    if (Test-Path $DestPath) {
        $needDl = ((Get-FileHash $DestPath -Algorithm SHA256).Hash -ne $expected)
    }
    if (-not $needDl) {
        Write-Host "$RelPath aktuell (Hash ok)."
        return $false
    }
    $tmp = Join-Path $env:TEMP ("$(Split-Path $RelPath -Leaf).$PID")
    try {
        Invoke-WebRequest -Uri "$RawBase/$RelPath" -OutFile $tmp -UseBasicParsing -TimeoutSec 60
        $actual = (Get-FileHash $tmp -Algorithm SHA256).Hash
        if ($actual -ne $expected) {
            throw "Hash stimmt nicht fuer ${RelPath}: $actual (erwartet $expected)"
        }
        Move-Item $tmp $DestPath -Force
        Write-Host "$RelPath installiert (Hash ok)."
        return $true
    } finally {
        if (Test-Path $tmp) { Remove-Item $tmp -Force -EA SilentlyContinue }
    }
}

# --- Deinstallation ---
if ($Uninstall) {
    Stop-SwiftSlate
    Remove-Item $Lnk -Force -EA SilentlyContinue
    Remove-Item $Base -Recurse -Force -EA SilentlyContinue
    Write-Host "SwiftSlate entfernt ($Base, Autostart Verknuepfung)."
    return
}

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) { throw 'Bitte in einer normalen PowerShell ohne Adminrechte ausfuehren.' }

New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
New-Item -ItemType Directory -Force -Path $AssetsDir | Out-Null
Protect-Directory $AppDir

# --- 1) Python und venv ---
$py = Get-Python
& $py -c "import tkinter" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'Einstellungsfenster braucht tkinter (Python von python.org mit Tcl/Tk).'
}
$pythonw = Join-Path $VenvDir 'Scripts\pythonw.exe'
if (-not (Test-Path $pythonw)) {
    & $py -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { throw 'venv konnte nicht erstellt werden.' }
}

# --- 2) Programmdateien vom Release Tag laden und Hash pruefen ---
Stop-SwiftSlate
Install-VerifiedFile 'SwiftSlate.pyw' $Pyw | Out-Null
Install-VerifiedFile 'assets/icon.ico' (Join-Path $AssetsDir 'icon.ico') | Out-Null

# --- 3) commands.json (nur wenn fehlend oder -ResetCommands) ---
if ($ResetCommands -or -not (Test-Path $CmdPath)) {
    if (Test-Path $CmdPath) { Copy-Item $CmdPath "$CmdPath.bak" -Force }
    $tmpCmd = Join-Path $env:TEMP "commands.json.$PID"
    try {
        Invoke-WebRequest -Uri "$RawBase/commands.json" -OutFile $tmpCmd -UseBasicParsing -TimeoutSec 60
        $actual = (Get-FileHash $tmpCmd -Algorithm SHA256).Hash
        if ($actual -ne $Hashes['commands.json']) {
            throw "Hash stimmt nicht fuer commands.json: $actual"
        }
        Move-Item $tmpCmd $CmdPath -Force
        Write-Host 'commands.json installiert (Hash ok).'
    } finally {
        if (Test-Path $tmpCmd) { Remove-Item $tmpCmd -Force -EA SilentlyContinue }
    }
} else {
    Write-Host 'commands.json vorhanden, unveraendert.'
}

# --- 4) config.json ---
if ($ResetConfig -or $SetKey -or -not (Test-Path $CfgPath)) {
    $cfg = $null
    if ((Test-Path $CfgPath) -and -not $ResetConfig) {
        $cfg = Get-Content $CfgPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    $isNewCfg = (-not $cfg)
    if ($isNewCfg) {
        if ($Provider -eq 'custom') {
            if (-not $Endpoint) { $Endpoint = (Read-Host 'OpenAI-kompatibler Endpoint (leer lassen zum spaeteren Einrichten)').Trim() }
            if (-not $Model)    { $Model    = (Read-Host 'Modellname (leer lassen zum spaeteren Einrichten)').Trim() }
        }
        $cfg = [ordered]@{
            api_keys         = @()
            provider         = $Provider
            endpoint         = if ($Endpoint) { $Endpoint } else { '' }
            model            = if ($Model) { $Model } else { '' }
            temperature      = 0.3
            prefix           = '.'
            trigger_delay_ms = 1000
            key_delay        = 200
            spinner          = 'animated'
        }
    }
    if ($SetKey -or $isNewCfg) {
        $sec = Read-Host 'API Key (Eingabe bleibt unsichtbar, Enter fuer leer)' -AsSecureString
        $b = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
        try { $k = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($b) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b) }
        if ([string]::IsNullOrWhiteSpace($k)) {
            if ($isNewCfg) { $cfg.api_keys = @() }
        } else {
            $cfg.api_keys = @($k.Trim())
        }
        $k = $null
    }
    if (-not (Test-Path $CfgPath)) { New-Item -ItemType File -Path $CfgPath -Force | Out-Null }
    Protect-File $CfgPath
    [IO.File]::WriteAllText($CfgPath, ($cfg | ConvertTo-Json -Depth 3), $Utf8)
    $cfg = $null
    Write-Host "config.json geschrieben (nur fuer $env:USERNAME lesbar)."
} else {
    Protect-File $CfgPath
    Write-Host 'config.json vorhanden, unveraendert (ACL erneut gesetzt).'
}

# --- 5) Autostart per Verknuepfung im Benutzer Startup Ordner ---
if ($NoAutostart) {
    Remove-Item $Lnk -Force -EA SilentlyContinue
} else {
    $sh = New-Object -ComObject WScript.Shell
    $sc = $sh.CreateShortcut($Lnk)
    $sc.TargetPath       = $pythonw
    $sc.Arguments        = "`"$Pyw`""
    $sc.WorkingDirectory = $AppDir
    $sc.Description      = 'SwiftSlate Desktop'
    $sc.Save()
    Write-Host "Autostart: $Lnk"
}

# --- 6) Starten ---
if (-not $NoStart) {
    Stop-SwiftSlate
    Start-Process -FilePath $pythonw -ArgumentList "`"$Pyw`"" -WorkingDirectory $AppDir
    Write-Host 'SwiftSlate laeuft (Tray Symbol). Test: in Notepad "ich hab das vergesen .fix" tippen und 1 Sekunde warten.'
}
