#!/bin/bash
set -ex

# Upload template to AWS Admincentral account to share with other projects.
repo_name="${PWD##*/}"
s3_bucket=$(aws cloudformation list-exports --query "Exports[?Name=='us-east-1-bootstrap-CloudformationBucket'].Value" --output text)
s3_bucket_path="${repo_name}/${TRAVIS_BRANCH}"
s3_bucket_url="s3://${s3_bucket}/${s3_bucket_path}"
template='.aws-sam/build/set-bucket-tags-macro.yaml'
file="${template##*/}"
aws s3 cp "${template}" "${s3_bucket_url}${file}"
