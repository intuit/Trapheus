import os
import boto3
import constants
import custom_exceptions
import utility as util

def lambda_restore_rds_cluster_target_account(event, context):
    region = os.environ['Region']
    ssm = boto3.client('ssm', region)
    rds = boto3.client('rds', region)
    try:
        describe_cluster_response = rds.describe_db_clusters(
            DBClusterIdentifier=event['identifier']
        )
        db_cluster_data = describe_cluster_response['DBClusters'][0]
        engine = db_cluster_data['Engine']
        engine_version = db_cluster_data['EngineVersion']

        db_cluster_members = [db_cluster_member['DBInstanceIdentifier'] for db_cluster_member in
                              db_cluster_data['DBClusterMembers']]

        db_cluster_instance_class = [desc_db_response['DBInstances'][0]['DBInstanceClass'] for desc_db_response in [
            rds.describe_db_instances(DBInstanceIdentifier=db_cluster_member['DBInstanceIdentifier']) for
            db_cluster_member in db_cluster_data['DBClusterMembers']]]

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
                    db_cluster_data['Port']
                ],
                'DatabaseName': [
                    db_cluster_data['DatabaseName']
                ],
                'DBMemberInstanceList': db_cluster_members,
                'DBMemberInstanceClassList': db_cluster_instance_class,
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

        result = {
            'identifier': event['identifier'],
            'automation_execution_id': response.get("AutomationExecutionId")
        }
        return result
    except Exception as error:
        error_message = util.get_error_message(event['identifier'], error)
        raise custom_exceptions.ClusterRestoreException(error_message)