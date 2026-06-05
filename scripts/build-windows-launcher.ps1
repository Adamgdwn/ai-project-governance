$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SourcePath = Join-Path $RepoRoot "windows/NewBuildGovernanceAgentLauncher.cs"
$DistRoot = Join-Path $RepoRoot "dist"
$WindowsDist = Join-Path $DistRoot "windows"
$ExePath = Join-Path $WindowsDist "NewBuildGovernanceAgent.exe"
$PackageRoot = Join-Path $DistRoot "NewBuildGovernanceAgent-Windows"
$PackageZip = Join-Path $DistRoot "NewBuildGovernanceAgent-Windows.zip"

function Get-CSharpCompiler {
    $candidates = @(
        (Join-Path $env:WINDIR "Microsoft.NET\Framework64\v4.0.30319\csc.exe"),
        (Join-Path $env:WINDIR "Microsoft.NET\Framework\v4.0.30319\csc.exe")
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    $fromPath = Get-Command csc.exe -ErrorAction SilentlyContinue
    if ($fromPath) {
        return $fromPath.Source
    }

    throw "Unable to find csc.exe. Run this script on Windows with .NET Framework build tools available."
}

function Copy-TrackedFiles {
    param([string]$TargetRoot)

    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) {
        throw "git is required to build the Windows package from tracked repository files."
    }

    $files = & $git.Source -C $RepoRoot ls-files
    if ($LASTEXITCODE -ne 0 -or -not $files) {
        throw "Unable to list tracked files for Windows package."
    }

    foreach ($file in $files) {
        if ($file -like "dist/*") {
            continue
        }

        $source = Join-Path $RepoRoot $file
        $target = Join-Path $TargetRoot $file
        $targetDir = Split-Path -Parent $target
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
        Copy-Item -Path $source -Destination $target -Force
    }
}

if (-not (Test-Path $SourcePath)) {
    throw "Missing launcher source: $SourcePath"
}

New-Item -ItemType Directory -Force -Path $WindowsDist | Out-Null

$csc = Get-CSharpCompiler
& $csc `
    "/nologo" `
    "/target:winexe" `
    "/optimize+" `
    "/reference:System.Windows.Forms.dll" `
    "/reference:System.Drawing.dll" `
    "/out:$ExePath" `
    $SourcePath

if ($LASTEXITCODE -ne 0) {
    throw "Windows launcher compilation failed."
}

if (-not (Test-Path $ExePath)) {
    throw "Expected launcher executable was not created: $ExePath"
}

Remove-Item -Recurse -Force -Path $PackageRoot -ErrorAction SilentlyContinue
Remove-Item -Force -Path $PackageZip -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $PackageRoot | Out-Null

Copy-TrackedFiles -TargetRoot $PackageRoot
Copy-Item -Path $ExePath -Destination (Join-Path $PackageRoot "NewBuildGovernanceAgent.exe") -Force

Compress-Archive -Path (Join-Path $PackageRoot "*") -DestinationPath $PackageZip -Force

Write-Host "PASS: Built $ExePath"
Write-Host "PASS: Packaged $PackageZip"
