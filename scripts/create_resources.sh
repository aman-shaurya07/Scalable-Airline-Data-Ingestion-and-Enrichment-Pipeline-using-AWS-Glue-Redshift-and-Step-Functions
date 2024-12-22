#!/bin/bash

# Create S3 buckets
aws s3api create-bucket --bucket airline-data-ingestion --region us-east-1
aws s3api put-bucket-versioning --bucket airline-data-ingestion --versioning-configuration Status=Enabled

# Upload initial data
aws s3 cp ../data/airport_codes.csv s3://airline-data-ingestion/dimensional-data/
aws s3 cp ../data/sample_flights.csv s3://airline-data-ingestion/daily-flight-data/

# Create CloudTrail
aws cloudtrail create-trail --name airline-data-trail --s3-bucket-name airline-data-ingestion-trail-logs
aws cloudtrail start-logging --name airline-data-trail
