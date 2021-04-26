import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/common/python')))
import constants
from export import export_cluster_snapshot_s3_function
from mock import patch

os.environ["Region"] = "us-west-2"
os.environ['SNAPSHOT_EXPORT_TASK_ROLE'] = "testrole"
os.environ['SNAPSHOT_EXPORT_TASK_KEY'] = "testkey"

@patch("export.export_snapshot_s3_function.boto3.client")
class TestExportClusterSnapshotS3Function(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1"}
        self.instance_id = self.event['identifier']
        self.snapshot_id = self.event['identifier'] + constants.SNAPSHOT_POSTFIX
        self.mock_snapshot_arn = 'testarn'

        self.mocked_describe_cluster_snapshots_good = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'DBClusterSnapshots': [
                {
                    'Status': 'available',
                    'DBClusterSnapshotArn': self.mock_snapshot_arn,
                },
            ]
        }
        self.mocked_describe_cluster_snapshots_creating = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'DBClusterSnapshots': [
                {
                    'Status': 'creating',
                    'DBClusterSnapshotArn': self.mock_snapshot_arn,
                },
            ]
        }

    @patch("utility.get_aws_account_id", return_value="1231231234")
    def test_lambda_export_rds_snapshot_to_s3_good(self, mock_get_aws_account_id, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_cluster_snapshots.return_value = self.mocked_describe_cluster_snapshots_good
        mock_rds.start_export_task.return_value = {
            'SourceArn': self.mock_snapshot_arn,
            'Status': 'creating',
        }
        res = export_cluster_snapshot_s3_function.lambda_export_rds_cluster_snapshot_to_s3(self.event, {})
        self.assertEqual(res['status'], 'creating')

    @patch("utility.get_aws_account_id", return_value="1231231234")
    def test_lambda_export_rds_cluster_snapshot_to_s3_bad(self, mock_get_aws_account_id, mock_client):
        mock_rds = mock_client.return_value
        err_msg = "An error occurred (ExportTaskAlreadyExists) when calling the StartExportTask operation"
        mock_rds.start_export_task.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_cluster_snapshot_s3_function.lambda_export_rds_cluster_snapshot_to_s3(self.event, {})
            self.assertEqual(err.exception, err_msg)

    @patch("utility.get_aws_account_id", return_value="1231231234")
    def test_lambda_export_rds_cluster_snapshot_to_s3_bad_bucket_deleted(self, mock_get_aws_account_id, mock_client):
        mock_rds = mock_client.return_value
        err_msg = "An error occurred (InvalidS3BucketFault) when calling the StartExportTask operation: The S3 bucket rds-snapshots-1231231234 doesn't exist."
        mock_rds.start_export_task.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_cluster_snapshot_s3_function.lambda_export_rds_cluster_snapshot_to_s3(self.event, {})
            self.assertEqual(err.exception, err_msg)

    def test_get_cluster_snapshot_arn_good(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_cluster_snapshots.return_value = self.mocked_describe_cluster_snapshots_good
        res = export_cluster_snapshot_s3_function.get_cluster_snapshot_arn(self.snapshot_id)
        self.assertEqual(res, self.mock_snapshot_arn)

    def test_get_cluster_snapshot_arn_error(self, mock_client):
        """when snapshot not found"""
        mock_rds = mock_client.return_value
        err_msg = "Snapshot not found"
        mock_rds.describe_db_cluster_snapshots.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_cluster_snapshot_s3_function.get_cluster_snapshot_arn(self.snapshot_id)
            self.assertEqual(err.exception, err_msg)

    def test_get_cluster_snapshot_arn_notavailable(self, mock_client):
        """when snapshot is in creating state"""
        mock_rds = mock_client.return_value
        mock_rds.describe_db_cluster_snapshots.return_value = self.mocked_describe_cluster_snapshots_creating
        with self.assertRaises(Exception) as err:
            _ = export_cluster_snapshot_s3_function.get_cluster_snapshot_arn(self.snapshot_id)
            self.assertEqual(err.exception, "Snapshot is not available yet, status is creating")

