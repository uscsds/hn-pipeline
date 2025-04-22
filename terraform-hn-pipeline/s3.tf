resource "aws_s3_bucket" "hn_raw" {
  bucket        = "hn-raw-data-123456"
  force_destroy = true

  lifecycle_rule {
    id      = "archive-raw"
    enabled = true

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket" "hn_cleaned" {
  bucket        = "hn-cleaned-data-123456"
  force_destroy = true

  lifecycle_rule {
    id      = "archive-cleaned"
    enabled = true

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket" "hn_processed" {
  bucket        = "hn-processed-data-123456"
  force_destroy = true

  lifecycle_rule {
    id      = "archive-processed"
    enabled = true

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
