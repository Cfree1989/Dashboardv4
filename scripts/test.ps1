# test.ps1: Runs the test suite for the frontend application.

Write-Host "Navigating to frontend project directory..."
Set-Location -Path (Resolve-Path (Join-Path $PSScriptRoot "../Project Information/v0"))

Write-Host "Running tests with npm..."
npm test

Write-Host "Test script finished." 