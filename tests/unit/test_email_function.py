import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/emailalert')))
import mock_import
import email_function

class TestResourceProvider(unittest.TestCase):
    def test_email_success1(self):
        os.environ["Region"] = "us-west-2"
        os.environ["RecipientEmail"] = "abc@example.com"
        os.environ["SenderEmail"] = "xyz@example.com"
        factory_patch = patch('email_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.send_email.return_value = mock_response
        mock_response.send_email.return_value = {"MessageId": "Email sent successfully"}
        event = {"Error": "RestoreError","Cause": "DBInstanceIdentifier:database-1 ThrottlingError: Rate exceeded"}
        data = email_function.lambda_handler(event, {})
        self.assertEqual(data.get("Error"), "RestoreError")
        self.assertEqual(data.get("Cause"), "DBInstanceIdentifier:database-1 ThrottlingError: Rate exceeded")
        self.assertEqual(data.get("message"), "Email sent successfully")

    def test_email_success2(self):
        os.environ["Region"] = "us-west-2"
        os.environ["RecipientEmail"] = "abc@example.com"
        os.environ["SenderEmail"] = "xyz@example.com"
        factory_patch = patch('email_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.send_email.return_value = mock_response
        mock_response.send_email.return_value = {"MessageId": "Email sent successfully"}
        event = {"taskname": "Restore","status": "inaccessible-encryption-credentials"}
        data = email_function.lambda_handler(event, {})
        self.assertEqual(data.get("Error"), "RestoreError")
        self.assertEqual(data.get("Cause"), "inaccessible-encryption-credentials")
        self.assertEqual(data.get("message"), "Email sent successfully")
    
    def test_email_failure(self):
        os.environ["Region"] = "us-west-2"
        os.environ["RecipientEmail"] = "abc@example.com"
        os.environ["SenderEmail"] = "xyz@example.com"
        factory_patch = patch('email_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("Timeout Exception")
        event = {"Error": "RestoreError","Cause": "DBInstanceIdentifier:database-1 ThrottlingError: Rate exceeded"}
        try:
            email_function.lambda_handler(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "Timeout Exception")