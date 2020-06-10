import os
import boto3
import constants
import custom_exceptions
import utility as util

def lambda_restore_dbcluster(event, context):
    """Handles restore of a db cluster from its snapshot"""
    region = os.environ['Region']
    result = {}
    rds = boto3.client('rds', region)
    old_cluster_id = event['identifier']
    response = util.get_modified_identifier(event['identifier'])
    cluster_id = response["instance_id"]
    cluster_snapshot_id = response["snapshot_id"]
    try:
        describe_db_response = rds.describe_db_clusters(
            DBClusterIdentifier = old_cluster_id
        )
        vpc_security_groups = describe_db_response['DBClusters'][0]['VpcSecurityGroups']
        engine = describe_db_response['DBClusters'][0]['Engine']
        engine_version = describe_db_response['DBClusters'][0]['EngineVersion']
        vpc_security_groups_ids = []
        for vpc_security_group in vpc_security_groups:
            vpc_security_groups_ids.append(vpc_security_group['VpcSecurityGroupId'])
        rds.restore_db_cluster_from_snapshot(
            DBClusterIdentifier = cluster_id,
            SnapshotIdentifier = cluster_snapshot_id,
            Engine = engine,
            EngineVersion = engine_version,
            DBSubnetGroupName = describe_db_response['DBClusters'][0]['DBSubnetGroup'],
            Port = describe_db_response['DBClusters'][0]['Port'],
            DatabaseName = describe_db_response['DBClusters'][0]['DatabaseName'],
            VpcSecurityGroupIds = vpc_security_groups_ids)
        for db_cluster_member in describe_db_response['DBClusters'][0]['DBClusterMembers']:
            desc_db_response = rds.describe_db_instances(
                DBInstanceIdentifier = db_cluster_member['DBInstanceIdentifier']
            )
            dbinstance_identifier = util.get_modified_identifier(db_cluster_member['DBInstanceIdentifier'])["instance_id"]
            rds.create_db_instance(
                DBInstanceIdentifier = dbinstance_identifier,
                DBInstanceClass = desc_db_response['DBInstances'][0]['DBInstanceClass'],
                Engine = engine,
                DBClusterIdentifier = cluster_id)
        
        result['taskname'] = constants.CLUSTER_RESTORE
        result['identifier'] = cluster_id
        return result
    except Exception as error:
        error_message = util.get_error_message(cluster_id, error)
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(error_message)
        else:
            raise custom_exceptions.ClusterRestoreException(error_message)
