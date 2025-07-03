#!/bin/bash
# lint.sh: Runs the linter on the frontend application.

set -e

echo "Navigating to frontend project directory..."
cd "$(dirname "$0")/../Project Information/v0"

echo "Running linter with pnpm..."
pnpm lint

echo "Linting complete." 