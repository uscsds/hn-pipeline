provider "aws" {
  region = "us-east-1"  # or your preferred region
}

module "hn_lambda" {
  source = "./lambda"  # Reference this directory/module

  raw_data_bucket_name = aws_s3_bucket.hn_raw.bucket
}
