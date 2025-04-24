variable "role_name" {
  type        = string
  description = "Name of the shared Lambda execution role"
  value       = aws_iam_role.lambda_exec.id
}
