import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/snapshot')))
import mock_import
import cluster_snapshot_function

class TestResourceProvider(unittest.TestCase):
    def test_snapshot_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "SnapshotCreation", "identifier": "database-1"}
        event = create_event()
        data = cluster_snapshot_function.lambda_create_cluster_snapshot(event, {})
        self.assertEqual(data.get("taskname"), "SnapshotCreation")
        self.assertEqual(data.get("identifier"), "database-1")

    def test_snapshot_rateexceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("Identifier:database-1 \nthrottling error: Rate exceeded")
        mock_response.side_effect = Exception("Identifier:database-1 \nthrottling error: Rate exceeded")
        event = create_event()
        try:
            cluster_snapshot_function.lambda_create_cluster_snapshot(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nthrottling error: Rate exceeded")

    def test_snapshot_duplicate_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("Identifier:database-1 \nDBClusterSnapshotAlreadyExistsFault")
        mock_response.side_effect = Exception("Identifier:database-1 \nDBClusterSnapshotAlreadyExistsFault")
        event = create_event()
        try:
            cluster_snapshot_function.lambda_create_cluster_snapshot(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nDBClusterSnapshotAlreadyExistsFault")

    def test_snapshot_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_snapshot_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("Identifier:database-1 \nTimeoutException")
        mock_response.side_effect = Exception("Identifier:database-1 \nTimeoutException")
        event = create_event()
        try:
            cluster_snapshot_function.lambda_create_cluster_snapshot(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "Identifier:database-1 \nTimeoutException")

def create_event():
    event = { "identifier": "database-1"}
    return event