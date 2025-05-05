# ---------------------
# Layer 1: NLTK Layer
# ---------------------
#resource "aws_lambda_layer_version" "nltk_layer" {
#  filename             = "${path.module}/../../shared_layer/nltk_layer.zip"
#  layer_name           = "nltk-python-libs"
#  compatible_runtimes  = ["python3.11"]
#  source_code_hash     = filebase64sha256("${path.module}/../../shared_layer/nltk_layer.zip")
#}

# ---------------------
# Layer 2: spaCy Layer
# ---------------------
#resource "aws_lambda_layer_version" "spacy_layer" {
#  filename             = "${path.module}/../../shared_layer/spacy_layer.zip"
#  layer_name           = "spacy-python-libs"
#  compatible_runtimes  = ["python3.11"]
#  source_code_hash     = filebase64sha256("${path.module}/../../shared_layer/spacy_layer.zip")
#}

# ---------------------
# Layer 3: other Layer
# ---------------------
#resource "aws_lambda_layer_version" "other_layer" {
#  filename             = "${path.module}/../../shared_layer/other_layer.zip"
#  layer_name           = "spacy-python-libs"
#  compatible_runtimes  = ["python3.11"]
#  source_code_hash     = filebase64sha256("${path.module}/../../shared_layer/other_layer.zip")
#}


resource "aws_s3_object" "lambda_code" {
  bucket = var.lambda_artifacts_bucket
  key    = var.s3_key
  source = var.source_path
  etag   = filemd5(var.source_path)
}

# ---------------------
# Lambda Function
# ---------------------
resource "aws_lambda_function" "this" {
  function_name = var.function_name
  handler       = var.handler
  runtime       = "python3.11"
  role          = var.lambda_role_arn

  s3_bucket        = var.lambda_artifacts_bucket
  s3_key           = aws_s3_object.lambda_code.key
  source_code_hash = filebase64sha256(var.source_path)

  environment {
    variables = var.env_variables
  }

  layers = [
    "arn:aws:lambda:us-east-1:502435263495:layer:hn-nltk_layer:1",
    "arn:aws:lambda:us-east-1:502435263495:layer:hn-spacy-layer:1",
    "arn:aws:lambda:us-east-1:502435263495:layer:hn-other-layer:1"
  ]
}

