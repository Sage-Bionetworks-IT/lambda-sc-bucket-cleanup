import boto3
import logging
import os

from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone

logging.basicConfig(level=logging.INFO)

MAX_DAYS_FROM_DELETION = 90

def _get_s3_client():
  return boto3.client('s3')

def _get_cfn_client():
  return boto3.client('cloudformation')

def _get_env_var_value(env_var):
  """Get the value of an environment variable
  :param env_var: The environment variable
  :returns: The environment variable's value, None if env var is not found
  """
  value = os.getenv(env_var)
  if not value:
    logging.warning(f'cannot get environment variable: {env_var}')

  return value

def _get_stack_summaries(status_filter):
  """
  Get a list of the cloudformation stack summaries applied with a status filter.
  :param status_filter: The status filter used when listing cloudformation stacks
  :return: A list of cloudformation stack summaries
  """
  cfn = _get_cfn_client()
  return cfn.list_stacks(StackStatusFilter=status_filter)['StackSummaries']

def _get_stack_resources(stack_name):
  """
  Get the information for a cloudformation stack's resource.
  :param stack_name: The name of the stack or a stack id.  The stack id is
                     required when getting resources for a deleted stack.
  :return:
  """
  cfn = _get_cfn_client()
  return cfn.list_stack_resources(StackName=stack_name)['StackResourceSummaries']

def _get_buckets():
  """
  Get a list of all buckets in the AWS account
  :return:
  """
  s3 = _get_s3_client()
  return s3.list_buckets()['Buckets']

def _get_purge_date(days_deleted):
  """
  Get the date used to determine whether an AWS resources should be removed.  We
  inspect any cloudformation stack that was deleted before this date and to see what
  resource it provisioned.  If that resource still exist in AWS it will be deleted.
  """
  return datetime.now(timezone.utc) - timedelta(days=days_deleted)

def _get_deleted_stacks(days_from_deletion):
  """
  Get all the deleted Cloudformation stacks that were deployed by the Service
  Catalog to provision S3 buckets.
  :param days_from_deletion: The number of days, from today, that the stack was deleted.
    Cloudformation will retain stack info for only 90 days after it has been deleted.
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stacks
  :return: A modified list of Cloudformation stacks summaries that includes
           an associated resource that the stack provisioned.
  """
  if days_from_deletion >= MAX_DAYS_FROM_DELETION:
    logging.info(f'Cloudformation will retain stack info for only 90 days '
                 f'after it has been deleted. Resetting days_from_deletion to 30' )
    days_from_deletion = MAX_DAYS_FROM_DELETION

  sc_stacks = []
  purge_date = _get_purge_date(days_from_deletion)
  stack_summaries = _get_stack_summaries(['DELETE_COMPLETE'])
  for stack_summary in stack_summaries:
    stack_name = stack_summary['StackName']
    stack_id = stack_summary['StackId']

    if "DeletionTime" in stack_summary and \
        stack_summary['DeletionTime'] < purge_date and \
        stack_name.startswith("SC-") and \
        "s3" in stack_summary['TemplateDescription'].lower():

      stack_resources_summaries = _get_stack_resources(stack_id)
      for stack_resource in stack_resources_summaries:
        if stack_resource['ResourceType'] == 'AWS::S3::Bucket':
          stack_summary['AssociatedResource'] = stack_resource['PhysicalResourceId']
          sc_stacks.append(stack_summary)
          break

  return sc_stacks

def _delete_bucket(bucket_name):
  """
  Delete a bucket including all the data in the bucket
  Note: This does not support removing buckets with versioning enabled
  :param bucket_name: The bucket's name
  :return:
  """
  try:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    bucket.delete()
  except ClientError as error:
    logging.warning(f'failed to delete bucket: {bucket_name}')
    raise error

def lambda_handler(event, context):
  archived_period = _get_env_var_value('ARCHIVED_PERIOD')
  deleted_stacks = _get_deleted_stacks(archived_period)
  logging.debug(f'SC deleted stacks: {deleted_stacks}')
  buckets = _get_buckets()
  for deleted_stack in deleted_stacks:
    for bucket in buckets:
      if deleted_stack['AssociatedResource'] == bucket['Name']:
        logging.info(f'Clean up bucket {bucket["Name"]} provisioned by '
                     f'CFN stack {deleted_stack["StackName"]}')
        _delete_bucket(bucket['Name'])
        break


if __name__ == "__main__":
    lambda_handler("event","context")
