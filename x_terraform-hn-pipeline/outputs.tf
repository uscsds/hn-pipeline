output "raw_bucket" {
  value = aws_s3_bucket.hn_raw.bucket
}

output "cleaned_bucket" {
  value = aws_s3_bucket.hn_cleaned.bucket
}

output "processed_bucket" {
  value = aws_s3_bucket.hn_processed.bucket
}
