import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/checkstatus')))
import mock_import
import get_dbcluster_status_function
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
        mock_response, mock_waiter = self._create_mock_response_and_waiter()
        self._set_mock_waiter_client_behavior(mock_waiter)
        self._test_success(constants.DELETE)

    def test_get_dbstatus_rename_success(self):
        os.environ["Region"] = "us-west-2"
        mock_response, mock_waiter = self._create_mock_response_and_waiter()
        mock_response.describe_db_clusters.return_value = {
            "DBClusters":
                [
                    {
                        "DBClusterIdentifier": "database-1",
                        "Status": "available",
                        "DBClusterMembers":
                         [
                             {
                                 "DBInstanceIdentifier": "database-1-instance-1"
                             }
                         ]
                    }
                ]
            }
        self._set_mock_waiter_client_behavior(mock_waiter)
        self._mock_response_behavior_and_test_success(mock_response, mock_waiter, constants.RENAME)

    def test_get_dbstatus_rename_failure(self):
        os.environ["Region"] = "us-west-2"
        taskname = constants.RENAME
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.describe_db_clusters.return_value = {
            "DBClusters":
                [
                    {
                        "DBClusterIdentifier": "database-1",
                        "Status": "available",
                        "DBClusterMembers":
                            [
                                {
                                    "DBInstanceIdentifier": "database-1-instance-1"
                                }
                            ]
                    }
                ]
        }
        mock_waiter = Mock()
        self._set_mock_waiter_client_behavior(mock_waiter)
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter database-1-instance-1 Max attempts exceeded")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(45)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1-instance-1 Max attempts exceeded")

    def test_get_dbstatus_snapshot_success(self):
        os.environ["Region"] = "us-west-2"
        mock_response, mock_waiter = self._create_mock_response_and_waiter()
        self._mock_response_behavior_and_test_success(mock_response, mock_waiter, "SnapshotCreation")

    def test_get_dbstatus_copy_snapshot_success(self):
        os.environ["ExportSnapshotSupportedRegion"] = "eu-west-1"
        mock_response, mock_waiter = self._create_mock_response_and_waiter()
        self._mock_response_behavior_and_test_success(mock_response, mock_waiter, constants.COPY_SNAPSHOT)

    def test_get_dbstatus_snapshot_failure(self):
        os.environ["Region"] = "us-west-2"
        self._test_snapshot_failure("SnapshotCreation")

    def test_get_dbstatus_copy_snapshot_failure(self):
        os.environ["ExportSnapshotSupportedRegion"] = "eu-west-1"
        self._test_snapshot_failure(constants.COPY_SNAPSHOT)

    def _test_snapshot_failure(self, taskname):
        mock_response, mock_waiter = self._create_mock_response_and_waiter()
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter encountered a terminal failure state")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(45)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter encountered a terminal failure state")

    def test_get_dbstatus_restore_failed(self):
        os.environ["Region"] = "us-west-2"
        taskname = constants.DB_RESTORE
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        waiter_error = Exception("Waiter encountered a terminal failure state")
        mock_waiter_client.check_dbcluster_status.side_effect = waiter_error
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), taskname)
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), constants.TASK_FAILED)

    def test_cluster_unavailable(self):
        os.environ["Region"] = "us-west-2"
        taskname = constants.DB_RESTORE
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        waiter_error = Exception("Waiter database-1 not found")
        mock_waiter_client.check_dbcluster_status.side_effect = waiter_error
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(45)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1 not found")

    def test_get_dbstatus_restore_max_attempts_exceeded(self):
        os.environ["Region"] = "us-west-2"
        taskname = constants.DB_RESTORE
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        waiter_error = Exception("Waiter database-1 Max attempts exceeded")
        mock_waiter_client.check_dbcluster_status.side_effect = waiter_error
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(55)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1 Max attempts exceeded")

    def _create_mock_response_and_waiter(self):
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        return mock_response, mock_waiter

    def _set_mock_waiter_client_behavior(self, mock_waiter):
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter

    def _mock_response_behavior_and_test_success(self, mock_response, mock_waiter, taskname):
        mock_response.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = mock_waiter
        self._test_success(taskname)

    def _test_success(self, taskname):
        event = {"output": {"taskname": taskname, "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), taskname)
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), constants.TASK_COMPLETE)
