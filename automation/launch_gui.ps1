$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$GuiScript = Join-Path $RepoRoot "automation/new_build_gui.py"
$LogDir = Join-Path $RepoRoot "data/new-build-agent/logs"
$LogPath = Join-Path $LogDir "gui-launch-windows.log"

function Get-PythonWithTk {
    $candidates = @(
        @("py", "-3"),
        @("python"),
        @("python3")
    )

    foreach ($candidate in $candidates) {
        try {
            $exe = $candidate[0]
            $prefix = @()
            if ($candidate.Count -gt 1) {
                $prefix = $candidate[1..($candidate.Count - 1)]
            }
            & $exe @prefix -c "import sys, tkinter; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)" *> $null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {
            continue
        }
    }

    throw "Unable to find Python 3.8 or newer with tkinter. Install Python from python.org and include Tcl/Tk support."
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$env:GOVERNANCE_HOME = $RepoRoot

$python = Get-PythonWithTk
$pythonExe = $python[0]
$pythonPrefix = @()
if ($python.Count -gt 1) {
    $pythonPrefix = $python[1..($python.Count - 1)]
}

try {
    & $pythonExe @pythonPrefix $GuiScript *> $LogPath
    exit $LASTEXITCODE
} catch {
    $_ | Out-File -FilePath $LogPath -Append -Encoding utf8
    throw
}
