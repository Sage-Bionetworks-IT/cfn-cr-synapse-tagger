# A wrapper script to Change ownership of Service Catalog provisioned products.
# This script supports changing ownership on one product at a time.
# More info at IT-4483
#
# Usage:
#   AWS_PROFILE=my-aws-profile AWS_DEFAULT_REGION=us-east-1 pipenv run change_owner --help
#
# Example to change bucket owner:
#   pipenv run change_owner \
#   --ProvisionedProductId pp-j6npiwvn72hjg \
#   --NewOwnerArn arn:aws:sts::999999999999:assumed-role/ServiceCatalogEndusers/1234567 \
#   --BucketName MYBUCKET
# Example to change EC2 instance owner:
#   pipenv run change_owner \
#   --ProvisionedProductId pp-j6npiwvn72hjg \
#   --NewOwnerArn arn:aws:sts::999999999999:assumed-role/ServiceCatalogEndusers/1234567 \
#   --InstanceId i-0c1d159b27a027a33
# Example to change scheduled jobs owner:
#   pipenv run change_owner \
#   --ProvisionedProductId pp-j6npiwvn72hjg \
#   --NewOwnerArn arn:aws:sts::999999999999:assumed-role/ServiceCatalogEndusers/1234567 \
#   --StackId 'arn:aws:cloudformation:us-east-1:999999999999:stack/SC-999999999999-pp-dtstzmysqf36i/f3a44380-9418-11f0-930e-1204b39d8e69'

import argparse
import json
import boto3
import os
import re
import sys
import set_tags.utils as utils
import set_tags.set_bucket_tags as set_bucket_tags
import set_tags.set_instance_tags as set_instance_tags
import set_tags.set_batch_tags as set_batch_tags


def get_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Change Service Catalog provisioned product ownership."
    )

    # Required argument
    parser.add_argument(
        "--ProvisionedProductId",
        help="The identifier of the provisioned product (required)",
        required=True
    )
    parser.add_argument(
        "--NewOwnerArn",
        help="The ARN of the new owner (required)",
        required = True
    )

    # Optional arguments
    parser.add_argument(
        "--StackId",
        help="The CloudFormation stack ID for batch scheduled jobs",
        default=None
    )
    parser.add_argument(
        "--BucketName",
        help="The S3 bucket name",
        default=None
    )
    parser.add_argument(
        "--InstanceId",
        help="The EC2 instance ID",
        default=None
    )

    return parser.parse_args()

def get_account_and_user_id_from_arn(arn: str):
    """
    Extracts the account ID and user ID from an assumed role ARN.

    Parameters:
    - arn: str → the ARN to parse (must be of form
      arn:aws:sts::<account_id>:assumed-role/ServiceCatalogEndusers/<user_id>)

    Returns:
    - Tuple (account_id: str, user_id: str)
    """
    match = re.match(
        r'arn:aws:sts::(\d+):assumed-role/ServiceCatalogEndusers/(\d+)',
        arn
    )
    if not match:
        raise ValueError(f"ARN {arn} is not in the expected format")

    return match.groups()


def update_bucket_principal_arn(bucket_name: str, target_user_id: str, new_assumed_role_arn: str):
    """
    Updates the Principal ARNs in an S3 bucket policy by replacing all ARNs
    that contain a specific target user ID with a new assumed-role ARN.

    Parameters:
    ----------
    bucket_name : str
        The name of the S3 bucket whose policy will be updated.
    target_user_id : str
        The user ID within the assumed-role ARN that should be replaced.
        Only ARNs containing this user ID will be updated.
    new_assumed_role_arn : str
        The new assumed-role ARN to replace the target ARN(s) with.
        Must be in the format:
        'arn:aws:sts::<account_id>:assumed-role/ServiceCatalogEndusers/<user_id>'
    """
    s3 = boto3.client("s3")

    try:
        # Fetch current bucket policy
        response = s3.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(response["Policy"])

        updated = False

        for statement in policy.get("Statement", []):
            aws_principals = statement.get("Principal", {}).get("AWS", [])

            # Ensure we have a list for consistency
            if isinstance(aws_principals, str):
                aws_principals = [aws_principals]

            new_list = []
            for arn in aws_principals:
                # Replace only if ARN contains the target user_id
                if f"/{target_user_id}" in arn:
                    new_list.append(new_assumed_role_arn)
                    updated = True
                else:
                    new_list.append(arn)

            if new_list:
                statement["Principal"]["AWS"] = new_list

        if not updated:
            print(f"No ARN found with user_id {target_user_id}.")
            return

        # Apply updated policy
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        print(f"Bucket policy updated successfully for {bucket_name}.")

    except s3.exceptions.NoSuchBucketPolicy:
        print(f"No policy found for bucket {bucket_name}.")
    except Exception as e:
        print(f"Error updating bucket policy: {e}")

