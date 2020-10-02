import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/restore')))
import mock_import
import restore_function

class TestResourceProvider(unittest.TestCase):
    def test_restore_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('restore_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "Restore", "identifier": "database-1"}
        mock_factory_boto_client.describe_db_instances.return_value = mock_response
        mock_response.describe_db_instances.return_value = {"DBInstances": [{"DBInstanceIdentifier": "database-1-temp","VpcSecurityGroups": [{"VpcSecurityGroupId": "abc"}],"DBSubnetGroup": {"DBSubnetGroupName": "xyz"}}]}
        event = create_event()
        data = restore_function.lambda_restore_dbinstance(event, {})
        self.assertEqual(data.get("taskname"), "Restore")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("snapshot_id"), "database-1-snapshot")

        event = create_event_with_snapshot_id()
        data = restore_function.lambda_restore_dbinstance(event, {})
        self.assertEqual(data.get("taskname"), "Restore")
        self.assertEqual(data.get("snapshot_id"), "snapshot-1")

    def test_restore_rateexceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('restore_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")
        event = create_event()
        try:
            restore_function.lambda_restore_dbinstance(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")

    def test_restore_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('restore_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1 \nDBInstanceNotFound")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1 \nDBInstanceNotFound")
        event = create_event()
        try:
            restore_function.lambda_restore_dbinstance(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1 \nDBInstanceNotFound")

def create_event():
    event = { "identifier": "database-1"}
    return event

def create_event_with_snapshot_id():
    event = { "identifier": "database-1", "snapshot_id": "snapshot-1"}
    return event