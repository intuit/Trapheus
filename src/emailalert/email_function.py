import os
import constants
import boto3

def lambda_handler(event, context):
    """Handles email alerts for any failure scenario in db instance or cluster state machine"""
    SENDER = os.environ['SenderEmail']
    RECIPIENTS = os.environ['RecipientEmail'].split(',')
    AWS_REGION = os.environ['Region']
    SUBJECT = "Failure alert for RDS Restore Pipeline"
    result = {}
    if 'status' in event:
        result['failed step'] = event['taskname']
        result[constants.CAUSE] = event['status']
    elif 'Error' in event:
        result['database id'] = event['Identifier']
        result['snapshot id'] = event['Identifier'] + constants.SNAPSHOT_POSTFIX
        result['failed step'] = event['taskname']
        result[constants.CAUSE] = event['Cause']
    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1>Failure alert for RDS Restore Pipeline</h1>
    <p>database id:""" + result['database id'] """</p>
    <p>snapshot id:""" + result['snapshot id'] """</p>
    <p>failed step:""" + result['taskname'] """</p>
    <p>cause of failure:""" + result[constants.CAUSE] """</p>
    </body>
    </html>"""

    CHARSET = "UTF-8"
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': RECIPIENTS,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
    # Display an error if something goes wrong.
    except Exception as e:
        raise Exception(e)
    else:
        result['message'] = response['MessageId']

    return result