def get_batch_resource_arns(stack_name: str) -> dict:
    """
    Retrieves physical IDs of Batch resources from a CloudFormation stack.

    Args:
        stack_name (str): The name or ID of the CloudFormation stack.

    Returns:
        dict: Dictionary containing ARNs for:
            - JobDefinitionArn
            - ComputeEnvironmentArn
            - SchedulingPolicyArn
            - JobQueueArn
    """
    cf_client = boto3.client("cloudformation")
    result = {}

    try:
        # Call describe_stack_resources API
        response = cf_client.describe_stack_resources(StackName=stack_name)
        stack_resources = response.get("StackResources", [])

        for resource in stack_resources:
            resource_type = resource.get("ResourceType")
            physical_id = resource.get("PhysicalResourceId")

            if resource_type == "AWS::Batch::JobDefinition":
                result["JobDefinitionArn"] = physical_id
            elif resource_type == "AWS::Batch::ComputeEnvironment":
                result["ComputeEnvironmentArn"] = physical_id
            elif resource_type == "AWS::Batch::SchedulingPolicy":
                result["SchedulingPolicyArn"] = physical_id
            elif resource_type == "AWS::Batch::JobQueue":
                result["JobQueueArn"] = physical_id

        return result

    except cf_client.exceptions.ClientError as e:
        print(f"Error retrieving stack resources: {e}")
        return {}


def main():
    args = get_args()
    new_owner_arn = args.NewOwnerArn
    new_account_id, new_user_id = get_account_and_user_id_from_arn(new_owner_arn)

    # Execute a Service catalog change owner action
    sc_client = boto3.client("servicecatalog")
    print(f"Executing Service Catalog change owner action for product "
          f"{args.ProvisionedProductId} to new owner {new_owner_arn}")
    response = sc_client.update_provisioned_product_properties(
        ProvisionedProductId=args.ProvisionedProductId,
        ProvisionedProductProperties={
            "OWNER": new_owner_arn
        }
    )
    print(f"Service Catalog change owner response: {response}")

    # Update tags for service catalog products
    os.environ["TEAM_TO_ROLE_ARN_MAP_PARAM_NAME"] = "/service-catalog/TeamToRoleArnMap"
    if args.StackId:
        stack_id = args.StackId
        print(f"StackId: {stack_id}")
        event = {"StackId": stack_id}
        stack_name = stack_id.split("stack/")[1].split("/")[0]
        try:
            # monkey patch to return the Synapse owner id from the passed in OwnerArn
            utils.get_synapse_owner_id = lambda tags: new_user_id

            # monkey patch to return a dict of batch resource ARNs from the list of cloudformation resources
            batch_resources = get_batch_resource_arns(stack_name)
            utils.get_property_value = lambda event, key: batch_resources

            print(f"Update tags on batch resources: {batch_resources}")
            set_batch_tags.create_or_update(event, None)
            print("Batch tags updated successfully.")
        except Exception as e:
            print(f"Failed to update batch resources: {e}")
            sys.exit(1)
    if args.BucketName:
        bucket_name = args.BucketName
        event = {"ResourceProperties":{"BucketName": bucket_name}}
        try:
            # Get existing synapse user id
            bucket_tags = set_bucket_tags.get_bucket_tags(bucket_name)
            existing_user_id = utils.get_synapse_owner_id(bucket_tags)

            # monkey patch to return the Synapse owner id from the passed in OwnerArn
            utils.get_synapse_owner_id = lambda tags: new_user_id

            print(f"Update tags on bucket: {bucket_name}")
            set_bucket_tags.create_or_update(event, None)
            print("Bucket tags updated successfully.")

            # Update the bucket policy to allow new owner access
            print(f"Update policy on bucket: {bucket_name}")
            update_bucket_principal_arn(bucket_name, existing_user_id, new_owner_arn)
        except Exception as e:
            print(f"Failed to update bucket: {e}")
            sys.exit(1)
    if args.InstanceId:
        instance_id = args.InstanceId
        event = {"ResourceProperties":{"InstanceId": instance_id}}
        try:
            # monkey patch to return the Synapse owner id from the passed in OwnerArn
            utils.get_synapse_owner_id = lambda tags: new_user_id

            print(f"Update tags on EC2 instance: {instance_id}")
            set_instance_tags.create_or_update(event, None)
            print("Instance tags updated successfully.")
        except Exception as e:
            print(f"Failed to update instance: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
