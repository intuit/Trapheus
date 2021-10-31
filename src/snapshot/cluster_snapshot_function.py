import os
import boto3
import constants
import utility as util

def lambda_create_cluster_snapshot(event, context):
    """create snapshot of db cluster"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    cluster_id = event['identifier']
    snapshot_id = event['identifier'] + constants.SNAPSHOT_POSTFIX
    try:
        rds.create_db_cluster_snapshot(
            DBClusterSnapshotIdentifier = snapshot_id,
            DBClusterIdentifier = cluster_id
        )
        if event['task'] == "create_snapshot_only":
            result['taskname'] = constants.SNAPSHOT_ONLY
        else:
            result['taskname'] = constants.SNAPSHOT
        result['identifier'] = cluster_id
        return result
    except Exception as error:
        util.eval_snapshot_exception(error, cluster_id, rds)
