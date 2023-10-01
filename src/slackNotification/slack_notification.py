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
    if 'status' in event:
        message[constants.ERROR] = event['taskname'] + 'Error'
        message[constants.CAUSE] = event['status']
    elif 'Error' in event:
        message['database id'] = event['databaseid']
        message['snapshot id'] = event['snapshotid']
        message['failed step'] = event['taskname']
        message['cause of failure'] = event['Error']
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
