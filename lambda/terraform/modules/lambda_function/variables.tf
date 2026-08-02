variable "function_name" {}
variable "description" { default = "" }
variable "handler" {}
variable "source_path" {}
variable "s3_key" {}
variable "env_variables" { type = map(string) }

variable "lambda_role_arn" {}
variable "lambda_artifacts_bucket" {}
