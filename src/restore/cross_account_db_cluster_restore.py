import os
import boto3
import constants
import custom_exceptions
import utility as util

def lambda_restore_rds_cluster_target_account(event, context):
    region = os.environ['Region']
    ssm = boto3.client('ssm', region)
    rds = boto3.client('rds', region)
    result = {}
    try:
        describe_cluster_response = rds.describe_db_clusters(
            DBClusterIdentifier=event['identifier']
        )
        engine = describe_cluster_response['DBClusters'][0]['Engine']
        engine_version = describe_cluster_response['DBClusters'][0]['EngineVersion']
        db_cluster_members = []
        db_cluster_instance_class = []
        for db_cluster_member in describe_cluster_response['DBClusters'][0]['DBClusterMembers']:
            desc_db_response = rds.describe_db_instances(
                DBInstanceIdentifier=db_cluster_member['DBInstanceIdentifier']
            )
            db_cluster_members.append(db_cluster_member['DBInstanceIdentifier'])
            db_cluster_instance_class.append(desc_db_response['DBInstances'][0]['DBInstanceClass'])

        response = ssm.start_automation_execution(
            DocumentName='Trapheus-RestoreDatabaseClusterFromSharedSnapshot',
            Parameters={
                'NewDatabaseIdentifier': [
                    event['identifier']
                ],
                'NewSnapshotIdentifier': [
                    event['identifier'] + constants.SNAPSHOT_POSTFIX
                ],
                'DatabaseEngine': [
                    engine
                ],
                'DatabaseEngineVersion': [
                    engine_version
                ],
                'DatabasePort': [
                    describe_cluster_response['DBClusters'][0]['Port']
                ],
                'DatabaseName': [
                    describe_cluster_response['DBClusters'][0]['DatabaseName']
                ],
                'DBMemberInstanceList': [
                    db_cluster_members
                ],
                'DBMemberInstanceClassList': [
                    db_cluster_instance_class
                ],
                'AutomationAssumeRole': [
                    event['AutomationAssumeRole']
                ]

            },
            Mode='Auto',
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
        result['automation_execution_id'] = response.get("AutomationExecutionId")
        return result
    except Exception as error:
        error_message = util.get_error_message(event['identifier'], error)
        raise custom_exceptions.ClusterRestoreException(error_message)