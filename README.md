# aws_automation_toolkit

Repository for Automating AWS with Python, demonstrating POCs.

## aws_web_builder

AWS Web Builder is a script that will sync a local directory to an s3 bucket, and optionally can configure route 53 or CloudFront.

### Features

AWS Web Builder currently has the following features:
- Help using click package
- Set AWS profile with --profile=<profile_name>

S3 (Simple Storage Service):
- List bucket
- List contents of a bucket
- Create and setup up bucket configuration
- Sync directory tree to bucket (any OS)

Route 53:
- List hosted zones
- Configure route 53 domain

CloudFront:
- Configure CloudFront Distribution With SSL Cert

## aws_ec2_builder

AWS EC2 Builder is a script that will build ec2 instances and interact with those instances.

### Features

AWS EC2 Builder currently has the following features:
- Help using click package
- Set AWS profile with --profile=<profile_name>

EC2 (Elastic Compute Cloud)
