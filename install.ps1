# zed-wpilib installer for Windows. Teammates run this in PowerShell:
#   irm https://raw.githubusercontent.com/radiobone/zed-wpilib/main/install.ps1 | iex
# Running it again updates. From a clone you can also run:  powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = 'Stop'

$Repo   = if ($env:ZED_WPILIB_REPO)   { $env:ZED_WPILIB_REPO }   else { 'https://github.com/radiobone/zed-wpilib' }
$Branch = if ($env:ZED_WPILIB_BRANCH) { $env:ZED_WPILIB_BRANCH } else { 'main' }
$Dest   = if ($env:ZED_WPILIB_DIR)    { $env:ZED_WPILIB_DIR }    else { Join-Path $env:LOCALAPPDATA 'zed-wpilib\app' }

function Find-Python {
    # Returns the full path of a Python 3.9+ interpreter, or $null.
    $candidates = @(@('py', '-3'), @('python'), @('python3'))
    foreach ($c in $candidates) {
        if (-not (Get-Command $c[0] -ErrorAction SilentlyContinue)) { continue }
        $rest = @($c | Select-Object -Skip 1)
        try {
            $exe = & $c[0] @rest -c "import sys; print(sys.executable) if sys.version_info >= (3, 9) else sys.exit(1)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $exe) { return $exe.Trim() }
        } catch { }
    }
    return $null
}

function Update-SessionPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
}

$py = Find-Python
if (-not $py) {
    Write-Host 'zed-wpilib needs Python 3.9 or newer, and it is not installed.'
    $answer = Read-Host 'Install Python now with winget? (Y/n)'
    if ($answer -match '^(n|no)$') { Write-Host 'Install Python from https://www.python.org/downloads/ and run this again.'; return }
    winget install -e --id Python.Python.3.13 --scope user --accept-package-agreements --accept-source-agreements
    Update-SessionPath
    $py = Find-Python
    if (-not $py) { Write-Host 'Python still was not found. Close this window, open a new PowerShell, and run the installer again.'; return }
}

# Running from a checkout? Install from it directly.
$here = if ($PSScriptRoot) { $PSScriptRoot } else { $null }
if ($here -and (Test-Path (Join-Path $here 'install.py')) -and (Test-Path (Join-Path $here 'bin\wpilib'))) {
    & $py (Join-Path $here 'install.py') @args
    return
}

if (Test-Path (Join-Path $Dest '.git')) {
    Write-Host "Updating $Dest"
    git -C $Dest pull --ff-only
} elseif ((Get-Command git -ErrorAction SilentlyContinue) -and -not (Test-Path $Dest)) {
    Write-Host "Downloading zed-wpilib to $Dest"
    git clone --depth 1 --branch $Branch $Repo $Dest
} else {
    Write-Host "Downloading zed-wpilib to $Dest"
    $zip = Join-Path $env:TEMP 'zed-wpilib.zip'
    $tmp = Join-Path $env:TEMP ('zed-wpilib-' + [guid]::NewGuid())
    Invoke-WebRequest -UseBasicParsing "$Repo/archive/refs/heads/$Branch.zip" -OutFile $zip
    Expand-Archive $zip $tmp -Force
    $inner = Get-ChildItem $tmp | Select-Object -First 1
    New-Item -ItemType Directory -Force $Dest | Out-Null
    Copy-Item (Join-Path $inner.FullName '*') $Dest -Recurse -Force
    Remove-Item $zip, $tmp -Recurse -Force
}

& $py (Join-Path $Dest 'install.py')
