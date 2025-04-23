variable "raw_data_bucket_name" {
  description = "Name of the raw data S3 bucket"
  type        = string
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda-hn-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Effect = "Allow",
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3_inline" {
  name = "lambda-s3-inline-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:PutObject"],
        Resource = "arn:aws:s3:::${var.raw_data_bucket_name}/*"
      }
    ]
  })
}

output "lambda_zip_path" {
  value = "${path.module}/lambda.zip"
}

data "local_file" "lambda_zip" {
  filename = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "hn_fetch" {
  function_name    = "fetch_hn-fetch"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  filename         = data.local_file.lambda_zip.filename
  source_code_hash = filebase64sha256(data.local_file.lambda_zip.filename)
  timeout          = 60
}

resource "aws_cloudwatch_event_rule" "every_hour" {
  name                = "fetch-hn-every-hour"
  schedule_expression = "rate(1 hour)"
}

resource "aws_cloudwatch_event_target" "lambda_schedule" {
  rule      = aws_cloudwatch_event_rule.every_hour.name
  target_id = "lambda"
  arn       = aws_lambda_function.hn_fetch.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hn_fetch.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_hour.arn
}
