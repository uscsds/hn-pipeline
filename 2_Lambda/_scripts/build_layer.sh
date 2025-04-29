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
pip install --upgrade pip
pip install -r "$REQUIREMENTS" -t "$PYTHON_DIR"

echo "📚 Downloading NLTK corpora..."
# Set environment so nltk will download data into your layer
export NLTK_DATA="$PYTHON_DIR/nltk_data"
mkdir -p "$NLTK_DATA"

python3 -c "
import nltk
nltk.download('punkt', download_dir='$NLTK_DATA')
nltk.download('averaged_perceptron_tagger', download_dir='$NLTK_DATA')
"

echo "📚 Downloading spaCy language model..."
# Set environment variable so spaCy downloads model into the layer
export SPACY_DATA="$PYTHON_DIR/spacy_data"
mkdir -p "$SPACY_DATA"

# Install the small English model into the layer
python3 -m spacy download en_core_web_sm --direct --destination "$SPACY_DATA"

# Patch environment variables for runtime (if needed)
# You could also adjust your lambda to load it from SPACY_DATA

echo "🗜️ Zipping layer..."
cd "$LAYER_DIR"
zip -r9 python_layer.zip python > /dev/null
cd -

echo "✅ Lambda layer built successfully: $ZIP_FILE"
