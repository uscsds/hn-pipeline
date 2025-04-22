provider "aws" {
  region = "us-east-1"  # or your preferred region
}

module "hn_lambda" {
  source = "./lambda"  # Reference this directory/module
}
