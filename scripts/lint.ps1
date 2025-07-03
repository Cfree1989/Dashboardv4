# lint.ps1: Runs the linter on the frontend application.

Write-Host "Navigating to frontend project directory..."
Set-Location -Path (Resolve-Path (Join-Path $PSScriptRoot "../Project Information/v0"))

Write-Host "Running linter with pnpm..."
pnpm lint

Write-Host "Linting complete." 