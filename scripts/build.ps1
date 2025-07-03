# build.ps1: Builds the frontend application.

Write-Host "Navigating to frontend project directory..."
Set-Location -Path (Resolve-Path (Join-Path $PSScriptRoot "../Project Information/v0"))

Write-Host "Building project with npm..."
npm run build

Write-Host "Build complete." 