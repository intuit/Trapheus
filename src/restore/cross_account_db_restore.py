import os
import boto3
import constants
import custom_exceptions

def lambda_restore_rds_target_account(event, context):
    region = os.environ['Region']
    ssm = boto3.client('ssm', region)
    result = {}
    try:
        response = ssm.start_automation_execution(
            DocumentName='Trapheus-RestoreDatabaseFromSharedSnapshot',
            Parameters={
                'SharedSnapshotARN': [
                    event['SharedSnapshotARN']
                ],
                'sourceDBInstanceIdentifier': [
                    event['identifier']
                ],
                'NewDatabaseIdentifier': [
                    event['identifier']
                ],
                'NewSnapshotIdentifier': [
                    event['identifier'] + constants.SNAPSHOT_POSTFIX
                ],
                'TargetVPCId': [
                    event['vpcId']
                ],
                'AutomationAssumeRole': [
                    event['AutomationAssumeRole']
                ]

            },
            Mode='Interactive',
            TargetLocations=[
                {
                    'Accounts': [
                        event['targetAccountIds']
                    ],
                    'Regions': [
                        event['targetRegions']
                    ]
                }
            ]
        )
        result['identifier'] = event['identifier']
        result['restoreRDSAutomationExecutionId'] = response.get("AutomationExecutionId")
        return result
    except Exception as error:
        raise custom_exceptions.InstanceRestoreException(error)