import os
from unittest import TestCase
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))

import constants
from export import export_snapshot_s3_function

os.environ["Region"] = "us-west-2"
os.environ["ExportSnapshotSupportedRegion"] = "eu-west-1"
os.environ['SNAPSHOT_EXPORT_TASK_ROLE'] = "testrole"
os.environ['SNAPSHOT_EXPORT_TASK_KEY'] = "testkey"
os.environ['SNAPSHOT_COPY_EXPORT_TASK_KEY'] = "test_copy_key"


@patch("utility.get_aws_account_id", return_value="1231231234")
class TestExportSnapshotS3Function(TestCase):

    def setUp(self):
        self.event = create_event("")
        self.mock_snapshot_arn = 'testarn'

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_lambda_export_rds_snapshot_to_s3_good(self, mock_client, _):
        mock_rds = mock_client.return_value
        mock_rds.start_export_task.return_value = {
            'SourceArn': self.mock_snapshot_arn,
            'Status': 'creating',
        }
        res = export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
        self.assertEqual(res['status'], 'creating')

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_lambda_export_rds_snapshot_to_s3_bad(self, mock_client, _):
        mock_rds = mock_client.return_value
        err_msg = "An error occurred (ExportTaskAlreadyExists) when calling the StartExportTask operation"
        mock_rds.start_export_task.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
            self.assertEqual(err.exception, err_msg)

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_lambda_export_rds_snapshot_to_s3_bad_bucket_deleted(self, mock_client, _):
        mock_rds = mock_client.return_value
        err_msg = "An error occurred (InvalidS3BucketFault) when calling the StartExportTask operation: The S3 " \
                  "bucket rds-snapshots-1231231234 doesn't exist."
        mock_rds.start_export_task.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
            self.assertEqual(err.exception, err_msg)

    @patch("export.export_snapshot_s3_function.boto3")
    def test_lambda_export_rds_snapshot_to_s3_from_supporting_region_called_with_correct_region(self, mock_boto3, _):
        self.event = create_event(constants.EXPORT_SNAPSHOT_TO_S3_IN_REGION_THAT_SUPPORTS_SNAPSHOT_EXPORT_TO_S3)
        export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
        mock_boto3.client.assert_called_with('rds', "eu-west-1")


def create_event(taskname):
    event = {"identifier": "database-1", "taskname": taskname}
    return event
