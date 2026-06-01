$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Get-PythonCommand {
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
            & $exe @prefix -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)" *> $null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {
            continue
        }
    }

    throw "Unable to find Python 3.8 or newer."
}

function Invoke-Python {
    param(
        [string[]]$PythonCommand,
        [string[]]$Arguments
    )

    $exe = $PythonCommand[0]
    $prefix = @()
    if ($PythonCommand.Count -gt 1) {
        $prefix = $PythonCommand[1..($PythonCommand.Count - 1)]
    }
    & $exe @prefix @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Arguments -join ' ')"
    }
}

function Test-RequiredFile {
    param([string]$RelativePath)

    $path = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path $path)) {
        throw "Missing required file: $RelativePath"
    }
    Write-Host "PASS: Found $RelativePath"
}

$requiredFiles = @(
    "README.md",
    "START_HERE.md",
    "project-control.yaml",
    "docs/architecture.md",
    "docs/current-build-pathway.md",
    "docs/manual.md",
    "docs/roadmap.md",
    "docs/policy/durable-development-engineering-policy.md",
    "docs/standards/engineering-governance-by-use-case.md",
    "docs/risks/risk-register.md",
    "docs/deployment-guide.md",
    "docs/runbook.md",
    "AGENTS.md"
)

foreach ($file in $requiredFiles) {
    Test-RequiredFile $file
}

$python = Get-PythonCommand
Invoke-Python -PythonCommand $python -Arguments @((Join-Path $RepoRoot "automation/schema_validation.py"), "--project", $RepoRoot)

$pythonFiles = Get-ChildItem -Path (Join-Path $RepoRoot "automation") -Filter "*.py" -File | Sort-Object FullName
foreach ($file in $pythonFiles) {
    Invoke-Python -PythonCommand $python -Arguments @("-m", "py_compile", $file.FullName)
}

$psFiles = @(
    Get-ChildItem -Path (Join-Path $RepoRoot "automation") -Filter "*.ps1" -File
    Get-ChildItem -Path (Join-Path $RepoRoot "scripts") -Filter "*.ps1" -File
) | Sort-Object FullName
foreach ($file in $psFiles) {
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count -gt 0) {
        throw "PowerShell syntax failed for $($file.FullName): $($errors[0].Message)"
    }
}
Write-Host "PASS: PowerShell syntax"

$bash = Get-Command bash -ErrorAction SilentlyContinue
if ($bash) {
    $shellFiles = @(
        Get-ChildItem -Path (Join-Path $RepoRoot "automation") -Filter "*.sh" -File
        Get-ChildItem -Path (Join-Path $RepoRoot "scripts") -Filter "*.sh" -File
        Get-ChildItem -Path (Join-Path $RepoRoot "templates/project/scripts") -Filter "*.sh" -File
    ) | Sort-Object FullName
    foreach ($file in $shellFiles) {
        & $bash.Source -n $file.FullName
        if ($LASTEXITCODE -ne 0) {
            throw "Shell syntax failed for $($file.FullName)"
        }
    }
    Write-Host "PASS: Shell syntax"
} else {
    Write-Host "SKIP: Shell syntax check requires bash."
}

Invoke-Python -PythonCommand $python -Arguments @("-m", "unittest", "discover", "-s", (Join-Path $RepoRoot "tests"), "-p", "test_*.py")
Write-Host "Validation complete."
