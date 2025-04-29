variable "raw_bucket" {
  description = "The S3 bucket to store HN data"
  type        = string
  default     = "hn-raw-data-123456"  # replace or override via CLI
}

variable "cleaned_bucket" {
  description = "The S3 bucket to store HN data"
  type        = string
  default     = "hn-cleaned-data-123456"  # replace or override via CLI
}

variable "processed_bucket" {
  description = "The S3 bucket to store HN data"
  type        = string
  default     = "hn-processed-data-123456"  # replace or override via CLI
}

variable "state_bucket" {
  description = "The S3 bucket to store HN data"
  type        = string
  default     = "hn-state-data-123456"  # replace or override via CLI
}
