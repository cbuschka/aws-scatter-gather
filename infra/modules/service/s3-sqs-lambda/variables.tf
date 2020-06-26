variable "commitish" {
  default = "unknown"
  type = string
}

variable "scope" {
  default = ""
  type = string
}

variable "variant" {
  default = ""
  type = string
}

variable "package_base" {
  default = ""
  type = string
}

variable "env" {
  default = ""
  type = string
}

variable "with_work_bucket" {
  default = true
  type = bool
}

variable "with_batch_tables" {
  default = false
  type = bool
}
