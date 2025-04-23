variable "bucket_name" {
  description = "The S3 bucket to store HN data"
  type        = string
  default     = "my-hn-data-bucket"  # replace or override via CLI
}

