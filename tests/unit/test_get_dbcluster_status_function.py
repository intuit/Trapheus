import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/checkstatus')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/common/python')))
import custom_exceptions
from checkstatus import get_dbcluster_status_function

os.environ["Region"] = "us-west-2"

class ContextManager:
    def __init__(self, seconds):
        self.seconds = seconds

    def get_remaining_time_in_millis(self):
        return --self.seconds * 1000

@patch("checkstatus.get_dbcluster_status_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.mock_waiter = Mock()
        self.task_complete = "TASK_COMPLETE"
        self.task_failed = "TASK_FAILED"
        self.mock_rateexceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1 \nWaiter database-1 Max attempts exceeded")
        self.mock_instance_not_found_failure = custom_exceptions.InstanceUnavailableException("Identifier:database-1 \nWaiter database-1 not found")
        self.mock_snapshot_creation_failure_status = "Identifier:database-1 \nWaiter encountered a terminal failure state"
        self.mocked_describe_db_clusters = {
            "ResponseMetadata": {
                'HTTPStatusCode': 200
            },
            "DBClusters": [{
                "DBClusterIdentifier": "database-1",
                "DatabaseName": "POSTGRES",
                "Port": 3306,
                "Engine": "xyzz",
                "EngineVersion": 10.7,
                "VpcSecurityGroups": [{
                    "VpcSecurityGroupId": "abc"
                }],
                "DBSubnetGroup": {
                    "DBSubnetGroupName": "xyz"
                },
                "DBClusterMembers": [{
                    "DBInstanceIdentifier": "database-1-instance-1",
                    "IsClusterWriter": True,
                    "PromotionTier": 123
                }]
            }]
        }

    def test_get_dbstatus_delete_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.get_waiter.return_value = self.mock_waiter
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter database-1 not found")
        event = {"output": {"taskname": "Delete", "identifier": "database-1"}}
        context = ContextManager(145)
        with self.assertRaises(custom_exceptions.DeletionException) as err:
            data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
            self.assertEqual(err.exception, self.mock_instance_not_found_failure)
            self.assertEqual(data.get("taskname"), "Delete")
            self.assertEqual(data.get("identifier"), "database-1")
            self.assertEqual(data.get("task"), "TASK_COMPLETE")

    @patch('checkstatus.get_dbcluster_status_function.DBClusterStatusWaiter')
    def test_get_dbstatus_rename_success(self, mock_waiter_patch, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter_client.check_dbcluster_status.return_value = self.mock_waiter
        mock_rds.get_waiter.return_value = self.mock_waiter

        event = {"output": {"taskname": "Rename", "identifier": "database-1"}}
        context = ContextManager(145)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), "Rename")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), "TASK_COMPLETE")

    @patch('checkstatus.get_dbcluster_status_function.DBClusterStatusWaiter')
    def test_get_dbstatus_rename_failure(self, mock_waiter_patch, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter = self.mock_waiter
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter database-1-instance-1 Max attempts exceeded")
        event = {"output": {"taskname": "Rename", "identifier": "database-1"}}
        context = ContextManager(45)
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
            self.assertEqual(err.exception, self.mock_rateexceeded_exception)

    def test_get_dbstatus_snapshot_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.get_waiter.return_value = self.mock_waiter

        event = {"output": {"taskname": "SnapshotCreation", "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), "TASK_COMPLETE")

    def test_get_dbstatus_snapshot_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_waiter = self.mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter encountered a terminal failure state")
        event = {"output": {"taskname": "SnapshotCreation", "identifier": "database-1"}}
        context = ContextManager(45)
        with self.assertRaises(Exception) as err:
            _ = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
            self.assertEqual(err.exception, self.mock_snapshot_creation_failure_status)

    @patch('checkstatus.get_dbcluster_status_function.DBClusterStatusWaiter')
    def test_get_dbstatus_restore_failed(self, mock_waiter_patch, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter = self.mock_waiter
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter encountered a terminal failure state")

        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(45)
        data = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
        self.assertEqual(data.get("taskname"), "Restore")
        self.assertEqual(data.get("identifier"), "database-1")
        self.assertEqual(data.get("task"), self.task_complete)

    @patch('checkstatus.get_dbcluster_status_function.DBClusterStatusWaiter')
    def test_cluster_unavailable(self, mock_waiter_patch, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter = self.mock_waiter
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter database-1 not found")

        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(45)
        with self.assertRaises(Exception) as err:
            _ = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
            self.assertEqual(err.exception, self.mock_instance_not_found_failure)

    @patch('checkstatus.get_dbcluster_status_function.DBClusterStatusWaiter')
    def test_get_dbstatus_restore_max_attempts_exceeded(self, mock_waiter_patch, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter = self.mock_waiter
        mock_waiter_client.check_dbcluster_status.return_value = mock_waiter
        mock_rds.get_waiter.return_value = mock_waiter
        mock_waiter.wait.side_effect = Exception("Waiter database-1 Max attempts exceeded")
        event = {"output": {"taskname": "Restore", "identifier": "database-1"}}
        context = ContextManager(55)
        with self.assertRaises(Exception) as err:
            _ = get_dbcluster_status_function.lambda_get_cluster_status(event, context)
            self.assertEqual(err.exception, self.mock_rateexceeded_exception)