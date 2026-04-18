terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.default_aws_region
}

provider "aws" {
  alias  = "ap_southeast_1"
  region = "ap-southeast-1"
}