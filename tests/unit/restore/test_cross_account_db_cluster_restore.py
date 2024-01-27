import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import custom_exceptions
from mock import patch
from restore import cross_account_db_cluster_restore

os.environ["Region"] = "us-west-2"

@patch("restore.cross_account_db_cluster_restore.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1", "vpcId": "vpc-2342432",
                      "AutomationAssumeRole": "role", "targetAccountIds": "123452", "targetRegions": "us-west-2"}
        self.instance_id = "database-1"
        self.mocked_cluster_not_found_exception = custom_exceptions.ClusterRestoreException("Identifier:database-1 \nDBClusterNotFound")
        self.dbcluster_creation_exception = custom_exceptions.ClusterRestoreException("Role unauthorised to restore rds instance in target account")
        self.mocked_start_ssm_automation = {
            'AutomationExecutionId': 'execution123'
        }

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

        self.mocked_describe_db_instances = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            "DBInstances": [{
                "DBInstanceIdentifier": "database-1-instance-1",
                "DBInstanceClass": "postgres-ee"
            }]
        }

    def test_restore_success(self, mock_client):
        mock_ssm = mock_client.return_value
        mock_rds = mock_client.return_value
        mock_ssm.start_automation_execution.return_value = self.mocked_start_ssm_automation
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.describe_db_instances.return_value = self.mocked_describe_db_instances
        data = cross_account_db_cluster_restore.lambda_restore_rds_cluster_target_account(self.event, {})
        self.assertEqual(data.get("identifier"), self.instance_id)
        self.assertEqual(data.get("restoreRDSAutomationExecutionId"), "execution123")

    def test_restore_cluster_not_found_failure(self, mock_client):
        mock_ssm = mock_client.return_value
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.side_effect = Exception("DBClusterNotFound")
        with self.assertRaises(custom_exceptions.ClusterRestoreException) as err:
            _ = cross_account_db_cluster_restore.lambda_restore_rds_cluster_target_account(self.event, {})
            self.assertEqual(err.exception, self.mocked_cluster_not_found_exception)

    def test_restore_ssm_execution_failure(self, mock_client):
        mock_ssm = mock_client.return_value
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.describe_db_instances.return_value = self.mocked_describe_db_instances
        mock_ssm.start_automation_execution.side_effect = Exception("Role unauthorised to restore rds instance in target account")
        with self.assertRaises(custom_exceptions.ClusterRestoreException) as err:
            _ = cross_account_db_cluster_restore.lambda_restore_rds_cluster_target_account(self.event, {})
            self.assertEqual(err.exception, self.dbcluster_creation_exception)