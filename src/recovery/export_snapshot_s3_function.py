import os

import boto3
from retrying import retry

import constants
import utility as util


def lambda_export_rds_snapshot_to_s3(event, context):
    """export RDS snapshot to S3 bucket"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    export_id = event['identifier'] + constants.EXPORT_TASK_POSTFIX
    snapshot_id = event['identifier'] + constants.SNAPSHOT_POSTFIX
    snapshot_arn = check_db_snapshot_is_ready(snapshot_id)
    try:
        response = rds.start_export_task(
            ExportTaskIdentifier=export_id,
            SourceArn=snapshot_arn,
            S3BucketName=constants.RDS_SNAPSHOTS_BUCKET_NAME,
            IamRoleArn=os.environ['SNAPSHOT_EXPORT_TASK_ROLE'],
            KmsKeyId=os.environ['SNAPSHOT_EXPORT_TASK_KEY'],
        )
        result['taskname'] = constants.EXPORT_SNAPSHOT
        result['identifier'] = response['SourceArn']
        return result
    except Exception as error:
        raise Exception()


@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
def check_db_snapshot_is_ready(snapshot_name):
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    snapshots_response = rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot_name)
    assert snapshots_response['ResponseMetadata'][
               'HTTPStatusCode'] == 200, f"Error fetching snapshots: {snapshots_response}"
    snapshots = snapshots_response['DBSnapshots']
    assert len(snapshots) == 1, f"More than one snapshot matches name {snapshot_name}"
    snap = snapshots[0]
    snap_arn = snap['DBSnapshotArn']
    snap_status = snapshots[0]['Status']
    if snap_status == 'available':
        return snap_arn
    else:
        raise Exception(f"Snapshot is not ready yet (status is {snap_status})")
