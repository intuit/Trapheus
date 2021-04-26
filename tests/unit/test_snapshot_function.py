import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/common/python')))
import custom_exceptions
from mock import patch
from snapshot import snapshot_function

os.environ["Region"] = "us-west-2"

@patch("snapshot.snapshot_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1"}
        self.mocked_rate_exceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1 \nthrottling error: Rate exceeded")
        self.mocked_instance_not_found_exception = custom_exceptions.SnapshotCreationException("Identifier:database-1 \nDBInstanceNotFoundFault")
        self.mocked_duplicate_snapshot_exception = custom_exceptions.RetryDBSnapshotException("Identifier:database-1 \nDBSnapshotAlreadyExists")

    def test_snapshot_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.create_db_snapshot.return_value = {}
        data = snapshot_function.lambda_create_dbinstance_snapshot(self.event, {})
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), self.event["identifier"])

    def test_snapshot_rateexceeded_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.create_db_snapshot.side_effect = Exception("throttling error: Rate exceeded")
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = snapshot_function.lambda_create_dbinstance_snapshot(self.event, {})
            self.assertEqual(err.exception, self.mocked_rate_exceeded_exception)

    def test_snapshot_duplicate_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.create_db_snapshot.side_effect = Exception("DBSnapshotAlreadyExists")
        with self.assertRaises(custom_exceptions.RetryDBSnapshotException) as err:
            _ = snapshot_function.lambda_create_dbinstance_snapshot(self.event, {})
            self.assertEqual(err.exception, self.mocked_duplicate_snapshot_exception)

    def test_snapshot_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.create_db_snapshot.side_effect = Exception("DBInstanceNotFoundFault")
        with self.assertRaises(custom_exceptions.SnapshotCreationException) as err:
            _ = snapshot_function.lambda_create_dbinstance_snapshot(self.event, {})
            self.assertEqual(err.exception, self.mocked_cluster_not_found_exception)
