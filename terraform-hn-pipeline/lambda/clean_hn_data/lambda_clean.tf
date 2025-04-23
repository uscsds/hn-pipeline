resource "aws_lambda_function" "clean_hn_data" {
  function_name = "clean_hn_data"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_exec.arn

  filename         = "${path.module}/clean_hn_data/lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/clean_hn_data/lambda.zip")

  environment {
    variables = {
      RAW_BUCKET   = var.raw_bucket
      CLEAN_BUCKET = var.cleaned_bucket
      RAW_KEY      = "raw/hn_dump.json"
      CLEAN_KEY    = "cleaned/hn_cleaned.json"
    }
  }
}

data "local_file" "lambda_zip" {
  filename = "${path.module}/clean_hn_data/lambda.zip"
}

resource "aws_lambda_permission" "allow_cloudwatch_clean" {
  statement_id  = "AllowExecutionFromCloudWatchClean"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.clean_hn_data.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.fetch_rule.arn
}
