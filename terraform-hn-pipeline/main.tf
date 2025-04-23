provider "aws" {
  region = "us-east-1"  # or your preferred region
}

module "hn_lambda" {
  source = "./lambda"  # Reference this directory/module
}

module "hn_lambda_clean" {
  source = "./lambda/clean_hn_data"  # Reference this directory/module
}
