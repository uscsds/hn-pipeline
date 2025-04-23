#!/bin/bash
set -e

cd $(dirname $0)
rm -rf venv package lambda.zip
python3 -m venv venv
source venv/bin/activate
# Install dependencies into build folder
pip install --target package/ -r requirements.txt
cp lambda_function.py package/
cd package
zip -r ../lambda.zip .
cd ..
aws s3 cp lambda.zip s3://my-hn-lambda-artifacts-123456/lambda/clean_hn_data/lambda.zip