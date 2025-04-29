resource "aws_s3_bucket" "hn_raw" {
  bucket        = "hn-raw-data-123456"
  force_destroy = true
}

resource "aws_s3_bucket" "hn_cleaned" {
  bucket        = "hn-cleaned-data-123456"
  force_destroy = true
}

resource "aws_s3_bucket" "hn_processed" {
  bucket        = "hn-processed-data-123456"
  force_destroy = true
}

resource "aws_s3_bucket" "hn_state" {
  bucket        = "hn-state-data-123456"
  force_destroy = true
}

# ✅ Lifecycle Rules

resource "aws_s3_bucket_lifecycle_configuration" "hn_raw_lifecycle" {
  bucket = aws_s3_bucket.hn_raw.id

  rule {
    id     = "archive-raw"
    status = "Enabled"

    filter {
      prefix = ""  # ✅ Properly scoped inside 'filter'
    }

    transition {
      days          = 2
      storage_class = "GLACIER"
    }

    expiration {
      days = 3
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "hn_cleaned_lifecycle" {
  bucket = aws_s3_bucket.hn_cleaned.id

  rule {
    id     = "archive-cleaned"
    status = "Enabled"

    filter {
      prefix = ""  # ✅ Properly scoped inside 'filter'
    }
    transition {
      days          = 3
      storage_class = "GLACIER"
    }

    expiration {
      days = 5
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "hn_processed_lifecycle" {
  bucket = aws_s3_bucket.hn_processed.id

  rule {
    id     = "archive-processed"
    status = "Enabled"

    filter {
      prefix = ""  # ✅ Properly scoped inside 'filter'
    }

    transition {
      days          = 7
      storage_class = "GLACIER"
    }

    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "hn_state_lifecycle" {
  bucket = aws_s3_bucket.hn_state.id

  rule {
    id     = "archive-processed"
    status = "Enabled"

    filter {
      prefix = ""  # ✅ Properly scoped inside 'filter'
    }

    transition {
      days          = 7
      storage_class = "GLACIER"
    }

    expiration {
      days = 30
    }
  }
}
