import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/snapshot')))
import mock_import
import snapshot_function

class TestResourceProvider(unittest.TestCase):
    def test_snapshot_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "SnapshotCreation", "identifier": "database-1"}
        event = create_event()
        data = snapshot_function.lambda_create_dbinstance_snapshot(event, {})
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), "database-1")

    def test_snapshot_rateexceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")
        event = create_event()
        try:
            snapshot_function.lambda_create_dbinstance_snapshot(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")

    def test_snapshot_duplicate_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1 \nDBSnapshotAlreadyExists")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1 \nDBSnapshotAlreadyExists")
        event = create_event()
        try:
            snapshot_function.lambda_create_dbinstance_snapshot(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1 \nDBSnapshotAlreadyExists")

    def test_snapshot_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1 \nTimeoutException")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1 \nTimeoutException")
        event = create_event()
        try:
            snapshot_function.lambda_create_dbinstance_snapshot(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1 \nTimeoutException")

    def test_snapshot_id_not_provided_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "SnapshotCreation", "identifier": "database-1", "snapshot_id": "database-1-snapshot"}
        event = create_event()
        data = snapshot_function.lambda_create_dbinstance_snapshot(event, {})
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("snapshot_id"), "database-1-snapshot")

    def test_snapshot_id_provided_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "SnapshotCreation", "identifier": "database-1", "snapshot_id": "database-1-snapshot"}
        event = create_event_with_snapshot_id()
        data = snapshot_function.lambda_create_dbinstance_snapshot(event, {})
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("snapshot_id"), "database-1-snapshot")

def create_event():
    event = { "identifier": "database-1"}
    return event

def create_event_with_snapshot_id():
    event = { "identifier": "database-1"}
    return event