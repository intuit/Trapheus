import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import constants
import custom_exceptions
from mock import patch
from rename import rename_function

os.environ["Region"] = "us-west-2"

@patch("rename.rename_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1"}
        self.revert_event = {"Error": "InstanceRestoreException","Cause": "Identifier:database-1 \n ThrottlingError: Rate exceeded"}
        self.updated_instance_id = self.event['identifier'] + constants.TEMP_POSTFIX
        self.original_instance_id = self.event['identifier']
        self.mocked_rate_exceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1-temp \nthrottling error: Rate exceeded")
        self.mocked_instance_not_found_exception = custom_exceptions.RenameException("Identifier:database-1-instance-1 \nDBInstanceNotFound")

    def test_rename_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.modify_db_instance.return_value = {}
        data = rename_function.lambda_rename_dbinstance(self.event, {})
        self.assertEqual(data["taskname"], "Rename")
        self.assertEqual(data["identifier"], self.updated_instance_id)

    def test_rename_revert_success(self, mock_client):
        # test revert of the initial rename operation
        # incase of failure of restore operation
        mock_rds = mock_client.return_value
        mock_rds.modify_db_instance.return_value = {}
        data = rename_function.lambda_rename_dbinstance(self.revert_event, {})
        self.assertEqual(data["taskname"], "Rename")
        self.assertEqual(data["identifier"], self.original_instance_id)

    def test_rename_rateexceeded_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.modify_db_instance.side_effect = Exception("throttling error: Rate exceeded")
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = rename_function.lambda_rename_dbinstance(self.event, {})
            self.assertEqual(err.exception, self.mocked_rate_exceeded_exception)

    def test_rename_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.modify_db_instance.side_effect = Exception("DBInstanceNotFound")
        with self.assertRaises(custom_exceptions.RenameException) as err:
            _ = rename_function.lambda_rename_dbinstance(self.event, {})
            self.assertEqual(err.exception, self.mocked_rate_exceeded_exception)
