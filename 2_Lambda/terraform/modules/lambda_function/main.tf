resource "aws_lambda_layer_version" "shared_layer" {
  filename             = "${path.module}/../../shared_layer/python_layer.zip"
  layer_name           = "shared-python-libs"
  compatible_runtimes  = ["python3.11"]
  source_code_hash     = filebase64sha256("${path.module}/../../shared_layer/python_layer.zip")
}

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  handler       = var.handler
  runtime       = "python3.11"
  role          = var.lambda_role_arn

  s3_bucket        = var.lambda_artifacts_bucket
  s3_key           = var.s3_key
  source_code_hash = filebase64sha256(var.source_path)

  environment {
    variables = var.env_variables
  }

  layers = [aws_lambda_layer_version.shared_layer.arn]
}
