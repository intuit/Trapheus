import os
import time

import boto3

import constants
import utility as util

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_export_rds_snapshot_to_s3(event, context):
    """start export task of RDS snapshot to S3 bucket"""
    logger.info('## starting function execution ...')
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    instance_id = event['identifier']
    epoch = int(time.time())
    export_id = instance_id + "-" + str(epoch)
    snapshot_id = instance_id + constants.SNAPSHOT_POSTFIX
    snapshot_arn = get_instance_snapshot_arn(snapshot_id)
    account_id = util.get_aws_account_id()
    bucket_name = constants.RDS_SNAPSHOTS_BUCKET_NAME_PREFIX + account_id
    try:
        response = rds.start_export_task(
            ExportTaskIdentifier=export_id,
            SourceArn=snapshot_arn,
            S3BucketName=bucket_name,
            IamRoleArn=os.environ['SNAPSHOT_EXPORT_TASK_ROLE'],
            KmsKeyId=os.environ['SNAPSHOT_EXPORT_TASK_KEY'],
        )
        result['taskname'] = constants.EXPORT_SNAPSHOT
        result['identifier'] = instance_id
        result['status'] = response['Status']
        logger.info('## FUNCTION RESULT')
        logger.info(result)
        logger.info('## ending function execution')
        return result
    except Exception as error:
        raise Exception(error)


def get_instance_snapshot_arn(snapshot_name):
    """returns instance snapshot arn if in available state"""
    logger.info('## starting get_instance_snapshot_arn() function execution ...')
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    snapshots_response = rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot_name)
    logger.info('## SNAPSHOTS_RESPONSE')
    logger.info(snapshots_response)
    assert snapshots_response['ResponseMetadata'][
               'HTTPStatusCode'] == 200, f"Error fetching DB snapshots: {snapshots_response}"
    snapshots = snapshots_response['DBSnapshots']
    assert len(snapshots) == 1, f"No snapshot matches name {snapshot_name}"
    snap = snapshots[0]
    snap_status = snap.get('Status')
    if snap_status == 'available':
        logger.info('## FUNCTION RESULT')
        logger.info(snap['DBSnapshotArn'])
        logger.info('## ending get_instance_snapshot_arn() function execution')
        return snap['DBSnapshotArn']
    else:
        raise Exception(f"Snapshot is not available yet, status is {snap_status}")
