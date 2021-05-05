import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import custom_exceptions
from checkstatus import get_dbstatus_function
from mock import patch, Mock

os.environ["Region"] = "us-west-2"

class ContextManager:
    def __init__(self, seconds):
        self.seconds = seconds

    def get_remaining_time_in_millis(self):
        return --self.seconds * 1000

@patch("checkstatus.get_dbstatus_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.mock_waiter = Mock()
        self.task_complete = "TASK_COMPLETE"
        self.task_failed = "TASK_FAILED"
        self.mock_rateexceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1 \nWaiter database-1 Max attempts exceeded")
        self.mock_instance_not_found_failure = custom_exceptions.InstanceUnavailableException("Identifier:database-1 \nWaiter database-1 not found")
        self.mock_snapshot_creation_failure_status = "Identifier:database-1 \nWaiter encountered a terminal failure state"

    def test_get_dbstatus_delete_success(self, mock_client):
        # test successful delete of the db cluster
        mock_rds = mock_client.return_value
        mock_rds.get_waiter.return_value = self.mock_waiter
        event = {"output": {"taskname": "Delete", "identifier": "database-1"}}
        context = ContextManager(20)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), "Delete")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), self.task_complete)

    def test_get_dbstatus_delete_failure(self, mock_client):
        # test rds waiter max attempt limit post deleting a db cluster
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter database-1 Max attempts exceeded")
        event = {"output": {"taskname": "Delete", "identifier": "database-1"}}
        context = ContextManager(50)
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
            self.assertEqual(err.exception, self.mock_rateexceeded_exception)

    def test_get_dbstatus_rename_success(self, mock_client):
        #test availability status of db instance post rename operation
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        event = {"output": {"taskname": "Rename", "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), "Rename")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), self.task_complete)

    def test_get_dbstatus_snapshot_success(self, mock_client):
        #test successful availability of db snapshot post create operation
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        event = {"output": {"taskname": "SnapshotCreation", "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), self.task_complete)

    def test_get_dbstatus_snapshot_failure(self, mock_client):
        #test failure of rds waiter post db snapshot creation
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter encountered a terminal failure state")
        event = {"output": {"taskname": "SnapshotCreation", "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("status"), self.mock_snapshot_creation_failure_status)
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), self.task_failed)

    def test_get_dbstatus_restore_failed(self, mock_client):
        #test failure of rds waiter post db instance restore operation
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter encountered a terminal failure state")
        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(55)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), "Restore")
        self.assertEqual(data.get("status"), self.mock_snapshot_creation_failure_status)
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), self.task_failed)

    def test_get_dbstatus_restore_instance_not_found(self, mock_client):
        #test instance not found exception while checking status post any db instance operation
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter database-1 not found")
        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(25)
        with self.assertRaises(custom_exceptions.InstanceUnavailableException) as err:
            _ = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
            self.assertEqual(err.exception, self.mock_instance_not_found_failure)

    def test_get_dbstatus_restore_max_attempts_exceeded_failure(self, mock_client):
        #test rate limiting while checking status post any operation
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter database-1 Max attempts exceeded")
        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(40)
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
            self.assertEqual(err.exception, self.mock_rateexceeded_exception)