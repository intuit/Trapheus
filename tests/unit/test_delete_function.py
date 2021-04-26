import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/common/python')))
import custom_exceptions
import constants
from delete import delete_function
from mock import patch

os.environ["Region"] = "us-west-2"

@patch("delete.delete_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1"}
        self.instance_id = self.event['identifier'] + constants.TEMP_POSTFIX
        self.mocked_rate_exceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1-temp \nthrottling error: Rate exceeded")
        self.mocked_instance_not_found_exception = custom_exceptions.SnapshotCreationException("Identifier:database-1-temp \nInstanceNotFoundFault")

    def test_delete_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.delete_db_instance.return_value = {}
        data = delete_function.lambda_delete_dbinstance(self.event, {})
        self.assertEqual(data['taskname'], "Delete")
        self.assertEqual(data['identifier'], self.instance_id)

    def test_delete_rateexceeded_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.delete_db_instance.side_effect = Exception("throttling error: Rate exceeded")
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = delete_function.lambda_delete_dbinstance(self.event, {})
            self.assertEqual(err, self.mocked_rate_exceeded_exception)

    def test_delete_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.delete_db_instance.side_effect = Exception("InstanceNotFoundFault")
        with self.assertRaises(custom_exceptions.DeletionException) as err:
            _ = delete_function.lambda_delete_dbinstance(self.event, {})
            self.assertEqual(err, self.mocked_instance_not_found_exception)
