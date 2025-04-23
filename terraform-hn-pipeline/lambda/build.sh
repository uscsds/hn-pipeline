#!/bin/bash

set -e

echo "Packaging Lambda..."

LAMBDA_DIR=$(dirname "$0")
cd "$LAMBDA_DIR"

rm -f lambda.zip
rm -rf python

# Install dependencies
python3 -m venv venv
source venv/bin/activate
mkdir -p python
pip install -r requirements.txt -t python/

# Zip the code
zip -r lambda.zip lambda_function.py python/
deactivate

echo "Lambda packaged: lambda.zip"
