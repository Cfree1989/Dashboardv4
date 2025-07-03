#!/bin/bash
# test.sh: Runs the test suite for the frontend application.

set -e

echo "Navigating to frontend project directory..."
cd "$(dirname "$0")/../Project Information/v0"

echo "Running tests with pnpm..."
echo "NOTE: 'test' script is not yet defined in package.json."
# pnpm test

echo "Test script finished." 