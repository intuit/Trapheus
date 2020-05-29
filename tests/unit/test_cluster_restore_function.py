import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/restore')))
import mock_import
import cluster_restore_function

class TestResourceProvider(unittest.TestCase):
    def test_restore_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_restore_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "ClusterRestore", "identifier": "database-1"}
        mock_factory_boto_client.describe_db_clusters.return_value = mock_response
        mock_response.describe_db_clusters.return_value = {"DBClusters": [{"DBClusterIdentifier": "database-1-temp","DatabaseName": "POSTGRES", "Port": 3306, "Engine": "xyzz", "EngineVersion": 10.7, "VpcSecurityGroups": [{"VpcSecurityGroupId": "abc"}],"DBSubnetGroup": {"DBSubnetGroupName": "xyz"}, "DBClusterMembers": [{"DBInstanceIdentifier": "database-1-instance-1-temp", "IsClusterWriter": True, "PromotionTier": 123}]}]}
        mock_response.describe_db_instances.return_value = {"DBInstances": [{"DBInstanceIdentifier": "database-1-instance-1-temp", "DBInstanceClass": "postgres-ee"}]}
        event = {"identifier": "database-1-temp"}
        data = cluster_restore_function.lambda_restore_dbcluster(event, {})
        self.assertEqual(data.get("taskname"), "ClusterRestore")
        self.assertEqual(data.get("identifier"), "database-1")

    def test_restore_rateexceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_restore_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")
        event = create_event()
        try:
            cluster_restore_function.lambda_restore_dbcluster(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1 \nthrottling error: Rate exceeded")

    def test_restore_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('cluster_restore_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1 \nDBInstanceNotFound")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1 \nDBInstanceNotFound")
        event = create_event()
        try:
            cluster_restore_function.lambda_restore_dbcluster(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1 \nDBInstanceNotFound")

def create_event():
    event = { "identifier": "database-1"}
    return event