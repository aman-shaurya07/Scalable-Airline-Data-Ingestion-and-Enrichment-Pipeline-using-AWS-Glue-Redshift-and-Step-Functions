#!/bin/bash

# Delete S3 buckets
aws s3 rb s3://airline-data-ingestion --force

# Stop CloudTrail
aws cloudtrail delete-trail --name airline-data-trail
