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
# LAYER 1: NLTK layer
# -----------------------------
LAYER1_NAME="nltk_layer"
LAYER1_DIR="$BASE_DIR/$LAYER1_NAME/python"
ZIP1_FILE="$BASE_DIR/$LAYER1_NAME.zip"
REQ1_FILE="$BASE_DIR/nltk_requirements.txt"

echo "🔄 Cleaning NLTK layer..."
rm -rf "$LAYER1_DIR" "$ZIP1_FILE"
mkdir -p "$LAYER1_DIR"

echo "📦 Installing NLTK dependencies from $REQ1_FILE..."
pip install --upgrade pip
pip install -r "$REQ1_FILE" -t "$LAYER1_DIR"

echo "📚 Downloading NLTK corpora..."
export NLTK_DATA="$LAYER1_DIR/nltk_data"
mkdir -p "$NLTK_DATA"

python3 -c "
import nltk
nltk.download('punkt', download_dir='$NLTK_DATA')
nltk.download('averaged_perceptron_tagger', download_dir='$NLTK_DATA')
"

zip_layer "$LAYER1_NAME"

# -----------------------------
# LAYER 2: spaCy layer
# -----------------------------
LAYER2_NAME="spacy_layer"
LAYER2_DIR="$BASE_DIR/$LAYER2_NAME/python"
ZIP2_FILE="$BASE_DIR/$LAYER2_NAME.zip"
REQ2_FILE="$BASE_DIR/spacy_requirements.txt"

echo "🔄 Cleaning spaCy layer..."
rm -rf "$LAYER2_DIR" "$ZIP2_FILE"
mkdir -p "$LAYER2_DIR"

echo "🚀 Installing spaCy + minimal dependencies into layer..."
pip install spacy==3.8.5 --target "$LAYER2_DIR" --no-cache-dir

echo "🗣️ Downloading en_core_web_sm model (globally)..."
python3 -m spacy download en_core_web_sm

echo "📂 Locating model path..."
MODEL_PATH=$(python3 -c "import en_core_web_sm; print(en_core_web_sm.__path__[0])")
echo "   Found model path at: $MODEL_PATH"

echo "📂 Copying model into Lambda layer directory..."
cp -r "$MODEL_PATH" "$LAYER2_DIR/"

echo "🧹 Cleaning unnecessary files inside the model (optional)..."
find "$LAYER2_DIR/en_core_web_sm" -type d -name "__pycache__" -exec rm -rf {} +
find "$LAYER2_DIR/en_core_web_sm" -type f -name "*.pyc" -delete

echo "🧽 Cleaning up global installation of model (optional)..."
python3 -m spacy validate
pip uninstall en-core-web-sm
rm -rf "$MODEL_PATH"

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
find $LAYER2_DIR -type f -name "*.py" -delete

echo "🧹 Removing all languages except English..."
find $LAYER2_DIR/spacy/lang/ -mindepth 1 ! -name "en" -exec rm -rf {} +

echo "🧹 Removing training/config files..."
rm -rf $LAYER2_DIR/spacy/tests
rm -rf $LAYER2_DIR/spacy/schemas
rm -rf $LAYER2_DIR/spacy/training
rm -rf $LAYER2_DIR/spacy/pipeline/trainable_pipe.pyc # if it exists
echo "🧹 Removing numpy docs and tests (huge)..."
rm -rf "$LAYER2_DIR/numpy/tests"
rm -rf "$LAYER2_DIR/numpy/doc"

echo "🧹 Removing tokenizer exceptions for unused languages..."
#rm -rf $LAYER2_DIR/spacy/lang/*/lemmatizer
#rm -rf $LAYER2_DIR/spacy/lang/*/tokenizer_exceptions.pyc

echo "🧹 Removing additional non-essential metadata files..."
#find $LAYER2_DIR -type d -name "*.egg-info" -exec rm -rf {} +
find $LAYER2_DIR -type f -name "*.so.debug" -delete

zip_layer "$LAYER2_NAME"

# -----------------------------
# LAYER 3: Other dependencies layer (TextBlob + Requests + Boto3)
# -----------------------------
LAYER3_NAME="other_layer"
LAYER3_DIR="$BASE_DIR/$LAYER3_NAME/python"
ZIP3_FILE="$BASE_DIR/$LAYER3_NAME.zip"
REQ3_FILE="$BASE_DIR/other_requirements.txt"

echo "🔄 Cleaning other layer..."
rm -rf "$LAYER3_DIR" "$ZIP3_FILE"
mkdir -p "$LAYER3_DIR"

echo "📦 Installing other dependencies from $REQ3_FILE..."
pip install -r "$REQ3_FILE" -t "$LAYER3_DIR"

zip_layer "$LAYER3_NAME"

# -----------------------------
# ✅ DONE
# -----------------------------

echo "✅ Lambda layers built successfully:"
echo " - $ZIP1_FILE"
echo " - $ZIP2_FILE"
echo " - $ZIP3_FILE"
