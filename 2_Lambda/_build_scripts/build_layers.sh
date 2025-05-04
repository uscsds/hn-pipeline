#!/bin/bash

set -e

BASE_DIR="../terraform/shared_layer"

# Helper function to zip layer
zip_layer() {
  local layer_name="$1"
  cd "$BASE_DIR"
  echo "🗜️ Zipping $layer_name layer..."
  zip -r9 "${layer_name}.zip" "${layer_name}" > /dev/null
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

echo "📦 Installing spaCy dependencies from $REQ2_FILE..."
# Install spaCy and only core dependencies
pip install \
    -r "$REQ2_FILE" \
    --target $LAYER2_DIR \
    --no-cache-dir \
    --no-deps

#echo "📚 Downloading spaCy language model (en_core_web_sm)..."
#pip install https://github.com/explosion/spacy-models/releases/download/   -3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl --target "$LAYER2_DIR"

# Install minimal required deps explicitly (to avoid extra junk)
pip install \
    cymem \
    murmurhash \
    preshed \
    blis \
    thinc \
    numpy \
    wasabi \
    srsly \
    tqdm \
    catalogue \
    typer \
    langcodes \
    spacy-legacy \
    pydantic \
    requests \
    --target $LAYER2_DIR \
    --no-cache-dir

echo "🗣️ Downloading en_core_web_sm model..."
# Download and install model directly into the same target dir
python3 -m spacy download en_core_web_sm --direct --target $LAYER2_DIR


echo "🧹 Cleaning unnecessary files..."
# Remove tests, examples, .pyc, __pycache__, dist-info metadata (optional)
find $LAYER2_DIR -type d -name "tests" -exec rm -rf {} +
find $LAYER2_DIR -type d -name "__pycache__" -exec rm -rf {} +
find $LAYER2_DIR -type f -name "*.pyc" -delete
find $LAYER2_DIR -type d -name "examples" -exec rm -rf {} +
find $LAYER2_DIR -type d -name "demo*" -exec rm -rf {} +

# (Optional but recommended) Remove *.dist-info METADATA junk (~reduces 5-10MB)
find $LAYER2_DIR -type d -name "*.dist-info" -exec rm -rf {} +

# Remove unnecessary compiled binaries (like .libs)
find $LAYER2_DIR -type d -name "*.libs" -exec rm -rf {} +

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
