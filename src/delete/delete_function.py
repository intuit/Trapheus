import os
import boto3
import constants
import custom_exceptions
import utility as util

def lambda_delete_dbinstance(event, context):
    """Handles deletion of a RDS db instance"""
    region = os.environ['Region']
    rds = boto3.client('rds', region)
    result = {}
    instance_id = event['identifier'] + constants.TEMP_POSTFIX
    snapshot_id = util.get_snapshot_id(event)
    try:
        rds.delete_db_instance(
            DBInstanceIdentifier = instance_id,
            SkipFinalSnapshot = True
        )
        result['taskname'] = constants.DELETE
        result['identifier'] = instance_id
        result['snapshot_id'] = snapshot_id
        return result
    except Exception as error:
        error_message = util.get_error_message(instance_id, error)
        if constants.RATE_EXCEEDED in str(error):
            raise custom_exceptions.RateExceededException(error_message)
        else:
            raise custom_exceptions.DeletionException(error_message)
