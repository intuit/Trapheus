import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/checkstatus')))
import mock_import
import get_dbstatus_function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/common/python')))
import constants

class ContextManager:
    def __init__(self, seconds):
        self.seconds = seconds

    def get_remaining_time_in_millis(self):
        return --self.seconds * 1000

class TestResourceProvider(unittest.TestCase):
    def test_get_dbstatus_delete_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbstatus_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = mock_waiter
        event = {"output": {"taskname": constants.DELETE, "identifier": "database-1"}}
        context = ContextManager(20)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), constants.DELETE)
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), constants.TASK_COMPLETE)

    def test_get_dbstatus_delete_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbstatus_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter database-1 Max attempts exceeded")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": constants.DELETE, "identifier": "database-1"}}
        context = ContextManager(50)
        try:
            get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1 Max attempts exceeded")

    def test_get_dbstatus_rename_success(self):
        os.environ["Region"] = "us-west-2"
        self._test_success(constants.RENAME)

    def test_get_dbstatus_snapshot_success(self):
        os.environ["Region"] = "us-west-2"
        self._test_success("SnapshotCreation")

    def test_get_dbstatus_snapshot_failure(self):
        os.environ["Region"] = "us-west-2"
        self._test_snapshot_failure("SnapshotCreation")

    def test_get_dbstatus_copy_snapshot_success(self):
        os.environ["ExportSnapshotSupportedRegion"] = "eu-west-1"
        self._test_success(constants.COPY_SNAPSHOT)

    def _test_success(self, taskname):
        factory_patch = patch('get_dbstatus_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = mock_waiter
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), taskname)
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), constants.TASK_COMPLETE)

    def test_get_dbstatus_copy_snapshot_failure(self):
        os.environ["ExportSnapshotSupportedRegion"] = "eu-west-1"
        self._test_snapshot_failure(constants.COPY_SNAPSHOT)

    def _test_snapshot_failure(self, taskname):
        factory_patch = patch('get_dbstatus_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter encountered a terminal failure state")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), taskname)
        self.assertEqual(data.get("status"), "Identifier:database-1 \nWaiter encountered a terminal failure state")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), constants.TASK_FAILED)

    def test_get_dbstatus_restore_failed(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbstatus_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter encountered a terminal failure state")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": constants.DB_RESTORE, "identifier": "database-1"}}
        context = ContextManager(55)
        data = get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        self.assertEqual(data.get("taskname"), constants.DB_RESTORE)
        self.assertEqual(data.get("status"), "Identifier:database-1 \nWaiter encountered a terminal failure state")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), constants.TASK_FAILED)

    def test_get_dbstatus_restore_instance_not_found(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbstatus_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response = Mock(name='response')
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter database-1 not found")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": constants.DB_RESTORE, "identifier": "database-1"}}
        context = ContextManager(25)
        try:
            get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1 not found")

    def test_get_dbstatus_restore_max_attempts_exceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbstatus_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter database-1 Max attempts exceeded")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": constants.DB_RESTORE, "identifier": "database-1"}}
        context = ContextManager(40)
        try:
            get_dbstatus_function.lambda_get_dbinstance_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1 Max attempts exceeded")
