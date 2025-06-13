#!/usr/bin/env bash
# This script is used to build email templates from MJML to HTML.

set -e # Exit immediately if a command exits with a non-zero status
# set -x # Print each command before executing it

SRC_DIR="app/infrastructure/templates/mjml"
BUILD_DIR="app/infrastructure/templates/html"

mkdir -p "$BUILD_DIR"

echo "📤 Compilation MJML → HTML"
mjml "$SRC_DIR"/*.mjml -o "$BUILD_DIR"
echo "📤 Compilation MJML → HTML done!"

tree "$BUILD_DIR" -P "*.html" --dirsfirst --noreport