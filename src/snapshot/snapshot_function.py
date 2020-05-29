import os
import boto3
import constants
import utility as util

def lambda_create_dbinstance_snapshot(event, context):
    """create snapshot of db instance"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    instance_id = event['identifier']
    snapshot_id = event['identifier'] + constants.SNAPSHOT_POSTFIX
    try:
        rds.create_db_snapshot(
            DBSnapshotIdentifier = snapshot_id,
            DBInstanceIdentifier = instance_id
        )
        result['taskname'] = constants.SNAPSHOT
        result['identifier'] = instance_id
        return result
    except Exception as error:
        util.eval_snapshot_exception(error, instance_id, rds)
