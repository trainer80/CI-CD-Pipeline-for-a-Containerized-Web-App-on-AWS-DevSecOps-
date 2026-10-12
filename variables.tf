variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix used for resource names"
  type        = string
  default     = "devsecops-flask"
}

variable "instance_type" {
  description = "EC2 instance type (check which type is free-tier eligible in your account)"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of an existing EC2 key pair in your AWS account"
  type        = string
}

variable "my_ip_cidr" {
  description = "Your public IP in CIDR form for SSH access, e.g. 203.0.113.10/32"
  type        = string
}
