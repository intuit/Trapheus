import os
import boto3
import constants
import custom_exceptions
import utility as util

def lambda_restore_dbinstance(event, context):
    """Handles restore of a db instance from its snapshot"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    response = util.get_modified_response(event)
    try:
        describe_db_response = rds.describe_db_instances(
            DBInstanceIdentifier = event['identifier']
        )
        vpc_security_groups = describe_db_response['DBInstances'][0]['VpcSecurityGroups']
        vpc_security_group_ids = []
        for vpc_security_group in vpc_security_groups:
            vpc_security_group_ids.append(vpc_security_group['VpcSecurityGroupId'])
        rds.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier = response["instance_id"],
            DBSnapshotIdentifier = response["snapshot_id"],
            DBSubnetGroupName = describe_db_response['DBInstances'][0]['DBSubnetGroup']['DBSubnetGroupName'],
            VpcSecurityGroupIds = vpc_security_group_ids
        )
        result['taskname'] = constants.DB_RESTORE
        result['identifier'] = response["instance_id"]
        return result
    except Exception as error:
        error_message = util.get_error_message(response["instance_id"], error)
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(error_message)
        else:
            raise custom_exceptions.InstanceRestoreException(error_message)
