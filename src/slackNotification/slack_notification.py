import os
import constants
import json
from botocore.vendored import requests

"""
Lambda to send a failure alert to a configured webhook on slack
"""
def lambda_handler(event, context):
    """Handles slack alerts for a configured webhook"""
    slack_webhooks = os.environ['SLACK_WEBHOOK'].split(',')
    message = {}

    message[constants.DB_ID] = event['identifier']
    message[constants.SNAPSHOT_ID] = event['identifier'] + constants.SNAPSHOT_POSTFIX

    if 'status' in event:
        message[constants.ERROR] = event[constants.TASK_NAME] + 'Error'
        message[constants.CAUSE] = event['status']
    elif 'Error' in event:
        message[constants.FAILED_STEP] = event[constants.TASK_NAME]
        message[constants.CAUSE] = event['Error']
    send_to_slack(slack_webhooks, message)


def send_to_slack(slack_webhooks, message):
    """Sends message to the configure slack webhook"""
    if not slack_webhooks:
        print('No webhooks provided. Not sending a message...')
        return
    for webhook in slack_webhooks:
        data = {"text": json.dumps(message)}
        response = requests.post(webhook, json=data)
        response.raise_for_status()
