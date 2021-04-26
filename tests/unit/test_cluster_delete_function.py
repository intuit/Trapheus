import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/common/python')))
import constants
import custom_exceptions
from delete import cluster_delete_function
from mock import patch

os.environ["Region"] = "us-west-2"

@patch("delete.cluster_delete_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = { 'identifier' : 'database-1' }
        self.cluster_id = self.event['identifier'] + constants.TEMP_POSTFIX
        self.mocked_rate_exceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1-temp \nthrottling error: Rate exceeded")
        self.mocked_cluster_not_found_exception = custom_exceptions.DeletionException("Identifier:database-1-temp \nDBClusterNotFound")
        self.mocked_instance_not_found_exception = custom_exceptions.DeletionException("Identifier:database-1-temp \nInstanceDeletionFailure")
        self.mocked_describe_db_clusters = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'DBClusters': [{
                "DBClusterIdentifier": "database-1-temp",
                "DBClusterMembers": [{
                    "DBInstanceIdentifier": "database-1-instance-1-temp",
                    "IsClusterWriter": True,
                    "PromotionTier": 123
                }]
            }]
        }

    def test_delete_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.delete_db_instance.return_value = {}
        data = cluster_delete_function.lambda_delete_dbcluster(self.event, {})
        self.assertEqual(data['taskname'], "Delete")
        self.assertEqual(data['identifier'], self.cluster_id)

    def test_delete_rateexceeded_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.delete_db_cluster.side_effect = Exception("throttling error: Rate exceeded")
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = cluster_delete_function.lambda_delete_dbcluster(self.event, {})
            self.assertEqual(err, self.mocked_rate_exceeded_exception)

    def test_cluster_delete_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = {}
        mock_rds.delete_db_cluster.side_effect = Exception("DBClusterNotFound")
        with self.assertRaises(custom_exceptions.DeletionException) as err:
            _ = cluster_delete_function.lambda_delete_dbcluster(self.event, {})
            self.assertEqual(err, self.mocked_cluster_not_found_exception)

    def test_instance_delete_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = {}
        mock_rds.delete_db_cluster.side_effect = Exception("InstanceDeletionFailure")
        with self.assertRaises(custom_exceptions.DeletionException) as err:
            _ = cluster_delete_function.lambda_delete_dbcluster(self.event, {})
            self.assertEqual(err, self.mocked_instance_not_found_exception)
