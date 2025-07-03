#!/bin/bash
# dev-setup.sh: Installs frontend dependencies.

set -e # Exit immediately if a command exits with a non-zero status.

echo "Navigating to frontend project directory..."
cd "$(dirname "$0")/../Project Information/v0"

echo "Installing dependencies with pnpm..."
pnpm install

echo "Development setup complete." 