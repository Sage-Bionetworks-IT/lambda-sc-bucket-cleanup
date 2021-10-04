import unittest

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from sc_bucket_cleanup import app


class TestApp(unittest.TestCase):

  list_buckets_response = {
      "Buckets": [
          {
              "Name": "alb-notebook-access-logsbucke-albaccesslogsbucket-1rzim5kz2nl3o",
              "CreationDate": "2020-07-17T22:28:57+00:00"
          },
          {
              "Name": "cf-templates-1povqxuabylok-us-east-1",
              "CreationDate": "2020-04-19T04:09:26+00:00"
          },
          {
              "Name": "sc-465877038949-pp-7pup2nolwsdym-s3bucket-l2va9c9yid12",
              "CreationDate": "2021-09-17T20:17:38+00:00"
          },
          {
              "Name": "sc-465877038949-pp-7yjimm2chq4nq-s3bucket-jdyynbf6wr4b",
              "CreationDate": "2021-09-28T19:18:36+00:00"
          },
          {
              "Name": "sc-465877038949-pp-con4cmcptfvgm-s3bucket-fnaumo4nb3lb",
              "CreationDate": "2021-02-11T16:26:05+00:00"
          },
          {
              "Name": "sc-465877038949-pp-qzha7mc257fbo-s3bucket-1m9wbdmmcjukq",
              "CreationDate": "2021-09-28T19:19:27+00:00"
          },
          {
              "Name": "sc-465877038949-pp-xab7zqb7wiero-s3bucket-1rkpmtqiu83ey",
              "CreationDate": "2021-07-15T21:21:16+00:00"
          },
          {
              "Name": "synapse-login-scipooldev-loadbalanceraccesslogsbu-30wr5c69ynzz",
              "CreationDate": "2020-04-21T22:59:15+00:00"
          },
      ]
  }

  @patch('sc_bucket_cleanup.app._get_stack_summaries')
  def test_get_deleted_stacks_no_stacks(self, get_stacks_mock):
    """
    This tests that AWS list stacks returns no stacks
    """
    get_stacks_mock.return_value = []
    sc_stacks = app._get_deleted_stacks(30)
    self.assertEqual(0, len((sc_stacks)))


  @patch('sc_bucket_cleanup.app._get_stack_resources')
  @patch('sc_bucket_cleanup.app._get_stack_summaries')
  @patch('sc_bucket_cleanup.app._get_purge_date')
  def test_get_deleted_stacks(self, purge_date_mock, get_stacks_mock,
                                    get_stack_resources_mock):
    """
    This tests that non S3 templates are ignored.  It also tests
    that only stacks with a deleted time older than the purge date
    will be returned
    """
    list_deleted_stacks_response = {
      'StackSummaries': [
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-qzha7mc257fbo/f9566150-2090-11ec-9d2c-12b31fceab89',
          'StackName': 'SC-465877038949-pp-qzha7mc257fbo',
          'TemplateDescription': 'Synapse S3 Custom Storage (https://docs.synapse.org/articles/custom_storage_location.html)',
          'CreationTime': datetime(2021, 4, 15, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 5, 12, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          }
        },
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-hgcdyuiopvtxa/65630bd0-fafa-11eb-8b9c-0e443e7db6f3',
          'StackName': 'SC-465877038949-pp-hgcdyuiopvtxa',
          'TemplateDescription': 'Service Catalog: Workflows Linux EC2',
          'CreationTime': datetime(2021, 6, 11, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 7, 14, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          }
        },
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-7yjimm2chq4nq/dae9af10-2090-11ec-b2d4-0a9dbbfba805',
          'StackName': 'SC-465877038949-pp-7yjimm2chq4nq',
          'TemplateDescription': 'Synapse S3 Custom Storage (https://docs.synapse.org/articles/custom_storage_location.html)',
          'CreationTime': datetime(2021, 2, 18, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 9, 25, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          }
        },
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/sc-product-assoc-ec2-linux-jumpcloud-workflows/df427f90-faf9-11eb-a0df-0e508885cec5',
          'StackName': 'sc-product-assoc-ec2-linux-jumpcloud-workflows',
          'TemplateDescription': 'SC action assocations to SC EC2 products',
          'CreationTime': datetime(2021, 7, 11, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 8, 21, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          }
        }
      ]
    }

    list_stack_resources_response = {
      'StackResourceSummaries': [
        {
          'LogicalResourceId': 'S3Bucket',
          'PhysicalResourceId': 'sc-465877038949-pp-qzha7mc257fbo-s3bucket-1m9wbdmmcjukq',
          'ResourceType': 'AWS::S3::Bucket',
          'LastUpdatedTimestamp': datetime(2021, 6, 28, tzinfo=timezone.utc),
          'ResourceStatus': 'DELETE_SKIPPED',
          'DriftInformation': {
            'StackResourceDriftStatus': 'NOT_CHECKED'
          }
        },
        {
          'LogicalResourceId': 'SynapseOwnerFile',
          'PhysicalResourceId': 's3://sc-465877038949-pp-qzha7mc257fbo-s3bucket-1m9wbdmmcjukq/owner.txt',
          'ResourceType': 'Custom::S3Object',
          'LastUpdatedTimestamp': datetime(2021, 6, 28, tzinfo=timezone.utc),
          'ResourceStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackResourceDriftStatus': 'NOT_CHECKED'
          }
        }
      ]
    }

    purge_date_mock.return_value = datetime(2021, 9, 12, tzinfo=timezone.utc)
    get_stacks_mock.return_value = list_deleted_stacks_response['StackSummaries']
    get_stack_resources_mock.return_value = list_stack_resources_response['StackResourceSummaries']

    sc_stacks = app._get_deleted_stacks(30)
    self.assertEqual(1, len((sc_stacks)))
    self.assertEqual(sc_stacks[0]['StackName'], "SC-465877038949-pp-qzha7mc257fbo")
    self.assertEqual(sc_stacks[0]['AssociatedResource'],
                     "sc-465877038949-pp-qzha7mc257fbo-s3bucket-1m9wbdmmcjukq")


  @patch('sc_bucket_cleanup.app._get_deleted_stacks')
  @patch('sc_bucket_cleanup.app._get_buckets')
  @patch('sc_bucket_cleanup.app._delete_bucket')
  def test_lambda_handler_cleanup_no_buckets_no_stacks(self, delete_bucket_mock,
                                    get_buckets_mock, get_deleted_stacks_mock):
    """
    This verifies the case where there are no deleted CFN stacks associated with
    S3 buckets in AWS therefore no bucket deletion is required.
    """

    get_deleted_stacks_mock.return_value = []
    get_buckets_mock.return_value = self.list_buckets_response['Buckets']
    delete_bucket_mock.return_value = ""
    app.lambda_handler("","")
    self.assertEqual(delete_bucket_mock.call_count, 0)


  @patch('sc_bucket_cleanup.app._get_deleted_stacks')
  @patch('sc_bucket_cleanup.app._get_buckets')
  @patch('sc_bucket_cleanup.app._delete_bucket')
  def test_lambda_handler_cleanup_no_matching_buckets(self, delete_bucket_mock,
                                    get_buckets_mock, get_deleted_stacks_mock):
    """
    This test the case where there are deleted CFN stacks associated to S3 buckets
    however there are no actual S3 resources in AWS that match the deleted stack.
    Therefore no bucket deletion is required.
    """
    get_deleted_stacks_response = {
      'StackSummaries': [
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-qzha7mc257fbo/f9566150-2090-11ec-9d2c-12b31fceab89',
          'StackName': 'SC-465877038949-pp-qzha7mc257fbo',
          'TemplateDescription': 'Synapse S3 Custom Storage (https://docs.synapse.org/articles/custom_storage_location.html)',
          'CreationTime': datetime(2021, 4, 15, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 5, 12, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          },
          'AssociatedResource': 'sc-465877038949-pp-qzha7mc257fbo-s3bucket-539wbdjmcjopf'
        },
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-hgcdyuiopvtxa/65630bd0-fafa-11eb-8b9c-0e443e7db6f3',
          'StackName': 'SC-465877038949-pp-hgcdyuiopvtxa',
          'TemplateDescription': 'Service Catalog: Workflows Linux EC2',
          'CreationTime': datetime(2021, 6, 11, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 7, 14, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          },
          'AssociatedResource': 'sc-465877038949-pp-con4cmcptfvgm-s3bucket-wrtumo4n91dg'
        }
      ]
    }

    get_deleted_stacks_mock.return_value = get_deleted_stacks_response['StackSummaries']
    get_buckets_mock.return_value = self.list_buckets_response['Buckets']
    delete_bucket_mock.return_value = ""
    app.lambda_handler("","")
    self.assertEqual(delete_bucket_mock.call_count, 0)

  @patch('sc_bucket_cleanup.app._get_deleted_stacks')
  @patch('sc_bucket_cleanup.app._get_buckets')
  @patch('sc_bucket_cleanup.app._delete_bucket')
  def test_lambda_handler_cleanup_multiple_buckets(self, delete_bucket_mock,
                                    get_buckets_mock, get_deleted_stacks_mock):
    """
    This test the case where there are deleted CFN stacks associated to S3 buckets
    and there are S3 bucket resources in AWS that match the deleted stack.
    Therefore bucket deletions are required.
    """
    get_deleted_stacks_response = {
      'StackSummaries': [
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-qzha7mc257fbo/f9566150-2090-11ec-9d2c-12b31fceab89',
          'StackName': 'SC-465877038949-pp-qzha7mc257fbo',
          'TemplateDescription': 'Synapse S3 Custom Storage (https://docs.synapse.org/articles/custom_storage_location.html)',
          'CreationTime': datetime(2021, 4, 15, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 5, 12, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          },
          'AssociatedResource': 'sc-465877038949-pp-qzha7mc257fbo-s3bucket-1m9wbdmmcjukq'
        },
        {
          'StackId': 'arn:aws:cloudformation:us-east-1:465877038949:stack/SC-465877038949-pp-hgcdyuiopvtxa/65630bd0-fafa-11eb-8b9c-0e443e7db6f3',
          'StackName': 'SC-465877038949-pp-hgcdyuiopvtxa',
          'TemplateDescription': 'Service Catalog: Workflows Linux EC2',
          'CreationTime': datetime(2021, 6, 11, tzinfo=timezone.utc),
          'DeletionTime': datetime(2021, 7, 14, tzinfo=timezone.utc),
          'StackStatus': 'DELETE_COMPLETE',
          'DriftInformation': {
            'StackDriftStatus': 'NOT_CHECKED'
          },
          'AssociatedResource': 'sc-465877038949-pp-con4cmcptfvgm-s3bucket-fnaumo4nb3lb'
        }
      ]
    }

    get_deleted_stacks_mock.return_value = get_deleted_stacks_response['StackSummaries']
    get_buckets_mock.return_value = self.list_buckets_response['Buckets']
    delete_bucket_mock.return_value = ""
    app.lambda_handler("","")
    self.assertEqual(delete_bucket_mock.call_count, 2)
