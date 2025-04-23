variable "raw_data_bucket_name" {
  description = "Name of the raw data S3 bucket"
  type        = string
  default     = "hn-raw-data-123456"
}

variable "clean_data_bucket_name" {
  description = "Name of the raw data S3 bucket"
  type        = string
  default     = "hn-cleaned-data-123456"
}

variable "lambda_artifact_bucket" {
  description = "S3 bucket where lambda zip artifacts are stored"
  type        = string
}

variable "clean_lambda_zip_key" {
  description = "S3 key (path) for the clean lambda zip"
  type        = string
}

data "aws_iam_role" "existing_lambda_exec_role" {
  name = "lambda-hn-exec-role"  # The name of the existing IAM role
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = data.aws_iam_role.existing_lambda_exec_role.arn  # Reference the existing role ARN

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3_inline" {
  name = "lambda-s3-inline-policy"
  role = data.aws_iam_role.existing_lambda_exec_role.id  # Reference the existing role id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:PutObject"],
        Resource = ["arn:aws:s3:::${var.raw_data_bucket_name}/*","arn:aws:s3:::${var.clean_data_bucket_name}/*"]
      }
    ]
  })
}


resource "aws_lambda_function" "clean_hn_data" {
  function_name = "clean_hn_data"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  role          = data.aws_iam_role.existing_lambda_exec_role.arn  # Reference the existing role ARN

  s3_bucket = var.lambda_artifact_bucket
  s3_key    = var.clean_lambda_zip_key

  environment {
    variables = {
      RAW_BUCKET   = var.raw_data_bucket_name
      CLEAN_BUCKET = var.clean_data_bucket_name
      RAW_KEY      = "raw/hn_dump.json"
      CLEAN_KEY    = "cleaned/hn_cleaned.json"
    }
  }
}

resource "aws_s3_bucket_notification" "trigger_clean_lambda" {
  bucket = var.raw_data_bucket_name

  lambda_function {
    lambda_function_arn = aws_lambda_function.clean_hn_data.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/hn_dump.json"
  }

  depends_on = [
    aws_lambda_permission.allow_s3_trigger_clean
  ]
}

resource "aws_lambda_permission" "allow_cloudwatch_clean" {
  statement_id  = "AllowExecutionFromCloudWatchClean"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.clean_hn_data.function_name
  principal     = "events.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.raw_data_bucket_name}"  # Correct ARN for S3 bucket
}

resource "aws_lambda_permission" "allow_s3_trigger_clean" {
  statement_id  = "AllowS3InvokeClean"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.clean_hn_data.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.raw_data_bucket_name}"  # Correct ARN for S3 bucket
}