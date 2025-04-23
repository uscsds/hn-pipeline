provider "aws" {
  region = "us-east-1"  # or your preferred region
}

module "hn_lambda" {
  source = "./lambda"  # Reference this directory/module
}

module "hn_lambda_clean" {
  source = "./lambda/clean_hn_data"  # Reference this directory/module

  lambda_artifact_bucket = aws_s3_bucket.lambda_artifacts.bucket
  clean_lambda_zip_key   = "lambda/clean_hn_data/lambda.zip"
}

resource "aws_s3_bucket" "lambda_artifacts" {
  bucket = "my-hn-lambda-artifacts-123456"
  force_destroy = true  # Optional: allows full cleanup
}