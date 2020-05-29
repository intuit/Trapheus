import os
import unittest
from mock import patch,Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/delete')))
import mock_import
import cluster_delete_function

class TestResourceProvider(unittest.TestCase):
    def test_delete_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_delete_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "Delete", "identifier": "database-1-temp"}
        mock_response.describe_db_clusters.return_value = {"DBClusters": [{"DBClusterIdentifier": "database-1-temp", "DBClusterMembers": [{"DBInstanceIdentifier": "database-1-instance-1-temp", "IsClusterWriter": True, "PromotionTier": 123}]}]}
        mock_response.delete_db_instance.return_value = {}
        event = create_event()
        data = cluster_delete_function.lambda_delete_dbcluster(event, {})
        self.assertEqual(data.get("taskname"), "Delete")
        self.assertEqual(data.get("identifier"), "database-1-temp")

    def test_delete_rateexceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_delete_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBClusterIdentifier:database-1-temp \nthrottling error: Rate exceeded")
        mock_response.side_effect = Exception("DBClusterIdentifier:database-1-temp \nthrottling error: Rate exceeded")
        event = create_event()
        try:
            cluster_delete_function.lambda_delete_dbcluster(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBClusterIdentifier:database-1-temp \nthrottling error: Rate exceeded")

    def test_delete_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_delete_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBClusterIdentifier:database-1-temp \nDBClusterNotFound")
        mock_response.side_effect = Exception("DBClusterIdentifier:database-1-temp \nDBClusterNotFound")
        event = create_event()
        try:
            cluster_delete_function.lambda_delete_dbcluster(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBClusterIdentifier:database-1-temp \nDBClusterNotFound")

def create_event():
    event = { "identifier": "database-1"}
    return event