import os
from unittest import TestCase
from unittest.mock import patch

import constants
from export import export_snapshot_s3_function

os.environ["Region"] = "us-west-2"
os.environ['SNAPSHOT_EXPORT_TASK_ROLE'] = "testrole"
os.environ['SNAPSHOT_EXPORT_TASK_KEY'] = "testkey"


@patch("export.export_snapshot_s3_function.__get_aws_account_id", return_value="1231231234")
class TestExportSnapshotS3Function(TestCase):

    def setUp(self):
        self.event = create_event()
        self.instance_id = self.event['identifier']
        self.snapshot_id = self.event['identifier'] + constants.SNAPSHOT_POSTFIX
        self.mock_snapshot_arn = 'testarn'
        self.mocked_describe_db_snapshots_good = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'DBSnapshots': [
                {
                    'Status': 'available',
                    'DBSnapshotArn': self.mock_snapshot_arn,
                },
            ]
        }
        self.mocked_describe_db_snapshots_creating = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'DBSnapshots': [
                {
                    'Status': 'creating',
                    'DBSnapshotArn': self.mock_snapshot_arn,
                },
            ]
        }
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

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_lambda_export_rds_snapshot_to_s3_good(self, mock_client, _):
        self.event["isCluster"] = False
        mock_rds = mock_client.return_value
        mock_rds.describe_db_snapshots.return_value = self.mocked_describe_db_snapshots_good
        mock_rds.start_export_task.return_value = {
            'SourceArn': self.mock_snapshot_arn,
            'Status': 'creating',
        }
        res = export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
        self.assertEqual(res['status'], 'creating')

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_lambda_export_rds_snapshot_to_s3_bad(self, mock_client, _):
        self.event["isCluster"] = False
        mock_rds = mock_client.return_value
        err_msg = "An error occurred (ExportTaskAlreadyExists) when calling the StartExportTask operation"
        mock_rds.start_export_task.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
            self.assertEqual(err.exception, err_msg)

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_get_snapshot_arn_good(self, mock_client, _):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_snapshots.return_value = self.mocked_describe_db_snapshots_good
        res = export_snapshot_s3_function.get_snapshot_arn(self.snapshot_id, False)
        self.assertEqual(res, self.mock_snapshot_arn)

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_get_snapshot_arn_error(self, mock_client, _):
        """when snapshot not found"""
        mock_rds = mock_client.return_value
        err_msg = "Snapshot not found"
        mock_rds.describe_db_snapshots.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.get_snapshot_arn(self.snapshot_id, False)
            self.assertEqual(err.exception, err_msg)

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_get_snapshot_arn_notavailable(self, mock_client, _):
        """when snapshot is in creating state"""
        mock_rds = mock_client.return_value
        mock_rds.describe_db_snapshots.return_value = self.mocked_describe_db_snapshots_creating
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.get_snapshot_arn(self.snapshot_id, False)
            self.assertEqual(err.exception, "Snapshot is not available yet, status is creating")

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_lambda_export_rds_snapshot_to_s3_cluster_good(self, mock_client, _):
        self.event["isCluster"] = True
        mock_rds = mock_client.return_value
        mock_rds.describe_db_cluster_snapshots.return_value = self.mocked_describe_cluster_snapshots_good
        mock_rds.start_export_task.return_value = {
            'SourceArn': self.mock_snapshot_arn,
            'Status': 'creating',
        }
        res = export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
        self.assertEqual(res['status'], 'creating')

    # FOR CLUSTER SNAPSHOTS:
    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_lambda_export_rds_snapshot_to_s3_cluster_bad(self, mock_client, _):
        self.event["isCluster"] = True
        mock_rds = mock_client.return_value
        err_msg = "An error occurred (ExportTaskAlreadyExists) when calling the StartExportTask operation"
        mock_rds.start_export_task.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.lambda_export_rds_snapshot_to_s3(self.event, {})
            self.assertEqual(err.exception, err_msg)

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_get_snapshot_arn_is_cluster_good(self, mock_client, _):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_cluster_snapshots.return_value = self.mocked_describe_cluster_snapshots_good
        res = export_snapshot_s3_function.get_snapshot_arn(self.snapshot_id, True)
        self.assertEqual(res, self.mock_snapshot_arn)

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_get_snapshot_arn_is_cluster_error(self, mock_client, _):
        """when snapshot not found"""
        mock_rds = mock_client.return_value
        err_msg = "Snapshot not found"
        mock_rds.describe_db_cluster_snapshots.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.get_snapshot_arn(self.snapshot_id, True)
            self.assertEqual(err.exception, err_msg)

    @patch("export.export_snapshot_s3_function.boto3.client")
    def test_get_snapshot_arn_is_cluster_notavailable(self, mock_client, _):
        """when snapshot is in creating state"""
        mock_rds = mock_client.return_value
        mock_rds.describe_db_cluster_snapshots.return_value = self.mocked_describe_cluster_snapshots_creating
        with self.assertRaises(Exception) as err:
            _ = export_snapshot_s3_function.get_snapshot_arn(self.snapshot_id, True)
            self.assertEqual(err.exception, "Snapshot is not available yet, status is creating")


def create_event():
    event = {"identifier": "database-1"}
    return event
