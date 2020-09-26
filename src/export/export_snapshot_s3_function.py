import os
import time

import boto3

import constants
import utility as util


def lambda_export_rds_snapshot_to_s3(event, context):
    """start export task of RDS snapshot to S3 bucket"""
    if event['taskname'] == constants.EXPORT_FROM_REGION_THAT_SUPPORTS_SNAPSHOT_EXPORT_TO_S3:
        region = os.environ['ExportSnapshotSupportedRegion']
        kms_key_id = os.environ['SNAPSHOT_COPY_EXPORT_TASK_KEY']
    else:
        region = os.environ['Region']
        kms_key_id = os.environ['SNAPSHOT_EXPORT_TASK_KEY']
    rds = boto3.client('rds', region)
    result = {}
    instance_id = event['identifier']
    epoch = int(time.time())
    export_id = instance_id + "-" + str(epoch)
    snapshot_id = instance_id + constants.SNAPSHOT_POSTFIX
    snapshot_arn = util.get_instance_snapshot_arn(snapshot_id, region)
    account_id = util.get_aws_account_id()
    bucket_name = constants.RDS_SNAPSHOTS_BUCKET_NAME_PREFIX + account_id + '-' + region
    try:
        response = rds.start_export_task(
            ExportTaskIdentifier=export_id,
            SourceArn=snapshot_arn,
            S3BucketName=bucket_name,
            IamRoleArn=os.environ['SNAPSHOT_EXPORT_TASK_ROLE'],
            KmsKeyId=kms_key_id,
        )
        result['taskname'] = constants.EXPORT_SNAPSHOT
        result['identifier'] = instance_id
        result['status'] = response['Status']
        return result
    except Exception as error:
        raise Exception(error)

