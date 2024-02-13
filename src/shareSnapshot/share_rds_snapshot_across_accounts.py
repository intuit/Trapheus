import os
import boto3
import constants
import custom_exceptions

def lambda_share_rds_snapshot_cross_account(event, context):
    region = os.environ['Region']
    ssm = boto3.client('ssm', region)
    result = {}
    try:
        response = ssm.start_automation_execution(
            DocumentName=constants.SNAPSHOT_SHARE_AUTOMATION,
            Parameters={
                'AccountIds': [
                    event['targetAccountIds']
                ],
                'Database': [
                    event['identifier']
                ],
                'SnapshotName': [
                    event['identifier'] + constants.SNAPSHOT_POSTFIX
                ],
                'AutomationAssumeRole': [
                     os.environ['SHARE_SNAPSHOT_TASK_ROLE']
                ]

            },
            Mode='Auto'
        )
        result['taskname'] = constants.SHARE_SNAPSHOT
        result['identifier'] = event['identifier']
        result['automation_execution_id'] = response.get("AutomationExecutionId")
        return result
    except Exception as error:
        raise custom_exceptions.SSMShareSnapshotException(error)