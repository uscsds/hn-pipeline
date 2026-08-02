#!/bin/bash

set -e

BASE_DIR="../terraform/shared_layer"

# Helper function to zip layer
zip_layer() {
  local layer_name="$1"
  cd "${BASE_DIR}/${layer_name}"
  echo "🗜️ Zipping $layer_name layer..."
  zip -r9 "${layer_name}.zip" "python" > /dev/null
  cd -
}

# -----------------------------
# LAYER 2: spaCy layer (Python 3.11)
# -----------------------------
LAYER2_NAME="spacy_layer"
LAYER2_DIR="$BASE_DIR/$LAYER2_NAME/python"
ZIP2_FILE="$BASE_DIR/$LAYER2_NAME.zip"
REQ2_FILE="$BASE_DIR/spacy_requirements.txt"

echo "🔄 Cleaning spaCy layer..."
rm -rf "$LAYER2_DIR" "$ZIP2_FILE"
mkdir -p "$LAYER2_DIR"

echo "🚀 Installing spaCy into layer (Python 3.11)..."
pip3.11 install spacy==3.8.5 --target "$LAYER2_DIR" --no-cache-dir

echo "🗣️ Installing en_core_web_sm model wheel into layer..."
pip3.11 install "en_core_web_sm-3.8.0-py3-none-any.whl" --target "$LAYER2_DIR" --no-deps

echo "✅ spaCy + model installed directly into layer!"

echo "🧹 Cleaning unnecessary files inside the model (optional)..."
find "$LAYER2_DIR/en_core_web_sm" -type d -name "__pycache__" -exec rm -rf {} +
find "$LAYER2_DIR/en_core_web_sm" -type f -name "*.pyc" -delete

echo "🧽 Cleaning up global installation of model (optional)..."
python3.11 -m spacy validate
pip3.11 uninstall -y en-core-web-sm || true

echo "✅ Model copied and global clutter removed!"

echo "🧹 Cleaning unnecessary files to reduce size..."
find "$LAYER2_DIR" -type d -name "tests" -exec rm -rf {} + || true
find "$LAYER2_DIR" -type d -name "__pycache__" -exec rm -rf {} + || true
find "$LAYER2_DIR" -type f -name "*.pyc" -delete || true
find "$LAYER2_DIR" -type d -name "examples" -exec rm -rf {} + || true
find "$LAYER2_DIR" -type d -name "demo*" -exec rm -rf {} + || true

# Remove .dist-info and .egg-info (reduces 10–20MB safely)
find "$LAYER2_DIR" -type d -name "*.dist-info" -exec rm -rf {} + || true
find "$LAYER2_DIR" -type d -name "*.egg-info" -exec rm -rf {} + || true

# Optional: Remove unused binaries (like BLAS/OpenMP libs spaCy won’t use in Lambda)
find "$LAYER2_DIR" -type d -name ".libs" -exec rm -rf {} + || true

# Strip large binaries (removes debug symbols; safe for Lambda)
find "$LAYER2_DIR" -type f -name "*.so" -exec strip --strip-unneeded {} + || true

echo "🧹 Removing .py source files (optional)..."
find "$LAYER2_DIR" -type f -name "*.py" -delete

echo "🧹 Removing all languages except English..."
find "$LAYER2_DIR/spacy/lang/" -mindepth 1 ! -name "en" -exec rm -rf {} +

echo "🧹 Removing training/config files..."
rm -rf "$LAYER2_DIR/spacy/tests"
rm -rf "$LAYER2_DIR/spacy/schemas"
rm -rf "$LAYER2_DIR/spacy/training"
rm -f "$LAYER2_DIR/spacy/pipeline/trainable_pipe.pyc" || true

echo "🧹 Removing numpy docs and tests (huge)..."
rm -rf "$LAYER2_DIR/numpy/tests"
rm -rf "$LAYER2_DIR/numpy/doc"

echo "🧹 Removing additional non-essential metadata files..."
find "$LAYER2_DIR" -type f -name "*.so.debug" -delete

zip_layer "$LAYER2_NAME"
