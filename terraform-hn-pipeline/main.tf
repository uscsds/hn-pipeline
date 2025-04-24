provider "aws" {
  region = "us-east-1"  # or your preferred region
}

module "hn_lambda" {
  source = "./lambda"  # Reference this directory/module

  lambda_role_name = module.shared_lambda_role.role_name
  lambda_role_arn = module.shared_lambda_role.role_arn
}

module "hn_lambda_clean" {
  source = "./lambda/clean_hn_data"  # Reference this directory/module

  lambda_artifact_bucket = "my-hn-lambda-artifacts-123456"
  clean_lambda_zip_key   = "lambda/clean_hn_data/lambda.zip"

  lambda_role_name = module.shared_lambda_role.role_name
  lambda_role_arn = module.shared_lambda_role.role_arn
}

module "shared_lambda_role" {
  source    = "./shared/iam_role_lambda"
  role_name = "shared-lambda-role"
}
