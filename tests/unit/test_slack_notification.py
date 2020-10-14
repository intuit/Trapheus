import os
import unittest
import mock_import

from mock import patch, Mock
from requests.exceptions import HTTPError

from src.slackNotification import slack_notification


class TestSlackNotification(unittest.TestCase):

    def _mock_response(
            self,
            status=200,
            raise_for_status=None):
        mock_resp = Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        mock_resp.status_code = status
        return mock_resp

    @patch("src.slackNotification.slack_notification.requests")
    def test_send_to_slack_response_success(self, mock_requests):
        mock_response = self._mock_response()
        mock_requests.post.return_value = mock_response
        slack_notification.send_to_slack(["webhook1", "webhook2"], {})
        self.assertEqual(mock_response.raise_for_status.call_count, 2)

    @patch("src.slackNotification.slack_notification.requests")
    def test_send_to_slack_response_failure(self, mock_requests):
        mock_response = self._mock_response(status=500,
                                            raise_for_status=HTTPError(
                                                "Invalid Url"))
        mock_requests.post.return_value = mock_response
        self.assertRaises(HTTPError, slack_notification.send_to_slack,
                          ["webhook1"], {})

    @patch("src.slackNotification.slack_notification.requests")
    def test_send_to_slack_no_webhooks(self, mock_requests):
        mock_response = self._mock_response()
        mock_requests.post.return_value = mock_response
        slack_notification.send_to_slack([], {})
        self.assertFalse(mock_response.raise_for_status.called)

    @patch("src.slackNotification.slack_notification.send_to_slack")
    def test_lambda_handler_success(self, mock_send_to_stack):
        os.environ["SLACK_WEBHOOK"] = "webhook1,webhook2"
        event = {"status": "status", "taskname": "taskname"}
        slack_notification.lambda_handler(event, {})
        expected_message = {"Error": "tasknameError", "Cause": "status"}
        mock_send_to_stack.assert_called_once_with(["webhook1", "webhook2"],
                                                   expected_message)

    @patch("src.slackNotification.slack_notification.send_to_slack")
    def test_lambda_handler_Error(self, mock_send_to_stack):
        os.environ["SLACK_WEBHOOK"] = "webhook1,webhook2,webhook3"
        event = {"Error": "Error", "Cause": "Error-Cause"}
        slack_notification.lambda_handler(event, {})
        expected_message = {"Error": "Error", "Cause": "Error-Cause"}
        mock_send_to_stack.assert_called_once_with(
            ["webhook1", "webhook2", "webhook3"], expected_message)
