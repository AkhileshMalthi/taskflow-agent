# Loads environment variables from .env file into the current PowerShell session
# Usage: . .\scripts\load_env.ps1

$envFile = ".env"
if (!(Test-Path $envFile)) {
    Write-Host ".env file not found at $envFile"
    exit 1
}

Get-Content $envFile | ForEach-Object {
    if ($_ -match '^(\w+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2].Trim('"')
        Set-Item -Path "Env:$name" -Value $value
    }
}
Write-Host "Loaded environment variables from $envFile"
