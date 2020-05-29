import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/checkstatus')))
import mock_import
import get_dbcluster_status_function

class ContextManager:
    def __init__(self, seconds):
        self.seconds = seconds

    def get_remaining_time_in_millis(self):
        return --self.seconds * 1000

class TestResourceProvider(unittest.TestCase):
    def test_get_dbstatus_delete_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter
        event = {"output": {"taskname": "Delete", "identifier": "database-1"}}
        context = ContextManager(145)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), "Delete")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), "TASK_COMPLETE")

    def test_get_dbstatus_rename_success(self):
        os.environ["Region"] = "us-west-2"
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
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter
        mock_response.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = mock_waiter
        event = {"output": {"taskname": "Rename", "identifier": "database-1"}}
        context = ContextManager(145)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), "Rename")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), "TASK_COMPLETE")

    def test_get_dbstatus_rename_failure(self):
        os.environ["Region"] = "us-west-2"
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
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter database-1-instance-1 Max attempts exceeded")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": "Rename", "identifier": "database-1"}}
        context = ContextManager(45)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1-instance-1 Max attempts exceeded")

    def test_get_dbstatus_snapshot_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = mock_waiter
        event = {"output": {"taskname": "SnapshotCreation", "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), "TASK_COMPLETE")

    def test_get_dbstatus_snapshot_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter = Mock()
        mock_response.get_waiter.return_value = mock_waiter
        waiter_error = Exception("Waiter encountered a terminal failure state")
        mock_waiter.wait.side_effect = waiter_error
        event = {"output": {"taskname": "SnapshotCreation", "identifier": "database-1"}}
        context = ContextManager(45)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter encountered a terminal failure state")

    def test_get_dbstatus_restore_failed(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        waiter_error = Exception("Waiter encountered a terminal failure state")
        mock_waiter_client.check_dbcluster_status.side_effect = waiter_error
        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), "Restore")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), "TASK_FAILED")

    def test_cluster_unavailable(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        waiter_error = Exception("Waiter database-1 not found")
        mock_waiter_client.check_dbcluster_status.side_effect = waiter_error
        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(45)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1 not found")

    def test_get_dbstatus_restore_max_attempts_exceeded(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('get_dbcluster_status_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_waiter_patch = patch('get_dbcluster_status_function.DBClusterStatusWaiter')
        mock_waiter_client = mock_waiter_patch.start()
        waiter_error = Exception("Waiter database-1 Max attempts exceeded")
        mock_waiter_client.check_dbcluster_status.side_effect = waiter_error
        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(55)
        try:
            get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nWaiter database-1 Max attempts exceeded")