import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/checkstatus')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/common/python')))
import custom_exceptions
from checkstatus import get_automation_execution_status
from mock import patch, Mock

os.environ["Region"] = "us-west-2"

class ContextManager:
    def __init__(self, seconds):
        self.seconds = seconds

    def get_remaining_time_in_millis(self):
        return --self.seconds * 1000

@patch("checkstatus.get_automation_execution_status.boto3.client")
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.mock_waiter = Mock()
        self.task_complete = "TASK_COMPLETE"
        self.task_failed = "TASK_FAILED"
        self.mock_automation_not_found_failure = custom_exceptions.SSMAutomationExecutionException(
            "Specified value for ExecutionId is not valid")
        self.mock_automation_execution_failure = custom_exceptions.SSMAutomationExecutionException(
            "Waiter encountered a terminal failure state")
        self.mocked_describe_automation_execution_success = {
            "ResponseMetadata": {
                'HTTPStatusCode': 200
            },
            "AutomationExecutionMetadataList": [
                {
                    "AutomationExecutionId": "execution-123",
                    "DocumentName": "trapheus",
                    "DocumentVersion": "2",
                    "AutomationExecutionStatus": "Success"
                }
            ]
        }

        self.mocked_describe_automation_execution_failure = {
            "ResponseMetadata": {
                'HTTPStatusCode': 200
            },
            "AutomationExecutionMetadataList": [
                {
                    "AutomationExecutionId": "execution-123",
                    "DocumentName": "trapheus",
                    "DocumentVersion": "2",
                    "AutomationExecutionStatus": "Failed"
                }
            ]
        }

    @patch('checkstatus.get_automation_execution_status.SSMAutomationExecutionStatusWaiter')
    def test_get_automation_execution_status_success(self, mock_waiter_patch, mock_client):
        # test successful completion of the automation execution
        mock_ssm = mock_client.return_value
        mock_ssm.describe_automation_executions.return_value = self.mocked_describe_automation_execution_success
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter_client.check_dbcluster_status.return_value = self.mock_waiter
        mock_ssm.get_waiter.return_value = self.mock_waiter

        event = {"output": {"automation_execution_id": "execution-123", "taskname": "ShareSnapshot"}}
        context = ContextManager(20)
        data = get_automation_execution_status.lambda_get_automation_execution_status(event, context)
        self.assertEqual(data.get("taskname"), "ShareSnapshot")
        self.assertEqual(data.get("task"), self.task_complete)

    @patch('checkstatus.get_automation_execution_status.SSMAutomationExecutionStatusWaiter')
    def test_get_automation_execution_status_failure(self, mock_waiter_patch, mock_client):
        # # test failure for automation execution
        mock_ssm = mock_client.return_value
        mock_ssm.describe_automation_executions.return_value = self.mocked_describe_automation_execution_failure
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter = self.mock_waiter
        # mock_waiter.wait.side_effect = Exception("Waiter encountered a terminal failure state")
        mock_waiter_client.check_automation_execution_status.return_value = mock_waiter
        mock_ssm.get_waiter.return_value = mock_waiter
        event = {"output": {"automation_execution_id": "execution-123", "taskname": "abc"}}
        context = ContextManager(45)
        with self.assertRaises(Exception) as err:
            _ = get_automation_execution_status.lambda_get_automation_execution_status(event, context)
            self.assertEqual(err.exception, self.mock_automation_execution_failure)

    @patch('checkstatus.get_automation_execution_status.SSMAutomationExecutionStatusWaiter')
    def test_get_automation_execution_status_automation_not_found(self, mock_waiter_patch, mock_client):
        # test automation id not found exception while checking completion of the automation execution
        mock_waiter = self.mock_waiter
        mock_ssm = mock_client.return_value
        mock_waiter_client = mock_waiter_patch.start()
        mock_waiter_client.describe_automation_executions.side_effect = Exception(
            "Specified value for ExecutionId is not valid")
        mock_waiter_client.check_automation_execution_status.return_value = mock_waiter
        mock_ssm.get_waiter.return_value = mock_waiter
        event = {"output": {"automation_execution_id": "execution-124", "taskname": "abc"}}
        context = ContextManager(25)
        with self.assertRaises(Exception) as err:
            _ = get_automation_execution_status.lambda_get_automation_execution_status(event, context)
            self.assertEqual(err.exception, self.mock_automation_not_found_failure)
