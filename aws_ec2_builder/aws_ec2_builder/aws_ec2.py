# /usr/bin/

import boto3
import click


s3 = boto3.resource('s3')

@cli
def __main__():

for bucket in s3.buckets.all():
    for obj in bucket.objects.filter()