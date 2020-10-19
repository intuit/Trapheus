import os
import constants
import utility


def lambda_check_region_support_cluster_snapshot_export_to_s3(event, context):
    """check whether the region supports snapshot export to s3"""
    region = os.environ['Region']
    instance_id = event['identifier']
    result = {'identifier': instance_id,
              'task': event['task']}

    if utility.supports_snapshot_export_region(region):
        result['taskname'] = constants.EXPORT_SNAPSHOT_SUPPORT
    elif is_cluster_snapshot_available(instance_id, os.environ['ExportSnapshotSupportedRegion']):
        result['taskname'] = constants.EXPORT_SNAPSHOT_TO_S3_IN_REGION_THAT_SUPPORTS_SNAPSHOT_EXPORT_TO_S3
    else:
        result['taskname'] = constants.COPY_SNAPSHOT

    return result


def is_cluster_snapshot_available(instance_id, region):
    """checks whether the region contains the cluster snapshot to be exported to s3"""
    snapshot_id = instance_id + constants.SNAPSHOT_POSTFIX
    try:
        return "" != utility.get_cluster_snapshot_arn(snapshot_id, region)
    except Exception as error:
        if constants.DB_SNAPSHOT_NOT_FOUND_FAULT in str(error):
            return False
        return True
