provider "aws" {
  region = "us-east-1"  # or your preferred region
}

module "clean_hn_data_lambda" {
  source        = "./modules/lambda_function"
  function_name = "clean_hn_data"
  handler       = "lambda_function.lambda_handler"
  source_path   = "${path.module}/clean_hn_data/lambda.zip"
  s3_key        = "lambda/clean_hn_data/lambda.zip"
  env_variables = {
    RAW_BUCKET   = var.raw_bucket
    CLEAN_BUCKET = var.cleaned_bucket
    STATE_BUCKET = var.state_bucket
    RAW_KEY_PREFIX    = "raw/hn_top_raw"
    CLEAN_KEY_PREFIX    = "cleaned/hn_top_cleaned"
    STATE_FILE    = "state/global_seen_ids.json"
    NLTK_DATA = "/opt/python/nltk_data"
  }
}

module "process_hn_data_lambda" {
  source        = "./modules/lambda_function"
  function_name = "process_hn_data"
  handler       = "lambda_function.lambda_handler"
  source_path   = "${path.module}/process_hn_data/lambda.zip"
  s3_key        = "lambda/process_hn_data/lambda.zip"
  env_variables = {
    CLEAN_BUCKET     = var.cleaned_bucket
    PROCESSED_BUCKET = var.processed_bucket
    STATE_BUCKET = var.state_bucket
    CLEAN_KEY_PREFIX        = "cleaned/hn_top_cleaned"
    PROCESSED_KEY_PREFIX    = "processed/hn_top_processed"
    STATE_FILE    = "state/global_seen_ids.json"
    SUMMARY_STATE_FILE = "state/processed_files.json"
  }
}

module "fetch_hn_data_lambda" {
  source        = "./modules/lambda_function"
  function_name = "fetch_hn_data"
  handler       = "lambda_function.lambda_handler"
  source_path   = "${path.module}/fetch_hn_data/lambda.zip"
  s3_key        = "lambda/fetch_hn_data/lambda.zip"
  env_variables = {
    RAW_BUCKET = var.raw_bucket
    RAW_KEY_PREFIX    = "raw/hn_top_raw"
  }
}

# Shared resources (used by module)
resource "aws_iam_role" "lambda_exec" {
  name = "lambda-hn-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = { Service = "lambda.amazonaws.com" },
      Effect = "Allow",
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_s3_bucket" "lambda_artifacts" {
  bucket        = "my-lambda-artifacts-123456"
  force_destroy = true
}

resource "aws_cloudwatch_event_rule" "trigger_fetch_hn" {
  name                = "fetch-hn-data-schedule"
  description         = "Scheduled trigger for fetch_hn_data Lambda"
  schedule_expression = "rate(15 minutes)"
}

resource "aws_cloudwatch_event_target" "fetch_hn_lambda" {
  rule      = aws_cloudwatch_event_rule.trigger_fetch_hn.name
  target_id = "fetchHnLambda"
  arn       = module.fetch_hn_data_lambda.this_lambda_arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_fetch" {
  statement_id  = "AllowCloudWatchInvokeFetch"
  action        = "lambda:InvokeFunction"
  function_name = module.fetch_hn_data_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trigger_fetch_hn.arn
}

resource "aws_s3_bucket_notification" "trigger_clean_lambda" {
  bucket = var.raw_bucket

  lambda_function {
    lambda_function_arn = module.clean_hn_data_lambda.this_lambda_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/hn_top_raw"
  }
}

resource "aws_lambda_permission" "allow_s3_to_invoke_clean" {
  statement_id  = "AllowS3InvokeClean"
  action        = "lambda:InvokeFunction"
  function_name = module.clean_hn_data_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.raw_bucket.arn
}

resource "aws_s3_bucket_notification" "trigger_process_lambda" {
  bucket = var.cleaned_bucket

  lambda_function {
    lambda_function_arn = module.process_hn_data_lambda.this_lambda_arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "cleaned/hn_top_cleaned"
  }
}

resource "aws_lambda_permission" "allow_s3_to_invoke_process" {
  statement_id  = "AllowS3InvokeProcess"
  action        = "lambda:InvokeFunction"
  function_name = module.process_hn_data_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.cleaned_bucket.arn
}


