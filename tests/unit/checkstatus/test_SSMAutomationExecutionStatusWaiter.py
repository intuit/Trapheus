import os
import sys
import unittest
import pytest
import botocore.waiter
from botocore.exceptions import WaiterError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/checkstatus')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/common/python')))
from checkstatus import SSMAutomationExecutionStatusWaiter
from mock import patch, Mock


@patch.object(botocore.waiter, 'create_waiter_with_client')
class TestResourceProvider(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.automation_execution_id = "execution-123"

    def test_waiter_creation_failure(self, mock_waiter_client):
        mock_waiter_client.side_effect = WaiterError('TestWaiter', 'Invalid boto3 client', 'sample')
        with pytest.raises(Exception):
            _ = SSMAutomationExecutionStatusWaiter.check_automation_execution_status(self.automation_execution_id, 5,
                                                                                     self.mock_client)

    def test_waiter_execution_failure(self, mock_waiter_client):
        mock_waiter_client.return_value = self.mock_client
        waiter = mock_waiter_client.return_value
        waiter.wait.side_effect = WaiterError('TestWaiter', 'Waiter encountered a terminal failure state', 'sample')
        with pytest.raises(Exception) as err:
            _ = SSMAutomationExecutionStatusWaiter.check_automation_execution_status(self.automation_execution_id, 5,
                                                                                     self.mock_client)
