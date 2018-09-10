# aws_web_builder

Repository for Automating AWS with Python, demonstrating POCs.

## AWSWebBuilder

AWS Web Builder is a script that will sync a local directory to an s3 bucket, and optionally can configure route 53 or CloudFront.

### Features

AWSWebBuilder currently has the following features:
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
