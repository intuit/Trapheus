import os
import constants
import json
from botocore.vendored import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
Lambda to send a failure alert to a configured webhook on slack
"""
def lambda_handler(event, context):
    """Handles slack alerts for a configured webhook"""
    logger.info('## starting function execution ...')
    slack_webhooks = os.environ['SLACK_WEBHOOK'].split(',')
    message = {}
    if 'status' in event:
        message[constants.ERROR] = event['taskname'] + 'Error'
        message[constants.CAUSE] = event['status']
    elif 'Error' in event:
        message[constants.ERROR] = event['Error']
        message[constants.CAUSE] = event['Cause']
    logger.info('## MESSAGE RESULT')
    logger.info(message)
    send_to_slack(slack_webhooks, message)
    logger.info('## ending function execution')


def send_to_slack(slack_webhooks, message):
    """Sends message to the configure slack webhook"""
    logger.info('## starting send_to_slack() function execution ...')
    if not slack_webhooks:
        print('No webhooks provided. Not sending a message...')
        logger.info('## ending send_to_slack() function execution')
        return
    for webhook in slack_webhooks:
        data = {"text": json.dumps(message)}
        response = requests.post(webhook, json=data)
        logger.info('## RESPONSE RESULT')
        logger.info(response)
        response.raise_for_status()
