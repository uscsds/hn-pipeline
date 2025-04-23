#!/bin/bash

echo "Packaging Lambda..."

# Remove old build
rm -rf venv package lambda.zip
python3 -m venv venv
source venv/bin/activate

# Create build directory
mkdir -p package
cp lambda_function.py package/

# Install dependencies into build folder
pip install --target package/ -r requirements.txt

# Zip everything
cd package
zip -r9 ../lambda.zip .
cd ..
