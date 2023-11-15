import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import custom_exceptions
from mock import patch
from restore import cross_account_db_restore

os.environ["Region"] = "us-west-2"

@patch("restore.cross_account_db_restore.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1", "vpcId": "vpc-2342432",
                      "AutomationAssumeRole": "role", "targetAccountIds": "123452", "targetRegions": "us-west-2"}
        self.instance_id = "database-1"
        self.dbinstance_creation_exception = custom_exceptions.InstanceRestoreException("Role unauthorised to restore rds instance in target account")
        self.mocked_start_ssm_automation = {
            'AutomationExecutionId': 'execution123'
        }

    def test_restore_success(self, mock_client):
        mock_ssm = mock_client.return_value
        mock_ssm.start_automation_execution.return_value = self.mocked_start_ssm_automation
        data = cross_account_db_restore.lambda_restore_rds_target_account(self.event, {})
        self.assertEqual(data.get("identifier"), self.instance_id)
        self.assertEqual(data.get("restoreRDSAutomationExecutionId"), "execution123")

    def test_restore_ssm_execution_failure(self, mock_client):
        mock_ssm = mock_client.return_value
        mock_ssm.start_automation_execution.side_effect = Exception("Role unauthorised to restore rds instance in target account")
        with self.assertRaises(custom_exceptions.InstanceRestoreException) as err:
            _ = cross_account_db_restore.lambda_restore_rds_target_account(self.event, {})
            self.assertEqual(err.exception, self.dbinstance_creation_exception)