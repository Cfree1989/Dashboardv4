# dev-setup.ps1: Installs frontend dependencies.

Write-Host "Navigating to frontend project directory..."
Set-Location -Path (Resolve-Path (Join-Path $PSScriptRoot "../Project Information/v0"))

Write-Host "Installing dependencies with pnpm..."
pnpm install

Write-Host "Development setup complete." 