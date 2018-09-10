#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
AWSWebBuilder: Deployes Wesbites On AWS Platform.

The program automates manual processes of deploying static websites to AWS.
- Configure AWS S3 Buckets
  + Create the s3 bucket
  + Set them up for static website hosting
  + Deploy local files to them
- Configure DNS with AWS Route 53 service
- Configure CDN (Content Delivery Network) with SSL on AWS CloudFront
"""

import sys
import boto3
import click

from aws_web_builder import aws_util
from aws_web_builder.aws_s3 import AWSBucketManager
from aws_web_builder.aws_route53 import AWSRoute53Manager
from aws_web_builder.aws_acm import AWSCertificateManager
from aws_web_builder.aws_cdn import AWSDistributionManager

sys.path.append('..')

session = None
bucket_manager = None
domain_manager = None
cert_manager = None
dist_manager = None


@click.group()
@click.option('--profile', default=None,
              help="Use a given AWS profile from .aws directory.")
def cli(profile):
    """AWS Web Builder deploys websites to AWS."""
    global session, bucket_manager, domain_manager, cert_manager, dist_manager

    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = AWSBucketManager(session)
    domain_manager = AWSRoute53Manager(session)
    cert_manager = AWSCertificateManager(session)
    dist_manager = AWSDistributionManager(session)


# AWS S3 Commands
@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets from AWS."""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an s3 bucket."""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('create-bucket')
@click.argument('bucket')
def create_bucket(bucket):
    """Create s3 bucket in region of current session and configure it."""
    s3_bucket = bucket_manager.bucket_build(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync contents of PATHNAME to BUCKET."""
    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))


# AWS Route 53 Commands
@cli.command('list-hosted-zones')
def list_hosted_zones():
    """List all hosted zones in AWS."""
    client = session.client('route53')
    paginator = client.get_paginator('list_hosted_zones')
    for page in paginator.paginate():
        for zone in page['HostedZones']:
            print(zone)


@cli.command('setup-domain')
@click.argument('domain')
def setup_domain(domain):
    """Confiure DOMAIN to point to BUCKET."""
    bucket = bucket_manager.get_bucket(domain)

    zone = domain_manager.find_hosted_zone(domain) \
        or domain_manager.create_hosted_zone

    endpoint = aws_util.get_endpoint(bucket_manager.get_region_name(bucket))
    a_record = domain_manager.create_s3_domain_record(zone, domain, endpoint)
    print("Domain has been configured: http://{}".format(domain))
    print(a_record)


@cli.command('find-cert')
@click.argument('domain')
def find_cert(domain):
    """Find a certificate that matches the domain."""
    print(cert_manager.find_matching_cert(domain))


@cli.command('setup-cdn')
@click.argument('domain')
@click.argument('bucket')
def setup_cdn(domain, bucket):
    """Setup Content Delivery Network on AWS CloudFront."""
    dist = dist_manager.find_matching_dist(domain)

    if not dist:
        cert = cert_manager.find_matching_cert(domain)
        if not cert:
            print("Error: There was no matching cert found.")
            return

        dist = dist_manager.create_dist(domain, cert)
        print("Waiting on distribution deployment...")
        dist_manager.await_deploy(dist)

    zone = domain_manager.find_hosted_zone(domain) \
        or domain_manager.create_hosted_zone

    domain_manager.create_cf_domain_record(zone, domain, dist['DomainName'])
    print("The domain has been configured: https://{}".format(domain))

    return


if __name__ == '__main__':
    cli()
