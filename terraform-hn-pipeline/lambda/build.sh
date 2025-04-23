#!/bin/bash

echo "Packaging Lambda..."

# Remove old build
rm -rf lambda/venv lambda/package lambda/lambda.zip
python3 -m venv lambda/venv
source lambda/venv/bin/activate

# Create build directory
mkdir -p lambda/package
cp lambda/lambda_function.py lambda/package/

# Install dependencies into build folder
pip install --target lambda/package/ -r requirements.txt

# Zip everything
cd lambda/package
zip -r9 ../lambda.zip .
cd ..
