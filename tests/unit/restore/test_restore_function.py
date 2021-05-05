import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import custom_exceptions
from mock import patch
from restore import restore_function

os.environ["Region"] = "us-west-2"

@patch("restore.restore_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1-temp"}
        self.restored_instance_id = "database-1"
        self.mocked_rate_exceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1 \nthrottling error: Rate exceeded")
        self.mocked_instance_not_found_exception = custom_exceptions.InstanceRestoreException("Identifier:database-1 \nDBInstanceNotFound")
        self.mocked_duplicate_instance_exception = custom_exceptions.InstanceRestoreException("Identifier:database-1 \nDBInstanceAlreadyExistsFault")
        self.mocked_describe_db_instances = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            "DBInstances": [{
                "DBInstanceIdentifier": "database-1-temp",
                "VpcSecurityGroups": [{
                    "VpcSecurityGroupId": "abc"
                }],
                "DBSubnetGroup": {
                    "DBSubnetGroupName": "xyz"
                }
            }]
        }

    def test_restore_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_instances.return_value = self.mocked_describe_db_instances
        data = restore_function.lambda_restore_dbinstance(self.event, {})
        self.assertEqual(data.get("taskname"), "Restore")
        self.assertEqual(data.get("identifier"), self.restored_instance_id)

    def test_restore_rateexceeded_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_instances.return_value = self.mocked_describe_db_instances
        mock_rds.restore_db_instance_from_db_snapshot.side_effect = Exception("throttling error: Rate exceeded")
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = restore_function.lambda_restore_dbinstance(self.event, {})
            self.assertEqual(err.exception, self.mocked_rate_exceeded_exception)

    def test_instance_describe_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_instances.side_effect = Exception("\nDBInstanceNotFound")
        with self.assertRaises(custom_exceptions.InstanceRestoreException) as err:
            _ = restore_function.lambda_restore_dbinstance(self.event, {})
            self.assertEqual(err.exception, self.mocked_instance_not_found_exception)

    def test_duplicate_instance_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_instances.side_effect = Exception("\nDBInstanceAlreadyExistsFault")
        with self.assertRaises(custom_exceptions.InstanceRestoreException) as err:
            _ = restore_function.lambda_restore_dbinstance(self.event, {})
            self.assertEqual(err.exception, self.mocked_duplicate_instance_exception)
