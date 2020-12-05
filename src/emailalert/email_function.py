import os
import constants
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Handles email alerts for any failure scenario in db instance or cluster state machine"""
    SENDER = os.environ['SenderEmail']
    RECIPIENTS = os.environ['RecipientEmail'].split(',')
    AWS_REGION = os.environ['Region']
    SUBJECT = "Failure alert for RDS Restore Pipeline"
    result = {}
    if 'status' in event:
        result[constants.ERROR] = event['taskname'] + 'Error'
        result[constants.CAUSE] = event['status']
    elif 'Error' in event:
        result[constants.ERROR] = event['Error']
        result[constants.CAUSE] = event['Cause']
    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1>Failure alert for RDS Restore Pipeline</h1>
    <p>""" + result['Error'] + """ : """ + result['Cause'] + """</p>
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

    logger.info("function lambda_handler execution result: {}".format(result))
    return result
