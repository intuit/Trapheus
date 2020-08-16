import os

import boto3

import constants


def lambda_export_rds_snapshot_to_s3(event, context):
    """start export task of RDS snapshot to S3 bucket"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    instance_id = event['identifier']
    export_id = instance_id + constants.EXPORT_TASK_POSTFIX
    snapshot_id = instance_id + constants.SNAPSHOT_POSTFIX
    snapshot_arn = get_snapshot_arn(snapshot_id)
    account_id = __get_aws_account_id()
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
        result['snapshot_arn'] = response['SourceArn']
        result['status'] = response['Status']
        return result
    except Exception as error:
        raise Exception(error)


def get_snapshot_arn(snapshot_name):
    """returns snapshort arn if in available state"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    snapshots_response = rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot_name)
    assert snapshots_response['ResponseMetadata'][
               'HTTPStatusCode'] == 200, f"Error fetching snapshots: {snapshots_response}"
    snapshots = snapshots_response['DBSnapshots']
    assert len(snapshots) == 1, f"More than one snapshot matches name {snapshot_name}"
    snap = snapshots[0]
    snap_status = snap.get('Status')
    if snap_status == 'available':
        snap_arn = snap.get('DBSnapshotArn')
        return snap_arn
    else:
        raise Exception(f"Snapshot is not available yet, status is {snap_status}")


def __get_aws_account_id():
    return boto3.client('sts').get_caller_identity().get('Account')
