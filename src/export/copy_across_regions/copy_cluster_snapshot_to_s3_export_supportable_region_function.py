import os
import boto3
import constants
import utility as util


def lambda_copy_cluster_snapshot_to_s3_export_supportable_region(event, context):
    """start export task of RDS snapshot to S3 bucket"""
    region = os.environ['Region']
    instance_id = event['identifier']
    snapshot_id = instance_id + constants.SNAPSHOT_POSTFIX
    snapshot_arn = util.get_instance_snapshot_arn(snapshot_id, region)
    export_snapshot_supported_region = os.environ['ExportSnapshotSupportedRegion']
    util.eval_export_exception(export_snapshot_supported_region)
    export_snapshot_supported_region_rds = boto3.client('rds', export_snapshot_supported_region)
    export_snapshot_supported_region_kms_key_id = os.environ['SNAPSHOT_COPY_EXPORT_TASK_KEY']
    result = {}

    try:
        db_snapshot_copy_response = copy_db_cluster_snapshot(export_snapshot_supported_region_kms_key_id,
                                                     export_snapshot_supported_region_rds, region, snapshot_arn,
                                                     snapshot_id)
        result['taskname'] = constants.COPY_SNAPSHOT
        result['identifier'] = instance_id
        result['status'] = db_snapshot_copy_response['DBClusterSnapshot']['Status']
        result['task'] = ''
        return result
    except Exception as error:
        raise Exception(error)


def copy_db_cluster_snapshot(export_snapshot_supported_region_kms_key_id, export_snapshot_supported_region_rds, region,
                     snapshot_arn, snapshot_id):
    return export_snapshot_supported_region_rds.copy_db_cluster_snapshot(
        SourceDBSnapshotIdentifier=snapshot_arn,
        TargetDBSnapshotIdentifier=snapshot_id,
        KmsKeyId=export_snapshot_supported_region_kms_key_id,
        CopyTags=True,
        SourceRegion=region
    )


