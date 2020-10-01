import os
from unittest import TestCase
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))
import mock_import
import constants
from common.python import utility


@patch("utility.get_aws_account_id", return_value="1231231234")
class TestExportSnapshotS3Function(TestCase):

    def setUp(self):
        self.event = create_event()
        self.instance_id = self.event['identifier']
        self.snapshot_id = self.event['identifier'] + constants.SNAPSHOT_POSTFIX
        self.region = "us-west-2"
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

    @patch("common.python.utility.boto3.client")
    def test_get_snapshot_arn_good(self, mock_client, _):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_snapshots.return_value = self.mocked_describe_db_snapshots_good
        res = utility.get_instance_snapshot_arn(self.snapshot_id, self.region)
        self.assertEqual(res, self.mock_snapshot_arn)

    @patch("common.python.utility.boto3.client")
    def test_get_snapshot_arn_error(self, mock_client, _):
        """when snapshot not found"""
        mock_rds = mock_client.return_value
        err_msg = "Snapshot not found"
        mock_rds.describe_db_snapshots.side_effect = Exception(err_msg)
        with self.assertRaises(Exception) as err:
            _ = utility.get_instance_snapshot_arn(self.snapshot_id, self.region)
            self.assertEqual(err.exception, err_msg)

    @patch("common.python.utility.boto3.client")
    def test_get_snapshot_arn_notavailable(self, mock_client, _):
        """when snapshot is in creating state"""
        mock_rds = mock_client.return_value
        mock_rds.describe_db_snapshots.return_value = self.mocked_describe_db_snapshots_creating
        with self.assertRaises(Exception) as err:
            _ = utility.get_instance_snapshot_arn(self.snapshot_id, self.region)
            self.assertEqual(err.exception, "Snapshot is not available yet, status is creating")


def create_event():
    event = {"identifier": "database-1"}
    return event
