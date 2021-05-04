import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import custom_exceptions
from mock import patch
from restore import cluster_restore_function

os.environ["Region"] = "us-west-2"

@patch("restore.cluster_restore_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1-temp"}
        self.cluster_id = "database-1"
        self.mocked_rate_exceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1 \nthrottling error: Rate exceeded")
        self.mocked_cluster_not_found_exception = custom_exceptions.ClusterRestoreException("Identifier:database-1 \nDBClusterNotFound")
        self.cluster_restore_exception = custom_exceptions.ClusterRestoreException("Identifier:database-1 \nCluster restoration failed")
        self.dbinstance_creation_exception = custom_exceptions.ClusterRestoreException("Identifier:database-1-instance-1 \nDBInstance creation failed")
        self.mocked_describe_db_clusters = {
            "ResponseMetadata": {
                'HTTPStatusCode': 200
            },
            "DBClusters": [{
                "DBClusterIdentifier": "database-1-temp",
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
                    "DBInstanceIdentifier": "database-1-instance-1-temp",
                    "IsClusterWriter": True,
                    "PromotionTier": 123
                }]
            }]
        }

        self.mocked_describe_db_instances = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            "DBInstances": [{
                "DBInstanceIdentifier": "database-1-instance-1-temp",
                "DBInstanceClass": "postgres-ee"
            }]
        }

    def test_restore_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.describe_db_instances.return_value = self.mocked_describe_db_instances
        mock_rds.restore_db_cluster_from_snapshot.return_value = {}
        mock_rds.create_db_instance.return_value = {}
        data = cluster_restore_function.lambda_restore_dbcluster(self.event, {})
        self.assertEqual(data.get("taskname"), "ClusterRestore")
        self.assertEqual(data.get("identifier"), self.cluster_id)

    def test_restore_rateexceeded_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.restore_db_cluster_from_snapshot.side_effect = Exception("throttling error: Rate exceeded")
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = cluster_restore_function.lambda_restore_dbcluster(self.event, {})
            self.assertEqual(err.exception, self.mocked_rate_exceeded_exception)

    def test_restore_cluster_not_found_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.side_effect = Exception("DBClusterNotFound")
        with self.assertRaises(custom_exceptions.ClusterRestoreException) as err:
            _ = cluster_restore_function.lambda_restore_dbcluster(self.event, {})
            self.assertEqual(err.exception, self.mocked_cluster_not_found_exception)

    def test_restore_cluster_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.restore_db_cluster_from_snapshot.side_effect = Exception("Cluster restoration failed")
        with self.assertRaises(custom_exceptions.ClusterRestoreException) as err:
            _ = cluster_restore_function.lambda_restore_dbcluster(self.event, {})
            self.assertEqual(err.exception, self.cluster_restore_exception)

    def test_restore_instance_creation_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.create_db_instance.side_effect = Exception("DBInstance creation failed")
        with self.assertRaises(custom_exceptions.ClusterRestoreException) as err:
            _ = cluster_restore_function.lambda_restore_dbcluster(self.event, {})
            self.assertEqual(err.exception, self.dbinstance_creation_exception)
