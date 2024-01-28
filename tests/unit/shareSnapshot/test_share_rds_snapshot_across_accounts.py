import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../src/common/python')))
import custom_exceptions
from mock import patch
from shareSnapshot import share_rds_snapshot_across_accounts

os.environ["Region"] = "us-west-2"
os.environ['SHARE_SNAPSHOT_TASK_ROLE'] = "ssm-automation-role"

@patch("shareSnapshot.share_rds_snapshot_across_accounts.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.event = {"identifier": "database-1", "targetAccountIds": "123452"}
        self.instance_id = "database-1"
        self.share_snapshot_exception = custom_exceptions.SSMShareSnapshotException("IAM role unauthorised to execute ssm automation")
        self.mocked_start_ssm_automation = {
            'AutomationExecutionId': 'execution345'
        }

    def test_share_snapshot_success(self, mock_client):
        mock_ssm = mock_client.return_value
        mock_ssm.start_automation_execution.return_value = self.mocked_start_ssm_automation
        data = share_rds_snapshot_across_accounts.lambda_share_rds_snapshot_cross_account(self.event, {})
        self.assertEqual(data.get("identifier"), self.instance_id)
        self.assertEqual(data.get("automation_execution_id"), "execution345")

    def test_share_snapshot_ssm_execution_failure(self, mock_client):
        mock_ssm = mock_client.return_value
        mock_ssm.start_automation_execution.side_effect = Exception("IAM role unauthorised to execute ssm automation")
        with self.assertRaises(custom_exceptions.SSMShareSnapshotException) as err:
            _ = share_rds_snapshot_across_accounts.lambda_share_rds_snapshot_cross_account(self.event, {})
            self.assertEqual(err.exception, self.dbinstance_creation_exception)