# -*- coding: utf-8 -*-

import uuid

"""Classes for Route 53 domains."""


class AWSRoute53Manager:
    """manage a Route 53 domain."""

    def __init__(self, session):
        """Create a AWSRoute53Manager object."""
        self.session = session
        self.client = self.session.client('route53')

    def find_hosted_zone(self, domain_name):
        """Find a hosted zone in Route53."""
        paginator = self.client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone

        return None

    def create_hosted_zone(self, domain_name):
        """Create a Route53 hosted zone."""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        self.client.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(uuid.uuid4())
        )

    def create_s3_domain_record(self, zone, domain_name, endpoint):
        """Create a Route53 domain record that maps to S3 bucket."""
        return self.client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': 'Created by AWS Web Builder',
                'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': domain_name,
                            'Type': 'A',
                            'AliasTarget': {
                                'HostedZoneId': endpoint.route53_zone,
                                'DNSName': endpoint.website_endpoint,
                                'EvaluateTargetHealth': False
                            }
                        }
                    }
                ]
            }
        )

    def create_cf_domain_record(self, zone, domain_name, cf_domain):
        """Create a CloudFront domain record that maps to S3 bucket."""
        return self.client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': 'Created by AWS Web Builder',
                'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': domain_name,
                            'Type': 'A',
                            'AliasTarget': {
                                'HostedZoneId': 'Z2FDTNDATAQYW2',
                                'DNSName': cf_domain,
                                'EvaluateTargetHealth': False
                            }
                        }
                    }
                ]
            }
        )