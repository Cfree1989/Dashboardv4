#!/bin/bash
# build.sh: Builds the frontend application.

set -e

echo "Navigating to frontend project directory..."
cd "$(dirname "$0")/../Project Information/v0"

echo "Building project with pnpm..."
pnpm build

echo "Build complete." 