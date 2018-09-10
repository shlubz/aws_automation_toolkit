# -*- coding: utf-8 -*-

"""Classes for AWS Certificate Manager (ACM)."""


class AWSCertificateManager:
    """Manage ACM certificates."""
    def __init__(self, session):
        self.session = session
        self.client = self.session.client('acm', region_name='us-east-1')

    def cert_matches(self, cert_arn, domain_name):
        """Check for a matching certificate with domain given."""
        cert_details = self.client.describe_certificate(CertificateArn=cert_arn)
        alt_names = cert_details['Certificate']['SubjectAlternativeNames']
        for name in alt_names:
            if name == domain_name:
                print("Domain Name Matches With Cert SAN: " + name)
                return True
            if name[0] == '*' and domain_name.endswith(name[1:]):
                print("Wildcard Domain Name Matches With Cert SAN: " + name)
                return True

        return False

    def find_matching_cert(self, domain_name):
        """Iterate over certificates to find matching certificate."""
        paginator = self.client.get_paginator('list_certificates')
        for page in paginator.paginate(CertificateStatuses=[]):
            if paginator.paginate(CertificateStatuses=['ISSUE']):
                for cert in page['CertificateSummaryList']:
                    if self.cert_matches(cert['CertificateArn'], domain_name):
                        print("Certificate Status is: ISSUED")
                        return cert

            elif paginator.paginate(CertificateStatuses=['PENDING_VALIDATION']):
                print("Certificate Status is: PENDING_VALIDATION")
                return None

        return None
