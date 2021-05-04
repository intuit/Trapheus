import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import constants
import custom_exceptions
from mock import patch
from rename import cluster_rename_function

os.environ["Region"] = "us-west-2"

@patch("rename.cluster_rename_function.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1"}
        self.revert_event = {"Error": "ClusterRestoreException","Cause": "DBClusterIdentifier:database-1 \n ThrottlingError: Rate exceeded"}
        self.updated_cluster_id = self.event['identifier'] + constants.TEMP_POSTFIX
        self.original_cluster_id = self.event['identifier']
        self.mocked_rate_exceeded_exception = custom_exceptions.RateExceededException("Identifier:database-1-temp \nthrottling error: Rate exceeded")
        self.mocked_cluster_not_found_exception = custom_exceptions.RenameException("Identifier:database-1-temp \nDBClusterNotFound")
        self.mocked_instance_not_found_exception = custom_exceptions.RenameException("Identifier:database-1-temp \nDBInstanceNotFound")
        self.mocked_describe_db_clusters = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'DBClusters': [{
                "DBClusterIdentifier": "database-1",
                "DBClusterMembers": [{
                    "DBInstanceIdentifier": "database-1-instance-1",
                    "IsClusterWriter": True,
                    "PromotionTier": 123
                }]
            }]
        }

        self.mocked_modify_db_cluster = {
            'ResponseMetadata': {
                'HTTPStatusCode': 200
            },
            'DBClusters': {
                "DBClusterIdentifier": "database-1-temp",
                "Status": "renaming",
                "DBClusterMembers": [{
                    "DBInstanceIdentifier": "database-1-instance-1-temp",
                    "IsClusterWriter": True,
                    "PromotionTier": 123
                }]
            }
        }

    def test_rename_success(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.modify_db_cluster.return_value = self.mocked_modify_db_cluster
        data = cluster_rename_function.lambda_rename_dbcluster(self.event, {})
        self.assertEqual(data['taskname'], "Rename")
        self.assertEqual(data['identifier'], self.updated_cluster_id)

    @patch("utility.get_modified_identifier", return_value={"instance_id" : "database-1-instance-1"})
    @patch("utility.get_identifier_from_error", return_value={"modified_identifier" : "database-1", "original_identifier": "database-1-temp"})
    def test_rename_revert_success(self, mock_get_identifier_from_error, mock_get_modified_identifier, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.modify_db_cluster.return_value = self.mocked_modify_db_cluster
        data = cluster_rename_function.lambda_rename_dbcluster(self.revert_event, {})
        self.assertEqual(data['taskname'], "Rename")
        self.assertEqual(data['identifier'], self.original_cluster_id)

    def test_rename_rateexceeded_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.modify_db_cluster.side_effect = Exception("throttling error: Rate exceeded")
        with self.assertRaises(custom_exceptions.RateExceededException) as err:
            _ = cluster_rename_function.lambda_rename_dbcluster(self.event, {})
            self.assertEqual(err.exception, self.mocked_rate_exceeded_exception)

    def test_rename_cluster_not_found_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.modify_db_cluster.side_effect = Exception("DBClusterNotFound")
        with self.assertRaises(custom_exceptions.RenameException) as err:
            _ = cluster_rename_function.lambda_rename_dbcluster(self.event, {})
            self.assertEqual(err.exception, self.mocked_cluster_not_found_exception)

    def test_rename_instance_not_found_failure(self, mock_client):
        mock_rds = mock_client.return_value
        mock_rds.describe_db_clusters.return_value = self.mocked_describe_db_clusters
        mock_rds.modify_db_instance.side_effect = Exception("DBInstanceNotFound")
        with self.assertRaises(custom_exceptions.RenameException) as err:
            _ = cluster_rename_function.lambda_rename_dbcluster(self.event, {})
            self.assertEqual(err.exception, self.mocked_instance_not_found_exception)
