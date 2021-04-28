import os
import boto3

def lambda_create_event_subscription(event, context):
     """Handles creation of unencrypted event notification subscription for a database to an SNS topic"""
     sourceType = 'db-instance' if event['isCluster'] == False else 'db-cluster'
     region = os.environ['Region']
     rds = boto3.client('rds', region)
     response = rds.create_event_subscription(
                    SubscriptionName='trapheus-event-subscription',
                    SnsTopicArn=os.environ['SNS_TOPIC_ARN'],
                    SourceType=sourceType,
                    SourceIds=[event['identifier']],
                    Enabled=True
                )