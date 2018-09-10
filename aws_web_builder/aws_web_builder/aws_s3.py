# -*- coding: utf-8 -*-

"""Classes for AWS S3 Buckets."""

import mimetypes
import boto3

from pathlib import Path
from botocore.exceptions import ClientError
from hashlib import md5
from sys import platform
from functools import reduce
from aws_web_builder.aws_web_builder import aws_util


class AWSBucketManager:
    """Manage AWS S3 Bucket."""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a AWSBucketManager object."""
        self.session = session
        self.s3 = session.resource('s3')
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE,
            multipart_threshold=self.CHUNK_SIZE
        )
        self.manifest = {}

    def get_bucket(self, bucket_name):
        """Get a bucket by name."""
        return self.s3.Bucket(bucket_name)

    def get_region_name(self, bucket):
        """Get the S3 bucket region name."""
        client = self.s3.meta.client
        bucket_location = client.get_bucket_location(Bucket=bucket.name)
        return bucket_location["LocationConstraint"] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the URL of the S3 bucket website."""
        return "http://{}.{}".format(bucket.name, aws_util.get_endpoint(self.get_region_name(bucket)).website_endpoint)

    def all_buckets(self):
        """Iterate all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket_name):
        """Iterate all objects in bucket."""
        return self.s3.Bucket(bucket_name).objects.all()

    def bucket_build(self, bucket_name):
        """Create a new bucket or will return an existing one by name."""
        s3_bucket = None

        try:
            s3_bucket = self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.session.region_name}
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error

        return s3_bucket

    @staticmethod
    def set_policy(bucket):
        """Set bucket policy to be readable by everyone publically."""
        policy = """
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::%s/*"
                    }
                ]
            }
            """ % bucket.name

        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)

    @staticmethod
    def configure_website(bucket):
        """Configure website in S3."""
        website = bucket.Website()
        website.put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })

    def load_manifest(self, bucket):
        """Load manifest data for caching."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket.name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']

    @staticmethod
    def hash_data(data):
        """Generate the md5 hash for the given data."""
        hash = md5()
        hash.update(data)

        return hash

    def gen_etag(self, path):
        """Generate etag for the uploaded file."""
        hashes = []

        with open(path, 'rb') as f:
            while True:
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break

            hashes.append(self.hash_data(data))

        if not hashes:
            return
        elif len(hashes) == 1:
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            hash = self.hash_data(reduce(lambda x, y: x + y, (h.digest() for h in hashes)))
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))

    def upload_file(self, bucket, path, key):
        """Upload the contents from path to s3 bucket."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        etag = self.gen_etag(path)
        if self.manifest.get(key, '') == etag:
            print("Skipping {}, etags match".format(key))
            return

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            },
            Config=self.transfer_config
        )

    def sync(self, pathname, bucket_name):
        """Sync a bucket or upload contents of a path to an S3 bucket."""
        bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket)

        root = Path(pathname).expanduser().resolve()

        def handle_dir(target):
            for path in target.iterdir():
                if path.is_dir():
                    handle_dir(path)
                if path.is_file():
                    if platform == "linux" or platform == "linux2":
                        self.upload_file(bucket, str(path), str(path.relative_to(root)))
                    elif platform == "darwin":
                        self.upload_file(bucket, str(path), str(path.relative_to(root)))
                    elif platform == "win32":
                        self.upload_file(bucket,
                                         '/'.join(str(path).split('\\')),
                                         '/'.join(str(path.relative_to(root)).split('\\')))

        handle_dir(root)
