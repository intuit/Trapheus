import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/delete')))
import mock_import
import delete_function

class TestResourceProvider(unittest.TestCase):
    def test_delete_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('delete_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "Delete", "identifier": "database-1-temp"}
        event = create_event()
        data = delete_function.lambda_delete_dbinstance(event, {})
        self.assertEqual(data.get("taskname"), "Delete")
        self.assertEqual(data.get("identifier"), "database-1-temp")
        self.assertEqual(data.get("snapshot_id"), "database-1-snapshot")

        event = create_event_with_snapshot_id()
        data = delete_function.lambda_delete_dbinstance(event, {})
        self.assertEqual(data.get("taskname"), "Delete")
        self.assertEqual(data.get("identifier"), "database-1-temp")
        self.assertEqual(data.get("snapshot_id"), "snapshot-1")

    def test_delete_rateexceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('delete_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nthrottling error: Rate exceeded")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nthrottling error: Rate exceeded")
        event = create_event()
        try:
            delete_function.lambda_delete_dbinstance(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1-temp \nthrottling error: Rate exceeded")

    def test_delete_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('delete_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nDBInstanceNotFound")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nDBInstanceNotFound")
        event = create_event()
        try:
            delete_function.lambda_delete_dbinstance(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1-temp \nDBInstanceNotFound")

def create_event():
    event = { "identifier": "database-1"}
    return event

def create_event_with_snapshot_id():
    event = { "identifier": "database-1", "snapshot_id": "snapshot-1"}
    return event