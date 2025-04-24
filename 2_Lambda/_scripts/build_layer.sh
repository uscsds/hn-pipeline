#!/bin/bash

set -e

LAYER_DIR="../terraform/shared_layer"
PYTHON_DIR="$LAYER_DIR/python"
ZIP_FILE="$LAYER_DIR/python_layer.zip"
REQUIREMENTS="$LAYER_DIR/requirements.txt"

echo "🔄 Cleaning previous layer..."
rm -rf "$PYTHON_DIR" "$ZIP_FILE"
mkdir -p "$PYTHON_DIR"

echo "📦 Installing dependencies into layer..."
pip install -r "$REQUIREMENTS" -t "$PYTHON_DIR"

echo "🗜️ Zipping layer..."
cd "$LAYER_DIR"
zip -r9 python_layer.zip python > /dev/null
cd -

echo "✅ Lambda layer built successfully: $ZIP_FILE"
