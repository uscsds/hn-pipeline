#!/bin/bash
set -e

cd $(dirname $0)
rm -rf venv package lambda.zip
python3 -m venv venv
source venv/bin/activate
pip install boto3 -t package
cp lambda_function.py package/
cd package
zip -r ../lambda.zip .