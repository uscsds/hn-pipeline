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

# === Auto-fetch latest version of hn-nltk_layer ===
data "aws_lambda_layer_version" "hn_nltk_layer" {
  layer_name = "hn-nltk_layer"
}

# === Auto-fetch latest version of hn-spacy_layer ===
data "aws_lambda_layer_version" "hn_spacy_layer" {
  layer_name = "hn-spacy_layer"
}
# === Auto-fetch latest version of hn-other_layer ===
data "aws_lambda_layer_version" "hn_other_layer" {
  layer_name = "hn-other_layer"
}


# ---------------------
# Lambda Function
# ---------------------
resource "aws_lambda_function" "this" {
  function_name = var.function_name
  handler       = var.handler
  runtime       = "python3.11"
  role          = var.lambda_role_arn
  timeout = 30  # in seconds (default is 3)

  s3_bucket        = var.lambda_artifacts_bucket
  s3_key           = aws_s3_object.lambda_code.key
  source_code_hash = filebase64sha256(var.source_path)

  environment {
    variables = var.env_variables
  }

  layers = [
    data.aws_lambda_layer_version.hn_nltk_layer.arn,
    data.aws_lambda_layer_version.hn_spacy_layer.arn,
    data.aws_lambda_layer_version.hn_other_layer.arn
  ]
}

