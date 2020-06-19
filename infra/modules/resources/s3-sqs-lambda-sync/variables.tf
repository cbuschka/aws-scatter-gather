variable "commitish" {
  default = "unknown"
  type = string
}

variable "scope" {
  default = ""
  type = string
}

variable "variant" {
  default = "s3-sqs-lambda-sync"
  type = string
}

variable "env" {
  default = ""
  type = string
}
